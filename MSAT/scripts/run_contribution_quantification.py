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
    "node_type",
    "node_id",
    "path_index",
    "path_text",
    "path_features",
    "masked_score",
    "score_drop",
]


def _path_texts(row: dict) -> list[str]:
    texts: list[str] = []
    for item in row.get("paths", []):
        if isinstance(item, dict):
            text = item.get("path") or item.get("template") or ""
        else:
            text = str(item)
        if text:
            texts.append(text)
    return texts


def select_mechanistic_cases(payload: dict, max_cases: int = 2, max_features: int = 6) -> list[dict]:
    cases: list[dict] = []
    for row in payload.get("rows", []):
        paths = _path_texts(row)
        node_refs = extract_node_refs_from_paths(paths)
        if not node_refs:
            continue
        cases.append({**row, "path_texts": paths, "node_refs": node_refs[:max_features]})
        if len(cases) >= max_cases:
            break
    return cases


def build_case_contribution_payload(
    case: dict,
    original_score: float,
    score_masked,
    score_masked_path,
) -> dict:
    path_texts = case.get("path_texts") or _path_texts(case)
    mechanism_subgraph = build_key_mechanism_subgraph(path_texts)
    parsed_paths = [path for path in mechanism_subgraph["paths"] if path["feature_refs"]]
    node_contributions = score_node_perturbations(
        original_score=original_score,
        node_refs=case["node_refs"],
        score_masked=score_masked,
    )
    path_contributions = score_path_perturbations(
        original_score=original_score,
        paths=parsed_paths,
        score_masked_path=score_masked_path,
    )
    return {
        "herb_id": int(case["herb_id"]),
        "adr_id": int(case["adr_id"]),
        "source": case.get("source", "unknown"),
        "original_score": float(original_score),
        "path_count": len(path_texts),
        "feature_count": len(case["node_refs"]),
        "paths": path_texts,
        "mechanism_subgraph": mechanism_subgraph,
        "node_contributions": node_contributions,
        "path_contributions": path_contributions,
        "contributions": node_contributions,
    }


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


def quantify_cases_with_predictor(cases: list[dict], predictor: MSATPredictor) -> list[dict]:
    outputs: list[dict] = []
    for case in cases:
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

        outputs.append(
            build_case_contribution_payload(
                case,
                original_score=original_score,
                score_masked=score_masked,
                score_masked_path=score_masked_path,
            )
        )
    return outputs


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
                    **row,
                }
            )
    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
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
                "",
                "### Node Contributions",
                "",
                "| Feature | Type | Masked score | Score drop |",
                "| --- | --- | ---: | ---: |",
            ]
        )
        for row in case["node_contributions"]:
            lines.append(
                f"| `{row['feature']}` | `{row['node_type']}` | {row['masked_score']:.6f} | {row['score_drop']:.6f} |"
            )
        lines.extend(
            [
                "",
                "### Path Contributions",
                "",
                "| Path | Features | Masked score | Score drop |",
                "| --- | --- | ---: | ---: |",
            ]
        )
        for row in case["path_contributions"]:
            features = ", ".join(f"`{feature}`" for feature in row["features"])
            lines.append(
                f"| `{row['feature']}` | {features} | {row['masked_score']:.6f} | {row['score_drop']:.6f} |"
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
    parser.add_argument("--max-features", type=int, default=6)
    parser.add_argument("--device", default=None)
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()

    source = Path(args.input)
    raw = json.loads(source.read_text())
    cases = select_mechanistic_cases(raw, max_cases=args.max_cases, max_features=args.max_features)
    predictor = MSATPredictor(checkpoint=args.checkpoint, device=args.device)
    quantified = quantify_cases_with_predictor(cases, predictor)
    payload = {
        "experiment": "contribution_quantification",
        "created_at": datetime.now().isoformat(),
        "input": str(source),
        "checkpoint_path": str(predictor.checkpoint),
        "checkpoint_context": (
            "Local predictor checkpoint sensitivity analysis. This is not final "
            "full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit "
            "PU predictor checkpoint is exported and used."
        ),
        "method": "zero node input features and re-score the same pair",
        "claim_boundary": "Perturbation score drops are local sensitivity signals, not causal effects.",
        "cases": quantified,
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
