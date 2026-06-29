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
    "negative_drop_count",
]

CLAIM_BOUNDARY = "These are perturbation sensitivity aggregates, not causal or SHAP attributions."


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
    positive = [value for value in drops if value > 0]
    negative = [value for value in drops if value < 0]
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
    positive_node_count = 0
    positive_path_count = 0

    for case_index, case in enumerate(payload.get("cases", []), start=1):
        case_key = _case_key(case_index, case)
        for row in case.get("node_contributions", []):
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
            if score_drop > 0:
                positive_node_count += 1

        for row in case.get("path_contributions", []):
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
            if score_drop > 0:
                positive_path_count += 1

    top_nodes = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in node_buckets.values()],
        "feature",
    )[:top_k]
    top_paths = _sort_aggregates(
        [_finalize_bucket(bucket) for bucket in path_buckets.values()],
        "path_features",
    )[:top_k]

    return {
        "experiment": "contribution_aggregate_summary",
        "source_experiment": payload.get("experiment", "unknown"),
        "checkpoint_path": payload.get("checkpoint_path", "unknown"),
        "checkpoint_context": payload.get("checkpoint_context", "not specified"),
        "source_claim_boundary": payload.get("claim_boundary", ""),
        "claim_boundary": CLAIM_BOUNDARY,
        "case_count": len(payload.get("cases", [])),
        "positive_node_count": positive_node_count,
        "positive_path_count": positive_path_count,
        "top_k": top_k,
        "top_nodes": top_nodes,
        "top_paths": top_paths,
    }


def _write_csv(path: Path, summary: dict) -> None:
    rows = []
    rows.extend(summary.get("top_paths", []))
    rows.extend(summary.get("top_nodes", []))
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def _format_float(value: Any) -> str:
    return f"{float(value):.6f}"


def _markdown_table(rows: list[dict[str, Any]], aggregate_type: str) -> list[str]:
    if aggregate_type == "path":
        lines = [
            "| Rank | Path features | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for index, row in enumerate(rows, start=1):
            lines.append(
                f"| {index} | `{row['path_features']}` | {row['case_count']} | "
                f"{row['occurrence_count']} | {_format_float(row['mean_score_drop'])} | "
                f"{_format_float(row['max_score_drop'])} | {row['positive_drop_count']} | "
                f"{row['negative_drop_count']} |"
            )
        return lines

    lines = [
        "| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f"| {index} | `{row['feature']}` | `{row['node_type']}` | {row['case_count']} | "
            f"{row['occurrence_count']} | {_format_float(row['mean_score_drop'])} | "
            f"{_format_float(row['max_score_drop'])} | {row['positive_drop_count']} | "
            f"{row['negative_drop_count']} |"
        )
    return lines


def _write_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# PU-XMSAT Contribution Aggregate Summary",
        "",
        "This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.",
        "",
        f"- Cases summarized: {summary['case_count']}",
        f"- Positive node perturbation rows: {summary['positive_node_count']}",
        f"- Positive path perturbation rows: {summary['positive_path_count']}",
        f"- Checkpoint: `{summary.get('checkpoint_path', 'unknown')}`",
        f"- Checkpoint context: {summary.get('checkpoint_context', 'not specified')}",
        "",
        summary["claim_boundary"],
        "They are not causal effects, not SHAP-equivalent values, and not external clinical validation.",
        "",
        "## Top Path Aggregates",
        "",
    ]
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
