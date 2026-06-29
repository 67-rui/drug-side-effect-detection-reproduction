from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from inference.contribution_scoring import (
    build_key_mechanism_subgraph,
    extract_node_refs_from_paths,
)


DEFAULT_TOP_K = 20
NEAR_ZERO_THRESHOLD = 1e-4
CLAIM_BOUNDARY = (
    "Perturbation score drops are local sensitivity signals for mechanism triage; "
    "they are not causal effects, not SHAP values, and not external clinical validation."
)
TRANSITIONAL_NOTE = (
    "Current candidates come from mechanism-supported transitional artifacts, not final "
    "PU-XMSAT top-ranking export."
)
NONFINAL_TOP_PREDICTION_NOTE = (
    "Candidates come from a PU-XMSAT top-prediction export, but this is not final "
    "10-fold PU-XMSAT top-ranking export unless the source artifact explicitly marks it."
)

CSV_FIELDS = [
    "row_type",
    "case_index",
    "contribution_group",
    "source",
    "herb_id",
    "adr_id",
    "feature",
    "display_name",
    "name_source",
    "node_type",
    "node_id",
    "path_features",
    "path_display_features",
    "path_text",
    "score_drop",
    "masked_score",
    "drop_class",
    "case_count",
    "occurrence_count",
    "mean_score_drop",
    "max_score_drop",
    "positive_drop_count",
    "near_zero_drop_count",
    "negative_drop_count",
]


def _load_json(path: str | Path) -> dict[str, Any]:
    src = Path(path)
    if not src.exists():
        return {}
    return json.loads(src.read_text())


def _path_texts(row: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("top_mechanism_paths", "paths", "mechanism_paths"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value.strip())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    text = item.get("path") or item.get("path_text") or item.get("template") or ""
                else:
                    text = str(item)
                if text:
                    paths.append(text)
    return paths


def _row_score(row: dict[str, Any]) -> float:
    for key in ("prediction_score", "score", "original_score"):
        if row.get(key) not in (None, ""):
            return float(row[key])
    return 0.0


def _candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows") or payload.get("cases") or payload.get("candidates") or []
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def _coverage_missing_candidate(row: dict[str, Any], source: str) -> dict[str, Any] | None:
    if row.get("herb_id") in (None, "") or row.get("adr_id") in (None, ""):
        return None
    paths = _path_texts(row)
    status = "missing_explicit_mechanism_path"
    if paths and not extract_node_refs_from_paths(paths):
        status = "unparseable_explicit_mechanism_path"
    return {
        "source": row.get("source") or source,
        "rank": row.get("rank", ""),
        "herb_id": int(row["herb_id"]),
        "adr_id": int(row["adr_id"]),
        "score": _row_score(row),
        "coverage_status": status,
        "explicit_mechanism_path_count": len(paths),
    }


def _normal_candidate(row: dict[str, Any], source: str, priority: int) -> dict[str, Any] | None:
    if row.get("herb_id") in (None, "") or row.get("adr_id") in (None, ""):
        return None
    paths = _path_texts(row)
    if not paths:
        return None
    node_refs = extract_node_refs_from_paths(paths)
    if not node_refs:
        return None
    return {
        "source": row.get("source") or source,
        "candidate_source_detail": source,
        "source_priority": priority,
        "rank": row.get("rank", ""),
        "herb_id": int(row["herb_id"]),
        "adr_id": int(row["adr_id"]),
        "score": _row_score(row),
        "paths": paths,
        "explicit_mechanism_path_count": len(paths),
        "explicit_mechanism_node_ref_count": len(node_refs),
    }


def _dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[int, int]] = set()
    output = []
    for row in sorted(
        candidates,
        key=lambda item: (
            int(item["source_priority"]),
            -float(item.get("score", 0.0)),
            int(item["herb_id"]),
            int(item["adr_id"]),
        ),
    ):
        key = (int(row["herb_id"]), int(row["adr_id"]))
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


def _collect_from_payload(payload: dict[str, Any], source: str, priority: int) -> list[dict[str, Any]]:
    candidates = []
    for row in _candidate_rows(payload):
        candidate = _normal_candidate(row, source=source, priority=priority)
        if candidate:
            candidates.append(candidate)
    return candidates


def compute_topk_mechanism_coverage(
    final_predictions_payload: dict[str, Any],
    cutoffs: tuple[int, ...] = (50, 100, 500, 1000, 5000),
) -> list[dict[str, Any]]:
    rows = _candidate_rows(final_predictions_payload)
    coverage_rows = []
    for cutoff in cutoffs:
        top_rows = rows[: max(0, int(cutoff))]
        candidate_count = len(top_rows)
        explicit_count = sum(
            1
            for row in top_rows
            if _normal_candidate(row, "pu_xmsat_top_predictions", 0) is not None
        )
        coverage_rows.append(
            {
                "top_k": int(cutoff),
                "candidate_count": candidate_count,
                "explicit_path_candidate_count": explicit_count,
                "coverage_rate": (explicit_count / candidate_count) if candidate_count else 0.0,
            }
        )
    return coverage_rows


def _is_final_top_prediction_export(payload: dict[str, Any]) -> bool:
    checkpoint_context = payload.get("checkpoint_context") or {}
    if isinstance(checkpoint_context, dict):
        return bool(checkpoint_context.get("is_final_10fold_export"))
    return bool(payload.get("checkpoint_is_final_pu_xmsat"))


def select_top_mechanism_candidates(
    final_predictions_payload: dict[str, Any],
    case_evidence_payload: dict[str, Any],
    table5_payload: dict[str, Any],
    explanation_payload: dict[str, Any],
    structured_mechanism_payload: dict[str, Any],
    top_k: int = DEFAULT_TOP_K,
    candidate_pool_top_k: int | None = None,
    coverage_cutoffs: tuple[int, ...] = (50, 100, 500, 1000, 5000),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    requested_top_k = max(1, int(top_k))
    pool_top_k = max(requested_top_k, int(candidate_pool_top_k or requested_top_k))
    available_top_prediction_rows = _candidate_rows(final_predictions_payload)
    top_prediction_rows = available_top_prediction_rows[:pool_top_k]
    top_prediction_available_count = len(available_top_prediction_rows)
    candidate_pool_missing_count = max(0, pool_top_k - top_prediction_available_count)
    candidate_pool_is_complete = candidate_pool_missing_count == 0
    coverage_by_topk = compute_topk_mechanism_coverage(
        final_predictions_payload,
        cutoffs=coverage_cutoffs,
    )
    final_candidates = _dedupe_candidates(
        _collect_from_payload(
            {"rows": top_prediction_rows},
            "pu_xmsat_top_predictions",
            0,
        )
    )
    coverage_missing_candidates: list[dict[str, Any]] = []
    if top_prediction_rows:
        for row in top_prediction_rows:
            if _normal_candidate(row, "pu_xmsat_top_predictions", 0) is None:
                missing = _coverage_missing_candidate(row, "pu_xmsat_top_predictions")
                if missing:
                    coverage_missing_candidates.append(missing)

    if final_candidates:
        selected = final_candidates[:requested_top_k]
        is_final_export = _is_final_top_prediction_export(final_predictions_payload)
        metadata = {
            "candidate_source": (
                "final_pu_xmsat_top_predictions"
                if is_final_export
                else "pu_xmsat_top_predictions_nonfinal_export"
            ),
            "candidate_source_note": (
                "Final PU-XMSAT top-ranking export."
                if is_final_export
                else NONFINAL_TOP_PREDICTION_NOTE
            ),
            "is_final_pu_top_ranking_export": is_final_export,
            "top_prediction_checkpoint_context": final_predictions_payload.get(
                "checkpoint_context",
                {},
            ),
            "top_prediction_candidate_count": len(
                [
                    row
                    for row in top_prediction_rows
                    if row.get("herb_id") not in (None, "") and row.get("adr_id") not in (None, "")
                ]
            ),
            "top_prediction_available_count": top_prediction_available_count,
            "candidate_pool_top_k": pool_top_k,
            "candidate_pool_missing_count": candidate_pool_missing_count,
            "candidate_pool_is_complete": candidate_pool_is_complete,
            "mechanism_coverage_by_topk": coverage_by_topk,
            "coverage_missing_candidate_count": len(coverage_missing_candidates),
            "coverage_missing_candidates": coverage_missing_candidates,
        }
    else:
        transitional = []
        transitional.extend(_collect_from_payload(case_evidence_payload, "case_evidence_report", 1))
        transitional.extend(_collect_from_payload(table5_payload, "table5_top15", 2))
        transitional.extend(_collect_from_payload(explanation_payload, "explanation_case_studies", 3))
        transitional.extend(
            _collect_from_payload(
                structured_mechanism_payload,
                "structured_mechanism_explanation_artifacts",
                4,
            )
        )
        selected = _dedupe_candidates(transitional)[:requested_top_k]
        metadata = {
            "candidate_source": "transitional_mechanism_supported_artifacts",
            "candidate_source_note": TRANSITIONAL_NOTE,
            "is_final_pu_top_ranking_export": False,
            "top_prediction_candidate_count": 0,
            "top_prediction_available_count": top_prediction_available_count,
            "candidate_pool_top_k": pool_top_k,
            "candidate_pool_missing_count": candidate_pool_missing_count,
            "candidate_pool_is_complete": candidate_pool_is_complete,
            "mechanism_coverage_by_topk": coverage_by_topk,
            "coverage_missing_candidate_count": 0,
            "coverage_missing_candidates": [],
        }

    metadata.update(
        {
            "requested_top_k": requested_top_k,
            "selected_count": len(selected),
            "explicit_path_candidate_count": len(selected),
            "fewer_than_top_k_reason": (
                f"Only {len(selected)} candidates with explicit mechanism paths were available."
                if len(selected) < requested_top_k
                else ""
            ),
        }
    )
    return selected, metadata


def _summarize_random_controls(random_controls: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(random_controls, dict):
        return {}
    summary = {}
    for group, rows in random_controls.items():
        if not isinstance(rows, list):
            continue
        drops = [
            float(row.get("score_drop", 0.0))
            for row in rows
            if isinstance(row, dict) and row.get("score_drop") not in (None, "")
        ]
        summary[str(group)] = {
            "count": len(drops),
            "mean_score_drop": round(mean(drops), 10) if drops else 0.0,
            "max_score_drop": round(max(drops), 10) if drops else 0.0,
        }
    return summary


def _case_key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["herb_id"]), int(row["adr_id"])


def _drop_class(score_drop: float) -> str:
    value = float(score_drop)
    if value > NEAR_ZERO_THRESHOLD:
        return "positive"
    if value < -NEAR_ZERO_THRESHOLD:
        return "negative"
    return "near_zero"


def _path_features(row: dict[str, Any]) -> str:
    features = row.get("features") or row.get("path_features")
    if isinstance(features, list):
        return ";".join(str(feature) for feature in features)
    return str(features or "")


def _feature_display(feature: Any) -> str:
    text = str(feature or "")
    if ":" not in text:
        return text
    node_type, node_id = text.split(":", 1)
    if node_type == "compound":
        return f"Compound #{node_id}"
    if node_type == "target":
        return f"Target #{node_id}"
    return text


def _feature_source(feature: Any) -> str:
    text = str(feature or "")
    if text.startswith(("compound:", "target:")):
        return "unmapped_graph_id"
    return ""


def _with_node_display(row: dict[str, Any]) -> dict[str, Any]:
    feature = row.get("feature")
    output = dict(row)
    if not output.get("display_name"):
        output["display_name"] = _feature_display(feature)
    if not output.get("name_source"):
        output["name_source"] = _feature_source(feature)
    return output


def _path_display_features(row: dict[str, Any]) -> str:
    display = row.get("display_features") or row.get("path_display_features")
    if isinstance(display, list):
        return ";".join(str(feature) for feature in display)
    if display:
        return str(display)
    features = row.get("features") or row.get("path_features")
    if isinstance(features, list):
        return ";".join(_feature_display(feature) for feature in features)
    if isinstance(features, str) and features:
        return ";".join(_feature_display(feature) for feature in features.split(";"))
    return ""


def _aggregate(rows: list[dict[str, Any]], aggregate_type: str, key_field: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get(key_field, ""))
        if not key:
            continue
        bucket = buckets.setdefault(
            key,
            {
                "aggregate_type": aggregate_type,
                "feature": row.get("feature", ""),
                "display_name": row.get("display_name", ""),
                "name_source": row.get("name_source", ""),
                "node_type": row.get("node_type", ""),
                "node_id": row.get("node_id", ""),
                "path_features": row.get("path_features", ""),
                "path_display_features": row.get("path_display_features", ""),
                "case_keys": set(),
                "score_drops": [],
            },
        )
        bucket["case_keys"].add(row["case_key"])
        bucket["score_drops"].append(float(row.get("score_drop", 0.0)))
    output = []
    for bucket in buckets.values():
        drops = bucket.pop("score_drops")
        case_keys = bucket.pop("case_keys")
        classes = [_drop_class(value) for value in drops]
        bucket.update(
            {
                "case_count": len(case_keys),
                "occurrence_count": len(drops),
                "mean_score_drop": round(mean(drops), 10) if drops else 0.0,
                "max_score_drop": round(max(drops), 10) if drops else 0.0,
                "positive_drop_count": classes.count("positive"),
                "near_zero_drop_count": classes.count("near_zero"),
                "negative_drop_count": classes.count("negative"),
            }
        )
        output.append(bucket)
    return sorted(
        output,
        key=lambda row: (
            -float(row["max_score_drop"]),
            -float(row["mean_score_drop"]),
            str(row.get(key_field, "")),
        ),
    )


def _top_case_explanation(case: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for group in ("pathway_contributions", "target_contributions", "component_contributions"):
        for row in case.get(group, []):
            candidates.append({**row, "group": group.replace("_contributions", "")})
    if not candidates:
        return {}
    return max(candidates, key=lambda row: float(row.get("score_drop", 0.0)))


def build_batch_payload_from_contributions(
    candidates: list[dict[str, Any]],
    candidate_metadata: dict[str, Any],
    contribution_payload: dict[str, Any],
    checkpoint_path: str | None = None,
    checkpoint_is_final_pu: bool = False,
) -> dict[str, Any]:
    contributions_by_pair = {
        _case_key(case): case for case in contribution_payload.get("cases", [])
    }
    cases = []
    flat_components = []
    flat_targets = []
    flat_pathways = []

    for case_index, candidate in enumerate(candidates, start=1):
        contribution_case = contributions_by_pair.get(_case_key(candidate), {})
        path_texts = contribution_case.get("paths") or candidate.get("paths", [])
        mechanism_subgraph = contribution_case.get("mechanism_subgraph") or build_key_mechanism_subgraph(path_texts)
        component_rows = []
        target_rows = []
        for row in contribution_case.get("node_contributions", []):
            normalized = _with_node_display(
                {**row, "drop_class": _drop_class(float(row.get("score_drop", 0.0)))}
            )
            if row.get("node_type") == "compound":
                component_rows.append(normalized)
            elif row.get("node_type") == "target":
                target_rows.append(normalized)
        pathway_rows = []
        for row in contribution_case.get("path_contributions", []):
            normalized = {
                **row,
                "path_features": _path_features(row),
                "path_display_features": _path_display_features(row),
                "drop_class": _drop_class(float(row.get("score_drop", 0.0))),
            }
            pathway_rows.append(normalized)

        has_perturbation_rows = bool(component_rows or target_rows or pathway_rows)
        all_drops = [
            float(row.get("score_drop", 0.0))
            for row in [*component_rows, *target_rows, *pathway_rows]
        ]
        max_positive_drop = max([value for value in all_drops if value > 0], default=0.0)
        case_key = f"{case_index}:{candidate['source']}:{candidate['herb_id']}:{candidate['adr_id']}"
        case = {
            "case_index": case_index,
            "source": candidate["source"],
            "candidate_source_detail": candidate.get("candidate_source_detail", ""),
            "herb_id": int(candidate["herb_id"]),
            "adr_id": int(candidate["adr_id"]),
            "original_score": contribution_case.get("original_score", candidate.get("score")),
            "paths": path_texts,
            "explicit_mechanism_path_count": len(path_texts),
            "mechanism_subgraph": mechanism_subgraph,
            "component_contributions": component_rows,
            "target_contributions": target_rows,
            "pathway_contributions": pathway_rows,
            "top_explanation": {},
            "max_positive_score_drop": max_positive_drop,
            "sensitivity_class": (
                "unquantified"
                if not has_perturbation_rows
                else "near_zero"
                if max_positive_drop <= NEAR_ZERO_THRESHOLD
                else "positive"
            ),
            "has_negative_score_drop": any(value < -NEAR_ZERO_THRESHOLD for value in all_drops),
            "used_existing_contribution_rows": bool(contribution_case),
            "has_perturbation_rows": has_perturbation_rows,
        }
        case["top_explanation"] = _top_case_explanation(case)
        cases.append(case)

        for row in component_rows:
            flat_components.append({**row, "case_key": case_key})
        for row in target_rows:
            flat_targets.append({**row, "case_key": case_key})
        for row in pathway_rows:
            flat_pathways.append({**row, "case_key": case_key})

    component_contributions = _aggregate(flat_components, "component", "feature")
    target_contributions = _aggregate(flat_targets, "target", "feature")
    pathway_contributions = _aggregate(flat_pathways, "pathway", "path_features")
    random_control_summary = _summarize_random_controls(
        contribution_payload.get("random_controls")
    )
    explicit_unquantified_count = sum(1 for case in cases if not case["has_perturbation_rows"])
    coverage_missing_count = int(candidate_metadata.get("coverage_missing_candidate_count", 0))
    final_checkpoint = bool(checkpoint_is_final_pu)
    checkpoint_context = (
        "Final full-positive hybrid PU-XMSAT checkpoint attribution."
        if final_checkpoint
        else (
            "Fallback batch interpretability reuses existing contribution rows from the "
            "local predictor checkpoint because no final full-positive hybrid PU-XMSAT "
            "predictor checkpoint is available."
        )
    )
    return {
        "experiment": "batch_mechanism_interpretability",
        "created_at": datetime.now().isoformat(),
        **candidate_metadata,
        "checkpoint_path": checkpoint_path or contribution_payload.get("checkpoint_path", "unknown"),
        "checkpoint_is_final_pu_xmsat": final_checkpoint,
        "checkpoint_context": checkpoint_context,
        "claim_boundary": CLAIM_BOUNDARY,
        "fallback_contribution_source": contribution_payload.get("experiment", "unknown"),
        "summary": {
            "requested_top_k": candidate_metadata.get("requested_top_k", DEFAULT_TOP_K),
            "top_prediction_candidate_count": candidate_metadata.get("top_prediction_candidate_count", 0),
            "top_prediction_available_count": candidate_metadata.get("top_prediction_available_count", 0),
            "candidate_pool_top_k": candidate_metadata.get("candidate_pool_top_k", 0),
            "candidate_pool_missing_count": candidate_metadata.get("candidate_pool_missing_count", 0),
            "candidate_pool_is_complete": bool(candidate_metadata.get("candidate_pool_is_complete", False)),
            "coverage_missing_candidate_count": coverage_missing_count,
            "candidate_count": len(candidates),
            "quantified_case_count": sum(1 for case in cases if case["has_perturbation_rows"]),
            "unquantified_candidate_count": explicit_unquantified_count + coverage_missing_count,
            "unquantified_explicit_path_candidate_count": explicit_unquantified_count,
            "cases_with_explicit_mechanism_paths": sum(
                1 for case in cases if case["explicit_mechanism_path_count"] > 0
            ),
            "near_zero_sensitivity_case_count": sum(
                1
                for case in cases
                if case["has_perturbation_rows"] and case["sensitivity_class"] == "near_zero"
            ),
            "negative_score_drop_case_count": sum(
                1
                for case in cases
                if case["has_perturbation_rows"] and case["has_negative_score_drop"]
            ),
            "has_random_perturbation_controls": bool(random_control_summary),
            "fewer_than_top_k_reason": candidate_metadata.get("fewer_than_top_k_reason", ""),
        },
        "cases": cases,
        "coverage_missing_candidates": candidate_metadata.get("coverage_missing_candidates", []),
        "mechanism_coverage_by_topk": candidate_metadata.get("mechanism_coverage_by_topk", []),
        "random_control_summary": random_control_summary,
        "component_contributions": component_contributions,
        "target_contributions": target_contributions,
        "pathway_contributions": pathway_contributions,
    }


def _format_float(value: Any) -> str:
    return f"{float(value):.6f}"


def _write_markdown(payload: dict[str, Any], output_md: Path) -> None:
    source_note = payload.get("candidate_source_note", "")
    lines = [
        "# PU-XMSAT Batch Mechanism Interpretability",
        "",
        f"- Candidate source: `{payload.get('candidate_source', 'unknown')}`",
        f"- Candidate source note: {source_note}",
        f"- Checkpoint path: `{payload.get('checkpoint_path', 'unknown')}`",
        f"- Checkpoint is final PU-XMSAT: {'yes' if payload.get('checkpoint_is_final_pu_xmsat') else 'no'}",
        f"- Checkpoint context: {payload.get('checkpoint_context', 'not specified')}",
        f"- Quantified case count: {payload['summary']['quantified_case_count']}",
        f"- Top-prediction candidates checked: {payload['summary'].get('top_prediction_candidate_count', 0)}",
        f"- Top-prediction rows available: {payload['summary'].get('top_prediction_available_count', 0)}",
        f"- Requested candidate pool top-K: {payload['summary'].get('candidate_pool_top_k', 0)}",
        f"- Candidate pool complete: {'yes' if payload['summary'].get('candidate_pool_is_complete') else 'no'}",
        f"- Candidate pool missing rows: {payload['summary'].get('candidate_pool_missing_count', 0)}",
        f"- Coverage-missing top-prediction candidates: {payload['summary'].get('coverage_missing_candidate_count', 0)}",
        f"- Unquantified explicit-path candidates: {payload['summary'].get('unquantified_explicit_path_candidate_count', 0)}",
        f"- Cases with explicit mechanism paths: {payload['summary']['cases_with_explicit_mechanism_paths']}",
        f"- Near-zero sensitivity cases: {payload['summary']['near_zero_sensitivity_case_count']}",
        f"- Negative score_drop cases: {payload['summary']['negative_score_drop_case_count']}",
    ]
    if payload["summary"].get("fewer_than_top_k_reason"):
        lines.append(f"- Fewer than requested top-K: {payload['summary']['fewer_than_top_k_reason']}")
    if payload.get("coverage_missing_candidates"):
        lines.append(
            "- Coverage boundary: top-prediction candidates without parseable explicit mechanism "
            "paths were counted as coverage-missing, not silently dropped."
        )
    if payload.get("mechanism_coverage_by_topk"):
        lines.append(
            "- Mechanism coverage by top-K: reported separately so mechanism-supported "
            "cases are not treated as representative of all top-ranked predictions."
        )
    if payload["summary"].get("has_random_perturbation_controls"):
        lines.append("- Random perturbation controls: available for score-drop context.")
    lines.extend(
        [
            "",
            payload["claim_boundary"],
            "Negative score_drop is not protective biology; it means the score increased after masking.",
            "",
            "## Explicit Mechanism Path Coverage",
            "",
            "| Top K | Candidates checked | Explicit-path candidates | Coverage rate |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload.get("mechanism_coverage_by_topk", []):
        lines.append(
            f"| {row['top_k']} | {row['candidate_count']} | "
            f"{row['explicit_path_candidate_count']} | {_format_float(row['coverage_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Top Component/Compound Contributions",
            "",
            "| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for index, row in enumerate(payload.get("component_contributions", [])[:10], start=1):
        label = row.get("display_name") or row["feature"]
        lines.append(
            f"| {index} | `{row['feature']}` ({label}) | {row['case_count']} | "
            f"{_format_float(row['mean_score_drop'])} | {_format_float(row['max_score_drop'])} | "
            f"{row['positive_drop_count']} | {row['near_zero_drop_count']} | {row['negative_drop_count']} |"
        )
    lines.extend(
        [
            "",
            "## Top Target Contributions",
            "",
            "| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for index, row in enumerate(payload.get("target_contributions", [])[:10], start=1):
        label = row.get("display_name") or row["feature"]
        lines.append(
            f"| {index} | `{row['feature']}` ({label}) | {row['case_count']} | "
            f"{_format_float(row['mean_score_drop'])} | {_format_float(row['max_score_drop'])} | "
            f"{row['positive_drop_count']} | {row['near_zero_drop_count']} | {row['negative_drop_count']} |"
        )
    lines.extend(
        [
            "",
            "## Top Pathway/Path Contributions",
            "",
            "| Rank | Path features | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for index, row in enumerate(payload.get("pathway_contributions", [])[:10], start=1):
        label = row.get("path_display_features") or row["path_features"]
        lines.append(
            f"| {index} | `{row['path_features']}` ({label}) | {row['case_count']} | "
            f"{_format_float(row['mean_score_drop'])} | {_format_float(row['max_score_drop'])} | "
            f"{row['positive_drop_count']} | {row['near_zero_drop_count']} | {row['negative_drop_count']} |"
        )

    near_zero_cases = [case for case in payload["cases"] if case["sensitivity_class"] == "near_zero"]
    negative_cases = [case for case in payload["cases"] if case["has_negative_score_drop"]]
    lines.extend(["", "## Near-Zero Sensitivity Cases", ""])
    if near_zero_cases:
        for case in near_zero_cases:
            lines.append(f"- `{case['source']}` herb {case['herb_id']} -> ADR {case['adr_id']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Negative score_drop Cases", ""])
    if negative_cases:
        for case in negative_cases:
            lines.append(f"- `{case['source']}` herb {case['herb_id']} -> ADR {case['adr_id']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Random Perturbation Controls", ""])
    random_controls = payload.get("random_control_summary", {})
    if random_controls:
        lines.extend(
            [
                "| Group | Count | Mean drop | Max drop |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for group, row in sorted(random_controls.items()):
            lines.append(
                f"| {group} | {row['count']} | {_format_float(row['mean_score_drop'])} | "
                f"{_format_float(row['max_score_drop'])} |"
            )
    else:
        lines.append("- not available in the current contribution payload")

    lines.extend(["", "## Coverage-Missing Top-Prediction Candidates", ""])
    if payload.get("coverage_missing_candidates"):
        for candidate in payload["coverage_missing_candidates"][:20]:
            rank = candidate.get("rank", "")
            rank_text = f"rank {rank}, " if rank not in (None, "") else ""
            lines.append(
                f"- {rank_text}`{candidate['source']}` herb {candidate['herb_id']} -> "
                f"ADR {candidate['adr_id']}: {candidate['coverage_status']}."
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Case-Level Explanation Examples", ""])
    for case in payload["cases"][:5]:
        top = case.get("top_explanation", {})
        feature = top.get("path_features") or top.get("feature") or ";".join(top.get("features", []))
        if top:
            lines.append(
                f"- `{case['source']}` herb {case['herb_id']} -> ADR {case['adr_id']}: "
                f"top `{feature}` drop {_format_float(top.get('score_drop', 0.0))}; "
                f"class `{case['sensitivity_class']}`."
            )
        else:
            lines.append(
                f"- `{case['source']}` herb {case['herb_id']} -> ADR {case['adr_id']}: "
                "explicit mechanism path selected, but no reusable perturbation row under the current fallback checkpoint."
            )
    if payload.get("checkpoint_is_final_pu_xmsat") and payload.get("candidate_source") == "final_pu_xmsat_top_predictions":
        boundary_text = (
            "This batch uses the final PU-XMSAT top-ranking export and an explicit final "
            "PU-XMSAT checkpoint. Perturbation sensitivity remains local model sensitivity: "
            "it is not causal evidence, not SHAP, not clinical validation, and cannot "
            "upgrade evidence grades."
        )
    else:
        boundary_text = (
            "This batch uses mechanism-supported candidate artifacts rather than final "
            "PU-XMSAT top-ranking export when no final export is present. It also uses "
            "the local predictor checkpoint unless an explicit final PU checkpoint is "
            "supplied. Perturbation sensitivity is not causal evidence, not SHAP, not "
            "clinical validation, and cannot upgrade evidence grades."
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            boundary_text,
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def write_batch_artifacts(
    payload: dict[str, Any],
    output_json: str | Path,
    output_csv: str | Path,
    output_md: str | Path,
) -> None:
    output_json = Path(output_json)
    output_csv = Path(output_csv)
    output_md = Path(output_md)
    for path in (output_json, output_csv, output_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    rows = []
    for group_name, rows_key in (
        ("pathway", "pathway_contributions"),
        ("target", "target_contributions"),
        ("component", "component_contributions"),
    ):
        for row in payload.get(rows_key, []):
            rows.append({"row_type": "aggregate", "contribution_group": group_name, **row})
    for case in payload["cases"]:
        for group_name, rows_key in (
            ("pathway", "pathway_contributions"),
            ("target", "target_contributions"),
            ("component", "component_contributions"),
        ):
            for row in case.get(rows_key, []):
                rows.append(
                    {
                        "row_type": "case",
                        "case_index": case["case_index"],
                        "contribution_group": group_name,
                        "source": case["source"],
                        "herb_id": case["herb_id"],
                        "adr_id": case["adr_id"],
                        "path_features": row.get("path_features", _path_features(row)),
                        "path_display_features": row.get(
                            "path_display_features",
                            _path_display_features(row),
                        ),
                        **row,
                    }
                )
    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    _write_markdown(payload, output_md)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch-level mechanism interpretability")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument(
        "--candidate-pool-top-k",
        type=int,
        default=None,
        help="Search this many top-ranked predictions for mechanism-supported candidates.",
    )
    parser.add_argument(
        "--coverage-cutoffs",
        default="50,100,500,1000,5000",
        help="Comma-separated top-K cutoffs for explicit mechanism path coverage.",
    )
    parser.add_argument("--final-predictions", default="results/pu_xmsat_top_predictions.json")
    parser.add_argument("--case-evidence", default="results/case_evidence_report.json")
    parser.add_argument("--table5", default="results/table5_top15.json")
    parser.add_argument("--explanation", default="results/explanation_case_studies.json")
    parser.add_argument("--structured-mechanism", default="results/mechanism_explanation_layer.json")
    parser.add_argument("--contribution", default="results/contribution_quantification.json")
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--checkpoint-is-final-pu", action="store_true")
    parser.add_argument("--output-json", default="results/batch_mechanism_interpretability.json")
    parser.add_argument("--output-csv", default="results/batch_mechanism_interpretability.csv")
    parser.add_argument("--output-md", default="results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY.md")
    args = parser.parse_args()

    candidates, metadata = select_top_mechanism_candidates(
        final_predictions_payload=_load_json(args.final_predictions),
        case_evidence_payload=_load_json(args.case_evidence),
        table5_payload=_load_json(args.table5),
        explanation_payload=_load_json(args.explanation),
        structured_mechanism_payload=_load_json(args.structured_mechanism),
        top_k=args.top_k,
        candidate_pool_top_k=args.candidate_pool_top_k,
        coverage_cutoffs=tuple(
            int(item.strip())
            for item in str(args.coverage_cutoffs).split(",")
            if item.strip()
        ),
    )
    contribution_payload = _load_json(args.contribution)
    payload = build_batch_payload_from_contributions(
        candidates=candidates,
        candidate_metadata=metadata,
        contribution_payload=contribution_payload,
        checkpoint_path=args.checkpoint or contribution_payload.get("checkpoint_path"),
        checkpoint_is_final_pu=args.checkpoint_is_final_pu,
    )
    write_batch_artifacts(payload, args.output_json, args.output_csv, args.output_md)
    print(
        json.dumps(
            {
                "quantified_case_count": payload["summary"]["quantified_case_count"],
                "candidate_source": payload["candidate_source"],
                "checkpoint_is_final_pu_xmsat": payload["checkpoint_is_final_pu_xmsat"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
