from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_BATCH_PATH = Path("results/batch_mechanism_interpretability.json")
DEFAULT_CONTRIBUTION_PATH = Path("results/contribution_quantification.json")
DEFAULT_CASE_EVIDENCE_PATH = Path("results/case_evidence_report.json")
DEFAULT_MANUAL_REVIEW_PATH = Path("results/case_evidence_manual_review.json")
DEFAULT_OUTPUT_JSON = Path("results/direction3_targeted_review_queue.json")
DEFAULT_OUTPUT_CSV = Path("results/direction3_targeted_review_queue.csv")
DEFAULT_OUTPUT_MD = Path("results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md")

CLAIM_BOUNDARY = (
    "This queue prioritizes external-evidence review based on local perturbation "
    "sensitivity. It is not external validation and does not upgrade evidence "
    "grades without manual source review."
)

CSV_FIELDS = [
    "rank",
    "herb_id",
    "adr_id",
    "herb_latin",
    "adr_pt",
    "source",
    "original_score",
    "priority_score",
    "max_path_score_drop",
    "max_target_score_drop",
    "max_component_score_drop",
    "top_path_features",
    "top_path_text",
    "max_node_score_drop",
    "top_node_feature",
    "top_node_type",
    "evidence_grade",
    "updated_grade_recommendation",
    "manual_review_status",
    "paper_use",
    "direct_literature_support",
    "literature_record_count",
    "literature_support_candidate_count",
    "verified_literature_count",
    "review_action",
]


def _load_json(path: str | Path) -> dict[str, Any]:
    src = Path(path)
    if not src.exists():
        return {}
    return json.loads(src.read_text())


def _key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["herb_id"]), int(row["adr_id"])


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _index_rows(payload: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    return {
        _key(row): row
        for row in payload.get("rows", [])
        if row.get("herb_id") not in (None, "") and row.get("adr_id") not in (None, "")
    }


def _best_path(case: dict[str, Any]) -> dict[str, Any]:
    paths = list(case.get("pathway_contributions", []) or case.get("path_contributions", []))
    if not paths:
        return {}
    return max(paths, key=lambda row: max(0.0, _float(row.get("score_drop"))))


def _best_node(case: dict[str, Any], node_type: str | None = None) -> dict[str, Any]:
    if node_type == "target":
        nodes = list(case.get("target_contributions", []))
    elif node_type == "component":
        nodes = list(case.get("component_contributions", []))
    else:
        nodes = list(case.get("node_contributions", []) or case.get("contributions", []))
        if not nodes:
            nodes = list(case.get("target_contributions", [])) + list(
                case.get("component_contributions", [])
            )
    if not nodes:
        return {}
    return max(nodes, key=lambda row: max(0.0, _float(row.get("score_drop"))))


def _join_features(features: Any) -> str:
    if isinstance(features, list):
        return ";".join(str(feature) for feature in features)
    return str(features or "")


def _review_action(
    evidence: dict[str, Any],
    manual: dict[str, Any],
    priority_score: float,
) -> str:
    updated_grade = str(manual.get("updated_grade_recommendation") or "").upper()
    if updated_grade in {"A", "B"}:
        return "ready_for_strong_evidence_writeup"
    if manual:
        return "preserve_as_mechanism_screening_boundary"
    if priority_score > 0:
        return "target_external_evidence_review"
    return "low_priority_screening"


def _queue_row(
    case: dict[str, Any],
    evidence_by_pair: dict[tuple[int, int], dict[str, Any]],
    manual_by_pair: dict[tuple[int, int], dict[str, Any]],
) -> dict[str, Any]:
    pair = _key(case)
    evidence = evidence_by_pair.get(pair, {})
    manual = manual_by_pair.get(pair, {})
    best_path = _best_path(case)
    best_node = _best_node(case)
    best_target = _best_node(case, "target")
    best_component = _best_node(case, "component")
    max_path_drop = max(0.0, _float(best_path.get("score_drop")))
    max_node_drop = max(0.0, _float(best_node.get("score_drop")))
    max_target_drop = max(0.0, _float(best_target.get("score_drop")))
    max_component_drop = max(0.0, _float(best_component.get("score_drop")))
    priority_score = max(max_path_drop, max_target_drop, max_component_drop, max_node_drop)

    return {
        "herb_id": pair[0],
        "adr_id": pair[1],
        "herb_latin": evidence.get("herb_latin") or manual.get("herb_latin") or "",
        "adr_pt": evidence.get("adr_pt") or manual.get("adr_pt") or "",
        "source": case.get("source", ""),
        "original_score": case.get("original_score"),
        "priority_score": priority_score,
        "max_path_score_drop": max_path_drop,
        "max_target_score_drop": max_target_drop,
        "max_component_score_drop": max_component_drop,
        "top_path_features": _join_features(best_path.get("features"))
        or str(best_path.get("path_features", "")),
        "top_path_text": best_path.get("path_text", ""),
        "max_node_score_drop": max_node_drop,
        "top_node_feature": best_node.get("feature", ""),
        "top_node_type": best_node.get("node_type", ""),
        "evidence_grade": evidence.get("evidence_grade", ""),
        "updated_grade_recommendation": manual.get("updated_grade_recommendation", ""),
        "manual_review_status": manual.get("manual_review_status", ""),
        "paper_use": manual.get("paper_use", ""),
        "direct_literature_support": _truthy(evidence.get("direct_literature_support")),
        "literature_record_count": int(evidence.get("literature_record_count", 0) or 0),
        "literature_support_candidate_count": int(
            evidence.get("literature_support_candidate_count", 0) or 0
        ),
        "verified_literature_count": int(evidence.get("verified_literature_count", 0) or 0),
        "review_action": _review_action(evidence, manual, priority_score),
    }


def build_targeted_review_queue(
    contribution_payload: dict[str, Any],
    case_evidence_payload: dict[str, Any],
    manual_review_payload: dict[str, Any] | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    evidence_by_pair = _index_rows(case_evidence_payload)
    manual_by_pair = _index_rows(manual_review_payload or {})
    rows = [
        _queue_row(case, evidence_by_pair, manual_by_pair)
        for case in contribution_payload.get("cases", [])
    ]
    rows.sort(
        key=lambda row: (
            -_float(row.get("max_path_score_drop")),
            -_float(row.get("max_target_score_drop")),
            -_float(row.get("max_component_score_drop")),
            -_float(row.get("original_score")),
            row.get("herb_id", 0),
            row.get("adr_id", 0),
        )
    )
    if top_k is not None:
        rows = rows[:top_k]
    for index, row in enumerate(rows, start=1):
        row["rank"] = index

    evidence_counts = Counter(str(row.get("evidence_grade") or "unknown") for row in rows)
    updated_counts = Counter(
        str(row.get("updated_grade_recommendation") or "not_reviewed") for row in rows
    )
    action_counts = Counter(row["review_action"] for row in rows)
    return {
        "experiment": "direction3_targeted_review_queue",
        "created_at": datetime.now().isoformat(),
        "source_experiment": contribution_payload.get("experiment"),
        "checkpoint_path": contribution_payload.get("checkpoint_path", ""),
        "checkpoint_context": contribution_payload.get("checkpoint_context", ""),
        "source_claim_boundary": contribution_payload.get("claim_boundary", ""),
        "claim_boundary": CLAIM_BOUNDARY,
        "review_boundaries": [
            "Perturbation high cannot upgrade evidence grade.",
            "Grade C is not external validation.",
            "Negative score_drop is not protective evidence.",
            "No causal claims.",
            "No manual direct evidence means no Grade A/B.",
        ],
        "summary": {
            "case_count": len(rows),
            "manual_reviewed_count": sum(1 for row in rows if row["manual_review_status"]),
            "ready_strong_evidence_count": action_counts.get(
                "ready_for_strong_evidence_writeup", 0
            ),
            "target_external_evidence_review_count": action_counts.get(
                "target_external_evidence_review", 0
            ),
            "boundary_case_count": action_counts.get(
                "preserve_as_mechanism_screening_boundary", 0
            ),
            "evidence_grade_counts": dict(evidence_counts),
            "updated_grade_recommendation_counts": dict(updated_counts),
            "review_action_counts": dict(action_counts),
        },
        "rows": rows,
    }


def write_queue_artifacts(
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
        for row in queue["rows"]:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})

    lines = [
        "# PU-XMSAT Direction 3 Targeted Review Queue",
        "",
        f"**Generated at:** {queue['created_at']}",
        f"**Claim boundary:** {queue['claim_boundary']}",
        "",
        "## Summary",
        "",
        f"- Cases queued: {queue['summary']['case_count']}",
        f"- Manually reviewed cases: {queue['summary']['manual_reviewed_count']}",
        f"- Ready strong-evidence cases: {queue['summary']['ready_strong_evidence_count']}",
        f"- Boundary/screening cases: {queue['summary']['boundary_case_count']}",
        f"- Target external-evidence review cases: {queue['summary']['target_external_evidence_review_count']}",
        "",
        "## Queue",
        "",
        "| Rank | Pair | Evidence | Manual status | Priority drop | Top path | Action |",
        "| ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in queue["rows"]:
        pair = f"{row['herb_latin'] or 'Herb ' + str(row['herb_id'])} -> {row['adr_pt'] or 'ADR ' + str(row['adr_id'])}"
        manual_status = row["manual_review_status"] or "not reviewed"
        top_path = row["top_path_features"] or row["top_node_feature"]
        lines.append(
            f"| {row['rank']} | {pair} | {row['evidence_grade'] or 'unknown'} "
            f"| {manual_status} | {row['priority_score']:.6g} | `{top_path}` "
            f"| {row['review_action']} |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
        ]
    )
    for boundary in queue.get("review_boundaries", []):
        lines.append(f"- {boundary}")
    lines.extend(
        [
            "",
            "## Use In Manuscript",
            "",
            "Use this artifact to explain how Direction 2 perturbation sensitivity selects cases for Direction 3 review. Do not present queued cases as external validation unless the row is manually upgraded to Grade A or B with direct source evidence.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a Direction 3 targeted evidence-review queue from contribution sensitivity."
    )
    parser.add_argument(
        "--contribution",
        default=None,
        help=(
            "Contribution or batch interpretability JSON. Defaults to batch results "
            "when present, otherwise contribution_quantification.json."
        ),
    )
    parser.add_argument("--case-evidence", default=str(DEFAULT_CASE_EVIDENCE_PATH))
    parser.add_argument("--manual-review", default=str(DEFAULT_MANUAL_REVIEW_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    contribution_path = args.contribution
    if contribution_path is None:
        contribution_path = str(DEFAULT_BATCH_PATH if DEFAULT_BATCH_PATH.exists() else DEFAULT_CONTRIBUTION_PATH)
    queue = build_targeted_review_queue(
        _load_json(contribution_path),
        _load_json(args.case_evidence),
        _load_json(args.manual_review),
        top_k=args.top_k,
    )
    write_queue_artifacts(queue, args.output_json, args.output_csv, args.output_md)
    print(
        json.dumps(
            {
                "case_count": queue["summary"]["case_count"],
                "ready_strong_evidence_count": queue["summary"][
                    "ready_strong_evidence_count"
                ],
                "boundary_case_count": queue["summary"]["boundary_case_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
