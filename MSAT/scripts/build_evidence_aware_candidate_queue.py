from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_TOP_PREDICTIONS = Path("results/pu_xmsat_top_predictions_top5000.json")
DEFAULT_BATCH_INTERPRETABILITY = Path(
    "results/batch_mechanism_interpretability_top5000_random_controls.json"
)
DEFAULT_OUTPUT_JSON = Path("results/evidence_aware_mechanism_candidate_queue.json")
DEFAULT_OUTPUT_CSV = Path("results/evidence_aware_mechanism_candidate_queue.csv")
DEFAULT_OUTPUT_MD = Path("results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md")

CLAIM_BOUNDARY = (
    "This queue reranks explicit-path mechanism candidates for manual evidence review; "
    "it is not external validation, not compound/target name confirmation, and not a "
    "causal mechanism claim."
)

CSV_FIELDS = [
    "rank",
    "source_rank",
    "herb_id",
    "adr_id",
    "herb_latin",
    "latin",
    "chinese",
    "pinyin",
    "adr_pt",
    "prediction_score",
    "evidence_priority_score",
    "model_score_component",
    "rank_component",
    "path_component",
    "node_coverage_component",
    "prior_perturbation_component",
    "evidence_retrievability_score",
    "explicit_mechanism_path_count",
    "parseable_node_ref_count",
    "prior_perturbation_score_drop",
    "sensitivity_class",
    "pubmed_exact_query",
    "pubmed_genus_query",
    "openfda_query",
    "top_path_text",
    "review_action",
]

COMMON_ADR_TERMS = {
    "anaesthesia",
    "anesthesia",
    "constipation",
    "cough",
    "diarrhea",
    "diarrhoea",
    "dizziness",
    "dry cough",
    "fatigue",
    "fever",
    "haemorrhage",
    "hemorrhage",
    "jaundice",
    "liver injury",
    "nausea",
    "oedema",
    "edema",
    "pain",
    "proteinuria",
    "pyrexia",
    "rash",
    "sedation",
    "tinnitus",
    "vomiting",
    "wheezing",
}

LOW_RETRIEVABILITY_ADR_TERMS = {
    "essential thrombocythaemia",
    "neoplasm",
    "spina bifida",
    "suicide attempt",
    "sulphaemoglobinaemia",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    src = Path(path)
    if not src.exists():
        return {}
    return json.loads(src.read_text())


def _candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows") or payload.get("candidates") or payload.get("cases") or []
    return [row for row in rows if isinstance(row, dict)]


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(value)


def _paths(row: dict[str, Any]) -> list[str]:
    output: list[str] = []
    for key in ("explicit_mechanism_paths", "top_mechanism_paths", "paths"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            output.append(value.strip())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    text = item.get("path") or item.get("path_text") or item.get("template") or ""
                else:
                    text = str(item)
                if text.strip():
                    output.append(text.strip())
    return output


def _node_refs(paths: list[str]) -> set[str]:
    refs: set[str] = set()
    for path in paths:
        for kind, node_id in re.findall(r"\b(compound|target):(\d+)\b", path, flags=re.I):
            refs.add(f"{kind.lower()}:{node_id}")
        for kind, node_id in re.findall(r"\b(Compound|Target)\s+#(\d+)\b", path):
            refs.add(f"{kind.lower()}:{node_id}")
    return refs


def _has_explicit_path(row: dict[str, Any]) -> bool:
    return bool(_paths(row)) and bool(_node_refs(_paths(row)))


def _prediction_score(row: dict[str, Any]) -> float:
    for key in ("prediction_score", "score", "original_score"):
        if row.get(key) not in (None, ""):
            return float(row[key])
    return 0.0


def _pair_key(row: dict[str, Any]) -> tuple[int, int]:
    return _int(row.get("herb_id")), _int(row.get("adr_id"))


def _prior_perturbation_index(batch_payload: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    indexed: dict[tuple[int, int], dict[str, Any]] = {}
    for case in _candidate_rows(batch_payload):
        key = _pair_key(case)
        if key == (0, 0):
            continue
        indexed[key] = {
            "prior_perturbation_score_drop": max(
                0.0,
                _float(case.get("max_positive_score_drop")),
            ),
            "sensitivity_class": case.get("sensitivity_class", ""),
        }
    return indexed


def _latin_specificity_score(herb_latin: str) -> float:
    cleaned = re.sub(r"[\[\]();,]", " ", herb_latin or "")
    tokens = [token for token in cleaned.split() if token and not token.startswith("#")]
    if len(tokens) >= 2:
        return 0.35
    if tokens:
        return 0.15
    return 0.0


def _adr_retrievability_score(adr_pt: str) -> float:
    adr = (adr_pt or "").strip().lower()
    if not adr:
        return 0.0
    if adr in LOW_RETRIEVABILITY_ADR_TERMS:
        return 0.0
    if adr in COMMON_ADR_TERMS:
        return 0.45
    if any(term in adr for term in COMMON_ADR_TERMS):
        return 0.35
    word_count = len(adr.split())
    if word_count <= 2:
        return 0.25
    if word_count <= 4:
        return 0.15
    return 0.05


def _evidence_retrievability_score(herb_latin: str, adr_pt: str) -> float:
    return min(1.0, _latin_specificity_score(herb_latin) + _adr_retrievability_score(adr_pt))


def _query_strings(herb_latin: str, adr_pt: str) -> dict[str, str]:
    herb = (herb_latin or "").strip()
    adr = (adr_pt or "").strip()
    genus = herb.split()[0] if herb.split() else herb
    return {
        "pubmed_exact_query": f'"{herb}" AND "{adr}"' if herb and adr else "",
        "pubmed_genus_query": f'"{genus}" AND "{adr}"' if genus and adr else "",
        "openfda_query": f'patient.drug.medicinalproduct:"{herb}" AND patient.reaction.reactionmeddrapt:"{adr}"'
        if herb and adr
        else "",
    }


def _score_row(
    row: dict[str, Any],
    prior: dict[str, Any],
) -> dict[str, Any]:
    paths = _paths(row)
    refs = _node_refs(paths)
    source_rank = _int(row.get("rank"), 999999)
    prediction_score = _prediction_score(row)
    model_component = max(0.0, min(1.0, prediction_score))
    rank_component = 1.0 / (1.0 + math.log1p(max(1, source_rank)))
    path_count = _int(row.get("explicit_mechanism_path_count"), len(paths)) or len(paths)
    path_component = min(1.0, path_count / 5.0)
    node_component = min(1.0, len(refs) / 8.0)
    prior_drop = _float(prior.get("prior_perturbation_score_drop"))
    prior_component = min(1.0, prior_drop / 0.001)
    herb_latin = str(row.get("herb_latin") or row.get("herb_name") or "")
    herb_chinese = str(row.get("herb_chinese") or "")
    herb_pinyin = str(row.get("herb_pinyin") or "")
    adr_pt = str(row.get("adr_pt") or "")
    retrievability = _evidence_retrievability_score(herb_latin, adr_pt)
    priority_score = (
        0.30 * model_component
        + 0.10 * rank_component
        + 0.15 * path_component
        + 0.10 * node_component
        + 0.20 * prior_component
        + 0.15 * retrievability
    )
    queries = _query_strings(herb_latin, adr_pt)
    return {
        "source_rank": source_rank,
        "herb_id": _int(row.get("herb_id")),
        "adr_id": _int(row.get("adr_id")),
        "herb_latin": herb_latin,
        "latin": herb_latin,
        "chinese": herb_chinese,
        "pinyin": herb_pinyin,
        "adr_pt": adr_pt,
        "prediction_score": prediction_score,
        "evidence_priority_score": priority_score,
        "model_score_component": model_component,
        "rank_component": rank_component,
        "path_component": path_component,
        "node_coverage_component": node_component,
        "prior_perturbation_component": prior_component,
        "evidence_retrievability_score": retrievability,
        "explicit_mechanism_path_count": path_count,
        "parseable_node_ref_count": len(refs),
        "prior_perturbation_score_drop": prior_drop,
        "sensitivity_class": prior.get("sensitivity_class", ""),
        "pubmed_exact_query": queries["pubmed_exact_query"],
        "pubmed_genus_query": queries["pubmed_genus_query"],
        "openfda_query": queries["openfda_query"],
        "top_path_text": paths[0] if paths else "",
        "review_action": "manual_external_evidence_review",
    }


def _select_diverse(
    rows: list[dict[str, Any]],
    top_k: int,
    max_per_herb: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_keys: set[tuple[int, int]] = set()
    herb_counts: Counter[str] = Counter()
    for row in rows:
        key = (row["herb_id"], row["adr_id"])
        herb = row["herb_latin"]
        if herb_counts[herb] >= max_per_herb:
            continue
        selected.append(row)
        selected_keys.add(key)
        herb_counts[herb] += 1
        if len(selected) >= top_k:
            return selected
    for row in rows:
        key = (row["herb_id"], row["adr_id"])
        if key in selected_keys:
            continue
        selected.append(row)
        selected_keys.add(key)
        if len(selected) >= top_k:
            break
    return selected


def build_evidence_aware_queue(
    top_predictions_payload: dict[str, Any],
    batch_interpretability_payload: dict[str, Any] | None = None,
    top_k: int = 30,
    max_per_herb: int = 5,
) -> dict[str, Any]:
    prior_by_pair = _prior_perturbation_index(batch_interpretability_payload or {})
    explicit_rows = [row for row in _candidate_rows(top_predictions_payload) if _has_explicit_path(row)]
    scored = [
        _score_row(row, prior_by_pair.get(_pair_key(row), {}))
        for row in explicit_rows
        if row.get("herb_id") not in (None, "") and row.get("adr_id") not in (None, "")
    ]
    scored.sort(
        key=lambda row: (
            -row["evidence_priority_score"],
            -row["prior_perturbation_score_drop"],
            -row["evidence_retrievability_score"],
            row["source_rank"],
            row["herb_id"],
            row["adr_id"],
        )
    )
    selected = _select_diverse(scored, max(1, int(top_k)), max(1, int(max_per_herb)))
    for index, row in enumerate(selected, start=1):
        row["rank"] = index

    herb_counts = Counter(row["herb_latin"] for row in explicit_rows)
    selected_herb_counts = Counter(row["herb_latin"] for row in selected)
    return {
        "experiment": "evidence_aware_mechanism_candidate_queue",
        "created_at": datetime.now().isoformat(),
        "source_experiment": top_predictions_payload.get("experiment", ""),
        "checkpoint_path": top_predictions_payload.get("checkpoint_path", ""),
        "checkpoint_context": top_predictions_payload.get("checkpoint_context", {}),
        "claim_boundary": CLAIM_BOUNDARY,
        "scoring_note": (
            "Scores combine model score, source rank, explicit path coverage, prior "
            "perturbation if already quantified, evidence-retrievability heuristics, "
            "and a top-k diversity cap. They are prioritization scores only."
        ),
        "summary": {
            "top_prediction_candidate_count": len(_candidate_rows(top_predictions_payload)),
            "explicit_path_candidate_count": len(explicit_rows),
            "prior_perturbation_matched_count": sum(
                1 for row in explicit_rows if _pair_key(row) in prior_by_pair
            ),
            "queued_count": len(selected),
            "requested_top_k": int(top_k),
            "diversity_max_per_herb": int(max_per_herb),
            "explicit_pool_unique_herb_count": len(herb_counts),
            "queued_unique_herb_count": len(selected_herb_counts),
            "most_common_explicit_pool_herbs": dict(herb_counts.most_common(10)),
            "queued_herb_counts": dict(selected_herb_counts),
        },
        "rows": selected,
    }


def write_outputs(
    queue: dict[str, Any],
    output_json: str | Path,
    output_csv: str | Path,
    output_md: str | Path,
) -> None:
    output_json = Path(output_json)
    output_csv = Path(output_csv)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(queue, ensure_ascii=False, indent=2))
    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in queue.get("rows", []):
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})

    lines = [
        "# PU-XMSAT Evidence-Aware Mechanism Candidate Queue",
        "",
        f"**Generated:** {queue['created_at']}",
        f"**Claim boundary:** {queue['claim_boundary']}",
        "",
        "## Summary",
        "",
        f"- Explicit-path candidates: {queue['summary']['explicit_path_candidate_count']}",
        f"- Prior perturbation matches: {queue['summary']['prior_perturbation_matched_count']}",
        f"- Queued candidates: {queue['summary']['queued_count']}",
        f"- Unique herbs in queue: {queue['summary']['queued_unique_herb_count']}",
        f"- Max rows per herb before backfill: {queue['summary']['diversity_max_per_herb']}",
        "",
        "## Top Queue",
        "",
        "| Rank | Source rank | Candidate | Priority | Retrievability | Prior drop | Paths | Review query |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in queue.get("rows", []):
        candidate = f"{row['herb_latin']} -> {row['adr_pt']}"
        lines.append(
            f"| {row['rank']} | {row['source_rank']} | {candidate} "
            f"| {row['evidence_priority_score']:.6f} "
            f"| {row['evidence_retrievability_score']:.3f} "
            f"| {row['prior_perturbation_score_drop']:.6g} "
            f"| {row['explicit_mechanism_path_count']} "
            f"| `{row['pubmed_exact_query']}` |"
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this queue to select candidates for manual external evidence review. "
            "Do not present queued rows as validated mechanisms unless direct source "
            "evidence is manually verified.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build an evidence-aware review queue from explicit-path PU-XMSAT candidates."
    )
    parser.add_argument("--top-predictions", default=str(DEFAULT_TOP_PREDICTIONS))
    parser.add_argument("--batch-interpretability", default=str(DEFAULT_BATCH_INTERPRETABILITY))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--top-k", type=int, default=30)
    parser.add_argument("--max-per-herb", type=int, default=5)
    args = parser.parse_args()

    queue = build_evidence_aware_queue(
        _load_json(args.top_predictions),
        _load_json(args.batch_interpretability),
        top_k=args.top_k,
        max_per_herb=args.max_per_herb,
    )
    write_outputs(queue, args.output_json, args.output_csv, args.output_md)
    print(
        json.dumps(
            {
                "explicit_path_candidate_count": queue["summary"][
                    "explicit_path_candidate_count"
                ],
                "queued_count": queue["summary"]["queued_count"],
                "queued_unique_herb_count": queue["summary"]["queued_unique_herb_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
