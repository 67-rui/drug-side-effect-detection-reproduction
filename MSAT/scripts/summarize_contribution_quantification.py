from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


CSV_FIELDS = [
    "aggregate_type",
    "feature",
    "node_type",
    "node_id",
    "path_features",
    "case_count",
    "occurrence_count",
    "mean_score_drop",
    "max_score_drop",
    "positive_drop_count",
    "near_zero_drop_count",
    "negative_drop_count",
]

CLAIM_BOUNDARY = "These are perturbation sensitivity aggregates, not causal or SHAP attributions."
NEAR_ZERO_THRESHOLD = 1e-4


def load_contribution_payload(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def _rounded(value: float) -> float:
    return round(float(value), 10)


def _case_key(case_index: int, case: dict[str, Any]) -> str:
    return f"{case_index}:{case.get('source', 'unknown')}:{case.get('herb_id')}:{case.get('adr_id')}"


def _path_features(row: dict[str, Any]) -> str:
    features = row.get("features")
    if isinstance(features, list):
        return ";".join(str(feature) for feature in features)
    if features:
        return str(features)
    return str(row.get("path_features", ""))


def _empty_bucket(**metadata: Any) -> dict[str, Any]:
    return {
        **metadata,
        "case_keys": set(),
        "score_drops": [],
    }


def _finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    drops = [float(value) for value in bucket["score_drops"]]
    positive = [value for value in drops if value > NEAR_ZERO_THRESHOLD]
    near_zero = [value for value in drops if abs(value) <= NEAR_ZERO_THRESHOLD]
    negative = [value for value in drops if value < -NEAR_ZERO_THRESHOLD]
    output = {
        key: value
        for key, value in bucket.items()
        if key not in {"case_keys", "score_drops"}
    }
    output.update(
        {
            "case_count": len(bucket["case_keys"]),
            "occurrence_count": len(drops),
            "mean_score_drop": _rounded(mean(drops)) if drops else 0.0,
            "max_score_drop": _rounded(max(drops)) if drops else 0.0,
            "positive_drop_count": len(positive),
            "near_zero_drop_count": len(near_zero),
            "negative_drop_count": len(negative),
        }
    )
    return output


def _sort_aggregates(rows: list[dict[str, Any]], key_field: str) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -float(row["mean_score_drop"]),
            -float(row["max_score_drop"]),
            str(row.get(key_field, "")),
        ),
    )


def summarize_contributions(payload: dict, top_k: int = 10) -> dict:
    node_buckets: dict[tuple[str, str, str], dict[str, Any]] = {}
    path_buckets: dict[str, dict[str, Any]] = {}
    component_buckets: dict[tuple[str, str, str], dict[str, Any]] = {}
    target_buckets: dict[tuple[str, str, str], dict[str, Any]] = {}
    pathway_buckets: dict[str, dict[str, Any]] = {}
    positive_node_count = 0
    near_zero_node_count = 0
    negative_node_count = 0
    positive_path_count = 0
    near_zero_path_count = 0
    negative_path_count = 0
    positive_component_count = 0
    near_zero_component_count = 0
    negative_component_count = 0
    positive_target_count = 0
    near_zero_target_count = 0
    negative_target_count = 0
    positive_pathway_count = 0
    near_zero_pathway_count = 0
    negative_pathway_count = 0

    for case_index, case in enumerate(payload.get("cases", []), start=1):
        case_key = _case_key(case_index, case)

        node_rows = list(case.get("node_contributions", []))
        if not node_rows and (
            case.get("component_contributions") or case.get("target_contributions")
        ):
            node_rows = list(case.get("component_contributions", [])) + list(
                case.get("target_contributions", [])
            )

        for row in node_rows:
            feature = str(row.get("feature", ""))
            node_type = str(row.get("node_type", ""))
            node_id = str(row.get("node_id", ""))
            key = (feature, node_type, node_id)
            bucket = node_buckets.setdefault(
                key,
                _empty_bucket(
                    aggregate_type="node",
                    feature=feature,
                    node_type=node_type,
                    node_id=node_id,
                    path_features="",
                ),
            )
            score_drop = float(row.get("score_drop", 0.0))
            bucket["case_keys"].add(case_key)
            bucket["score_drops"].append(score_drop)
            if score_drop > NEAR_ZERO_THRESHOLD:
                positive_node_count += 1
            elif score_drop < -NEAR_ZERO_THRESHOLD:
                negative_node_count += 1
            else:
                near_zero_node_count += 1

        for group_name, group_buckets in (
            ("component", component_buckets),
            ("target", target_buckets),
        ):
            rows_key = f"{group_name}_contributions"
            for row in case.get(rows_key, []):
                feature = str(row.get("feature", ""))
                node_type = str(row.get("node_type", group_name))
                node_id = str(row.get("node_id", ""))
                bucket = group_buckets.setdefault(
                    (feature, node_type, node_id),
                    _empty_bucket(
                        aggregate_type=group_name,
                        feature=feature,
                        node_type=node_type,
                        node_id=node_id,
                        path_features="",
                    ),
                )
                score_drop = float(row.get("score_drop", 0.0))
                bucket["case_keys"].add(case_key)
                bucket["score_drops"].append(score_drop)
                if group_name == "component":
                    if score_drop > NEAR_ZERO_THRESHOLD:
                        positive_component_count += 1
                    elif score_drop < -NEAR_ZERO_THRESHOLD:
                        negative_component_count += 1
                    else:
                        near_zero_component_count += 1
                else:
                    if score_drop > NEAR_ZERO_THRESHOLD:
                        positive_target_count += 1
                    elif score_drop < -NEAR_ZERO_THRESHOLD:
                        negative_target_count += 1
                    else:
                        near_zero_target_count += 1

        path_rows = list(case.get("path_contributions", []))
        if not path_rows and case.get("pathway_contributions"):
            path_rows = list(case.get("pathway_contributions", []))

        for row in path_rows:
            path_features = _path_features(row)
            bucket = path_buckets.setdefault(
                path_features,
                _empty_bucket(
                    aggregate_type="path",
                    feature=str(row.get("feature", "")),
                    node_type="",
                    node_id="",
                    path_features=path_features,
                ),
            )
            score_drop = float(row.get("score_drop", 0.0))
            bucket["case_keys"].add(case_key)
            bucket["score_drops"].append(score_drop)
            if score_drop > NEAR_ZERO_THRESHOLD:
                positive_path_count += 1
            elif score_drop < -NEAR_ZERO_THRESHOLD:
                negative_path_count += 1
            else:
                near_zero_path_count += 1

        for row in case.get("pathway_contributions", []):
            path_features = _path_features(row)
            bucket = pathway_buckets.setdefault(
                path_features,
                _empty_bucket(
                    aggregate_type="pathway",
                    feature=str(row.get("feature", "")),
                    node_type="",
                    node_id="",
                    path_features=path_features,
                ),
            )
            score_drop = float(row.get("score_drop", 0.0))
            bucket["case_keys"].add(case_key)
            bucket["score_drops"].append(score_drop)
            if score_drop > NEAR_ZERO_THRESHOLD:
                positive_pathway_count += 1
            elif score_drop < -NEAR_ZERO_THRESHOLD:
                negative_pathway_count += 1
            else:
                near_zero_pathway_count += 1

    top_nodes = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in node_buckets.values()],
        "feature",
    )[:top_k]
    top_paths = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in path_buckets.values()],
        "path_features",
    )[:top_k]
    top_components = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in component_buckets.values()],
        "feature",
    )[:top_k]
    top_targets = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in target_buckets.values()],
        "feature",
    )[:top_k]
    top_pathways = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in pathway_buckets.values()],
        "path_features",
    )[:top_k]

    return {
        "experiment": "contribution_aggregate_summary",
        "source_experiment": payload.get("experiment", "unknown"),
        "checkpoint_path": payload.get("checkpoint_path", "unknown"),
        "checkpoint_context": payload.get("checkpoint_context", "not specified"),
        "candidate_source": payload.get("candidate_source", ""),
        "candidate_source_note": payload.get("candidate_source_note", ""),
        "source_claim_boundary": payload.get("claim_boundary", ""),
        "claim_boundary": CLAIM_BOUNDARY,
        "case_count": len(payload.get("cases", [])),
        "quantified_case_count": payload.get("summary", {}).get(
            "quantified_case_count",
            len(payload.get("cases", [])),
        ),
        "candidate_count": payload.get("summary", {}).get(
            "candidate_count",
            len(payload.get("cases", [])),
        ),
        "positive_node_count": positive_node_count,
        "near_zero_node_count": near_zero_node_count,
        "negative_node_count": negative_node_count,
        "positive_path_count": positive_path_count,
        "near_zero_path_count": near_zero_path_count,
        "negative_path_count": negative_path_count,
        "positive_component_count": positive_component_count,
        "near_zero_component_count": near_zero_component_count,
        "negative_component_count": negative_component_count,
        "positive_target_count": positive_target_count,
        "near_zero_target_count": near_zero_target_count,
        "negative_target_count": negative_target_count,
        "positive_pathway_count": positive_pathway_count,
        "near_zero_pathway_count": near_zero_pathway_count,
        "negative_pathway_count": negative_pathway_count,
        "fewer_than_top_k_reason": payload.get("summary", {}).get("fewer_than_top_k_reason", ""),
        "top_k": top_k,
        "top_nodes": top_nodes,
        "top_paths": top_paths,
        "top_components": top_components,
        "top_targets": top_targets,
        "top_pathways": top_pathways,
    }


def _write_csv(path: Path, summary: dict) -> None:
    rows = []
    rows.extend(summary.get("top_pathways", []))
    rows.extend(summary.get("top_targets", []))
    rows.extend(summary.get("top_components", []))
    rows.extend(summary.get("top_paths", []))
    rows.extend(summary.get("top_nodes", []))
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def _format_float(value: Any) -> str:
    return f"{float(value):.6f}"


def _markdown_table(rows: list[dict[str, Any]], aggregate_type: str) -> list[str]:
    if aggregate_type == "path":
        lines = [
            "| Rank | Path features | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for index, row in enumerate(rows, start=1):
            lines.append(
                f"| {index} | `{row['path_features']}` | {row['case_count']} | "
                f"{row['occurrence_count']} | {_format_float(row['mean_score_drop'])} | "
                f"{_format_float(row['max_score_drop'])} | {row['positive_drop_count']} | "
                f"{row.get('near_zero_drop_count', 0)} | {row['negative_drop_count']} |"
            )
        return lines

    lines = [
        "| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f"| {index} | `{row['feature']}` | `{row['node_type']}` | {row['case_count']} | "
            f"{row['occurrence_count']} | {_format_float(row['mean_score_drop'])} | "
            f"{_format_float(row['max_score_drop'])} | {row['positive_drop_count']} | "
            f"{row.get('near_zero_drop_count', 0)} | {row['negative_drop_count']} |"
        )
    return lines


def _write_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# PU-XMSAT Contribution Aggregate Summary",
        "",
        "This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.",
        "",
        f"- Batch candidates summarized: {summary.get('candidate_count', summary['case_count'])}",
        f"- Perturbation-quantified cases: {summary.get('quantified_case_count', summary['case_count'])}",
        f"- Positive node perturbation rows: {summary['positive_node_count']}",
        f"- Near-zero node perturbation rows: {summary.get('near_zero_node_count', 0)}",
        f"- Negative node perturbation rows: {summary.get('negative_node_count', 0)}",
        f"- Positive path perturbation rows: {summary['positive_path_count']}",
        f"- Near-zero path perturbation rows: {summary.get('near_zero_path_count', 0)}",
        f"- Negative path perturbation rows: {summary.get('negative_path_count', 0)}",
        f"- Checkpoint: `{summary.get('checkpoint_path', 'unknown')}`",
        f"- Checkpoint context: {summary.get('checkpoint_context', 'not specified')}",
        f"- Candidate source: `{summary.get('candidate_source') or 'not recorded'}`",
        "",
        summary["claim_boundary"],
        "They are not causal effects, not SHAP-equivalent values, and not external clinical validation.",
        "",
    ]
    if summary.get("fewer_than_top_k_reason"):
        lines.extend([f"- Fewer than requested top-K: {summary['fewer_than_top_k_reason']}", ""])
    if summary.get("top_pathways") or summary.get("top_components") or summary.get("top_targets"):
        lines.extend(["## Top Pathway Aggregates", ""])
        lines.extend(_markdown_table(summary.get("top_pathways", []), "path"))
        lines.extend(["", "## Top Target Aggregates", ""])
        lines.extend(_markdown_table(summary.get("top_targets", []), "node"))
        lines.extend(["", "## Top Component Aggregates", ""])
        lines.extend(_markdown_table(summary.get("top_components", []), "node"))
        lines.extend(["", "## Legacy Top Path Aggregates", ""])
    else:
        lines.extend(["## Top Path Aggregates", ""])
    lines.extend(_markdown_table(summary.get("top_paths", []), "path"))
    lines.extend(["", "## Top Node Aggregates", ""])
    lines.extend(_markdown_table(summary.get("top_nodes", []), "node"))
    lines.append("")
    path.write_text("\n".join(lines))


def write_summary_artifacts(
    summary: dict,
    output_json: Path,
    output_csv: Path,
    output_md: Path,
) -> None:
    for path in (output_json, output_csv, output_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    _write_csv(output_csv, summary)
    _write_markdown(output_md, summary)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize PU-XMSAT contribution perturbation outputs")
    parser.add_argument("--input", default="results/contribution_quantification.json")
    parser.add_argument("--output-json", default="results/contribution_aggregate_summary.json")
    parser.add_argument("--output-csv", default="results/contribution_aggregate_summary.csv")
    parser.add_argument("--output-md", default="results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    payload = load_contribution_payload(args.input)
    summary = summarize_contributions(payload, top_k=args.top_k)
    write_summary_artifacts(
        summary,
        output_json=Path(args.output_json),
        output_csv=Path(args.output_csv),
        output_md=Path(args.output_md),
    )
    print("Wrote contribution aggregate summary")


if __name__ == "__main__":
    main()
