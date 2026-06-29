from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.contribution_scoring import (  # noqa: E402
    build_key_mechanism_subgraph,
    enrich_feature_refs,
    extract_node_refs_from_paths,
    score_path_perturbations,
    score_node_perturbations,
    zero_x_dict_feature_refs,
    zero_x_dict_node_features,
)
from inference.predictor import MSATPredictor  # noqa: E402


CSV_FIELDS = [
    "case_index",
    "contribution_type",
    "source",
    "herb_id",
    "adr_id",
    "original_score",
    "feature",
    "display_name",
    "name_source",
    "node_type",
    "node_id",
    "path_index",
    "path_text",
    "path_features",
    "path_display_features",
    "masked_score",
    "score_drop",
]


def _path_texts(row: dict) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for key in ("explicit_mechanism_paths", "paths", "top_mechanism_paths", "mechanism_paths"):
        value = row.get(key, [])
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                text = item.get("path") or item.get("path_text") or item.get("template") or ""
            else:
                text = str(item)
            if text and text not in seen:
                seen.add(text)
                texts.append(text)
    return texts


def infer_checkpoint_context(
    checkpoint_path: str | Path | None,
    checkpoint_is_final_pu: bool = False,
) -> str:
    if checkpoint_is_final_pu:
        return (
            "Final full-positive hybrid PU-XMSAT checkpoint perturbation sensitivity. "
            "This remains local model sensitivity, not causal or external validation."
        )

    checkpoint_text = "" if checkpoint_path is None else str(checkpoint_path)
    lowered = checkpoint_text.lower()
    if "pu_xmsat" in lowered or "full_msat_pu" in lowered:
        return (
            "PU-XMSAT checkpoint perturbation sensitivity, but not final 10-fold PU-XMSAT "
            "attribution unless the checkpoint is explicitly exported and marked as final."
        )

    return (
        "Local predictor checkpoint sensitivity analysis. This is not final full-positive "
        "hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint "
        "is exported and used."
    )


def _select_node_refs(node_refs: list[dict], max_features: int | None) -> tuple[list[dict], bool]:
    if max_features is None or int(max_features) <= 0:
        return list(node_refs), False
    selected = node_refs[: int(max_features)]
    return selected, len(selected) < len(node_refs)


def select_mechanistic_cases(payload: dict, max_cases: int = 2, max_features: int = 0) -> list[dict]:
    cases: list[dict] = []
    for row in payload.get("rows", []):
        paths = _path_texts(row)
        node_refs = extract_node_refs_from_paths(paths)
        if not node_refs:
            continue
        selected_refs, truncated = _select_node_refs(node_refs, max_features)
        cases.append(
            {
                **row,
                "path_texts": paths,
                "node_refs": selected_refs,
                "available_node_ref_count": len(node_refs),
                "quantified_node_ref_count": len(selected_refs),
                "node_refs_truncated": truncated,
            }
        )
        if len(cases) >= max_cases:
            break
    return cases


def build_case_contribution_payload(
    case: dict,
    original_score: float,
    score_masked,
    score_masked_path,
    random_node_refs: list[dict] | None = None,
    random_path_controls: list[dict] | None = None,
    entity_names=None,
) -> dict:
    path_texts = case.get("path_texts") or _path_texts(case)
    mechanism_subgraph = build_key_mechanism_subgraph(path_texts, entity_names=entity_names)
    parsed_paths = [path for path in mechanism_subgraph["paths"] if path["feature_refs"]]
    node_refs = enrich_feature_refs(case["node_refs"], entity_names=entity_names)
    node_contributions = score_node_perturbations(
        original_score=original_score,
        node_refs=node_refs,
        score_masked=score_masked,
    )
    path_contributions = score_path_perturbations(
        original_score=original_score,
        paths=parsed_paths,
        score_masked_path=score_masked_path,
    )
    random_controls = {"component": [], "target": [], "pathway": []}
    if random_node_refs:
        random_rows = score_node_perturbations(
            original_score=original_score,
            node_refs=enrich_feature_refs(random_node_refs, entity_names=entity_names),
            score_masked=score_masked,
        )
        for row in random_rows:
            normalized = {**row, "control_type": "random_same_node_type"}
            if row.get("node_type") == "compound":
                random_controls["component"].append(normalized)
            elif row.get("node_type") == "target":
                random_controls["target"].append(normalized)
    if random_path_controls:
        enriched_random_paths = [
            {
                **path,
                "feature_refs": enrich_feature_refs(
                    path.get("feature_refs", []),
                    entity_names=entity_names,
                ),
            }
            for path in random_path_controls
        ]
        random_path_rows = score_path_perturbations(
            original_score=original_score,
            paths=enriched_random_paths,
            score_masked_path=score_masked_path,
        )
        random_controls["pathway"].extend(
            {**row, "control_type": "random_same_path_node_types"}
            for row in random_path_rows
        )
    return {
        "herb_id": int(case["herb_id"]),
        "adr_id": int(case["adr_id"]),
        "source": case.get("source", "unknown"),
        "original_score": float(original_score),
        "path_count": len(path_texts),
        "available_node_ref_count": int(case.get("available_node_ref_count", len(case["node_refs"]))),
        "quantified_node_ref_count": int(case.get("quantified_node_ref_count", len(case["node_refs"]))),
        "node_refs_truncated": bool(case.get("node_refs_truncated", False)),
        "feature_count": len(node_refs),
        "paths": path_texts,
        "mechanism_subgraph": mechanism_subgraph,
        "node_contributions": node_contributions,
        "path_contributions": path_contributions,
        "random_controls": random_controls,
        "contributions": node_contributions,
    }


def _sample_random_ref(
    x_dict: dict[str, torch.Tensor],
    node_type: str,
    excluded_ids: set[int],
    rng: np.random.RandomState,
) -> dict | None:
    node_count = int(x_dict[node_type].shape[0])
    available = [idx for idx in range(node_count) if idx not in excluded_ids]
    if not available:
        return None
    node_id = int(available[int(rng.randint(0, len(available)))])
    return {
        "feature": f"{node_type}:{node_id}",
        "node_type": node_type,
        "node_id": node_id,
        "label": f"{node_type.title()} #{node_id}",
        "display_name": f"{node_type.title()} #{node_id}",
        "name_source": "unmapped_graph_id",
    }


def sample_random_node_refs(
    node_refs: list[dict],
    x_dict: dict[str, torch.Tensor],
    seed: int,
    controls_per_type: int,
) -> list[dict]:
    if controls_per_type <= 0:
        return []
    rng = np.random.RandomState(int(seed))
    refs = []
    by_type: dict[str, set[int]] = {}
    for ref in node_refs:
        by_type.setdefault(ref["node_type"], set()).add(int(ref["node_id"]))
    for node_type, excluded_ids in sorted(by_type.items()):
        if node_type not in x_dict:
            continue
        for _ in range(int(controls_per_type)):
            sampled = _sample_random_ref(x_dict, node_type, excluded_ids, rng)
            if sampled:
                excluded_ids.add(int(sampled["node_id"]))
                refs.append(sampled)
    return refs


def sample_random_path_controls(
    parsed_paths: list[dict],
    x_dict: dict[str, torch.Tensor],
    seed: int,
    max_controls: int,
) -> list[dict]:
    if max_controls <= 0:
        return []
    rng = np.random.RandomState(int(seed))
    controls = []
    for index, path in enumerate(parsed_paths[: int(max_controls)], start=1):
        random_refs = []
        for ref in path.get("feature_refs", []):
            sampled = _sample_random_ref(
                x_dict,
                ref["node_type"],
                excluded_ids={int(ref["node_id"])},
                rng=rng,
            )
            if sampled:
                random_refs.append(sampled)
        if not random_refs:
            continue
        controls.append(
            {
                "path_index": index,
                "path_text": "random same-type path control",
                "features": [ref["feature"] for ref in random_refs],
                "feature_refs": random_refs,
            }
        )
    return controls


def _score_pair_with_x_dict(predictor: MSATPredictor, x_dict: dict[str, torch.Tensor], herb_id: int, adr_id: int) -> float:
    h = torch.as_tensor(np.array([herb_id]), dtype=torch.long, device=predictor.device)
    a = torch.as_tensor(np.array([adr_id]), dtype=torch.long, device=predictor.device)
    with torch.no_grad():
        out = predictor.model(
            x_dict,
            predictor._edge_index_dict,
            predictor._edge_attr_dict,
            h,
            a,
        )
    return float(torch.nan_to_num(out, nan=0.5).detach().cpu().numpy().reshape(-1)[0])


def quantify_cases_with_predictor(
    cases: list[dict],
    predictor: MSATPredictor,
    random_controls_per_type: int = 0,
    random_path_controls: int = 0,
    random_seed: int = 42,
) -> list[dict]:
    outputs: list[dict] = []
    for case_index, case in enumerate(cases):
        herb_id = int(case["herb_id"])
        adr_id = int(case["adr_id"])
        original_score = float(predictor.score_pairs(np.array([herb_id]), np.array([adr_id]))[0])

        def score_masked(ref: dict) -> float:
            masked_x = zero_x_dict_node_features(
                predictor._x_dict,
                ref["node_type"],
                int(ref["node_id"]),
            )
            return _score_pair_with_x_dict(predictor, masked_x, herb_id, adr_id)

        def score_masked_path(path: dict) -> float:
            masked_x = zero_x_dict_feature_refs(predictor._x_dict, path["feature_refs"])
            return _score_pair_with_x_dict(predictor, masked_x, herb_id, adr_id)

        path_texts = case.get("path_texts") or _path_texts(case)
        mechanism_subgraph = build_key_mechanism_subgraph(path_texts)
        parsed_paths = [path for path in mechanism_subgraph["paths"] if path["feature_refs"]]
        outputs.append(
            build_case_contribution_payload(
                case,
                original_score=original_score,
                score_masked=score_masked,
                score_masked_path=score_masked_path,
                random_node_refs=sample_random_node_refs(
                    case["node_refs"],
                    predictor._x_dict,
                    seed=int(random_seed) + case_index,
                    controls_per_type=int(random_controls_per_type),
                ),
                random_path_controls=sample_random_path_controls(
                    parsed_paths,
                    predictor._x_dict,
                    seed=int(random_seed) + case_index + 1000,
                    max_controls=int(random_path_controls),
                ),
                entity_names=getattr(predictor, "names", None),
            )
        )
    return outputs


def collect_random_controls(cases: list[dict]) -> dict[str, list[dict]]:
    grouped = {"component": [], "target": [], "pathway": []}
    for case in cases:
        controls = case.get("random_controls") or {}
        for group in grouped:
            grouped[group].extend(controls.get(group, []))
    return grouped


def write_outputs(payload: dict, output_json: Path, output_csv: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    rows: list[dict] = []
    for case_index, case in enumerate(payload["cases"], start=1):
        for row in case["node_contributions"]:
            rows.append(
                {
                    "case_index": case_index,
                    "contribution_type": "node",
                    "source": case["source"],
                    "herb_id": case["herb_id"],
                    "adr_id": case["adr_id"],
                    "original_score": case["original_score"],
                    **row,
                }
            )
        for row in case["path_contributions"]:
            rows.append(
                {
                    "case_index": case_index,
                    "contribution_type": "path",
                    "source": case["source"],
                    "herb_id": case["herb_id"],
                    "adr_id": case["adr_id"],
                    "original_score": case["original_score"],
                        "path_features": ";".join(row["features"]),
                        "path_display_features": ";".join(row.get("display_features", [])),
                        **row,
                    }
                )
    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in CSV_FIELDS} for row in rows])

    lines = [
        "# PU-XMSAT Contribution Quantification",
        "",
        "This report quantifies local contribution by zeroing input feature vectors for mechanism nodes or whole mechanism paths, then re-scoring the same CMM-ADR pair with the trained MSAT predictor.",
        "",
        f"- Cases quantified: {len(payload['cases'])}",
        f"- Generated at: {payload['created_at']}",
        f"- Checkpoint: `{payload.get('checkpoint_path', 'unknown')}`",
        f"- Checkpoint context: {payload.get('checkpoint_context', 'not specified')}",
        "",
        payload.get(
            "claim_boundary",
            "The score drop is a perturbation sensitivity signal, not a causal effect.",
        ),
        "Negative score drops mean the score increased after masking; they should be interpreted as suppressive or non-supportive sensitivity signals, not as confirmed protective biology.",
        "",
    ]
    for i, case in enumerate(payload["cases"], start=1):
        lines.extend(
            [
                f"## Case {i}: herb {case['herb_id']} -> ADR {case['adr_id']}",
                "",
                f"- Source: `{case['source']}`",
                f"- Original score: {case['original_score']:.6f}",
                f"- Key subgraph nodes: {len(case['mechanism_subgraph']['nodes'])}",
                f"- Key subgraph edges: {len(case['mechanism_subgraph']['edges'])}",
                f"- Quantified node refs: {case.get('quantified_node_ref_count', len(case['node_contributions']))}/{case.get('available_node_ref_count', len(case['node_contributions']))}",
                f"- Node refs truncated: {'yes' if case.get('node_refs_truncated') else 'no'}",
                "",
                "### Node Contributions",
                "",
                "| Feature | Display name | Name source | Type | Masked score | Score drop |",
                "| --- | --- | --- | --- | ---: | ---: |",
            ]
        )
        for row in case["node_contributions"]:
            lines.append(
                f"| `{row['feature']}` | {row.get('display_name', row['feature'])} | "
                f"`{row.get('name_source', '')}` | `{row['node_type']}` | "
                f"{row['masked_score']:.6f} | {row['score_drop']:.6f} |"
            )
        lines.extend(
            [
                "",
                "### Path Contributions",
                "",
                "| Path | Features | Display names | Masked score | Score drop |",
                "| --- | --- | --- | ---: | ---: |",
            ]
        )
        for row in case["path_contributions"]:
            features = ", ".join(f"`{feature}`" for feature in row["features"])
            display = ", ".join(row.get("display_features", []))
            lines.append(
                f"| `{row['feature']}` | {features} | {display} | "
                f"{row['masked_score']:.6f} | {row['score_drop']:.6f} |"
            )
        lines.append("")
    output_md.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantify mechanism-node perturbation contributions")
    parser.add_argument("--input", default="results/explanation_case_studies.json")
    parser.add_argument("--output-json", default="results/contribution_quantification.json")
    parser.add_argument("--output-csv", default="results/contribution_quantification.csv")
    parser.add_argument("--output-md", default="results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md")
    parser.add_argument("--max-cases", type=int, default=2)
    parser.add_argument(
        "--max-features",
        type=int,
        default=0,
        help="Maximum mechanism node refs to perturb per case; <=0 quantifies all parsed refs.",
    )
    parser.add_argument("--device", default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--checkpoint-is-final-pu", action="store_true")
    parser.add_argument("--random-controls-per-type", type=int, default=0)
    parser.add_argument("--random-path-controls", type=int, default=0)
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()

    source = Path(args.input)
    raw = json.loads(source.read_text())
    cases = select_mechanistic_cases(raw, max_cases=args.max_cases, max_features=args.max_features)
    predictor = MSATPredictor(checkpoint=args.checkpoint, device=args.device)
    quantified = quantify_cases_with_predictor(
        cases,
        predictor,
        random_controls_per_type=args.random_controls_per_type,
        random_path_controls=args.random_path_controls,
        random_seed=args.random_seed,
    )
    payload = {
        "experiment": "contribution_quantification",
        "created_at": datetime.now().isoformat(),
        "input": str(source),
        "checkpoint_path": str(predictor.checkpoint),
        "checkpoint_context": infer_checkpoint_context(
            predictor.checkpoint,
            checkpoint_is_final_pu=args.checkpoint_is_final_pu,
        ),
        "checkpoint_is_final_pu_xmsat": bool(args.checkpoint_is_final_pu),
        "method": "zero node input features and re-score the same pair",
        "claim_boundary": "Perturbation score drops are local sensitivity signals, not causal effects.",
        "cases": quantified,
        "random_controls": collect_random_controls(quantified),
    }
    write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_csv=Path(args.output_csv),
        output_md=Path(args.output_md),
    )
    print(
        f"Wrote contribution quantification for {len(quantified)} cases to "
        f"{args.output_json}, {args.output_csv}, and {args.output_md}"
    )


if __name__ == "__main__":
    main()
