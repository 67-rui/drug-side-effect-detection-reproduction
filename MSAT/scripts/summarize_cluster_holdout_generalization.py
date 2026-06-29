from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


METRICS = ("auc", "auprc", "f1", "mcc")
TINY_HOLDOUT_CLUSTER_THRESHOLD = 5
CLAIM_BOUNDARY = (
    "Cluster-held-out evaluation probes generalization to held-out herb/CMM clusters; "
    "it is not external clinical validation, causal transportability, or evidence that "
    "all unobserved pairs are true negatives."
)


def summarize_cluster_holdout_run(payload: dict[str, Any]) -> dict[str, Any]:
    fold_rows = []
    metric_values = {metric: [] for metric in METRICS}
    for result in payload.get("fold_results", []):
        protocol = result.get("cluster_protocol") or {}
        metrics = result.get("test_metrics") or {}
        for metric in METRICS:
            if metric in metrics:
                metric_values[metric].append(float(metrics[metric]))
        fold_rows.append(
            {
                "fold": result.get("fold"),
                "holdout_cluster": protocol.get("holdout_cluster"),
                "heldout_herb_count": protocol.get("heldout_herb_count", 0),
                "test_positive_count": protocol.get("test_positive_count", 0),
                "hidden_eval_positive_pair_count": protocol.get(
                    "hidden_eval_positive_pair_count",
                    0,
                ),
                "excluded_herb_count": (result.get("pu_pair_counts") or {}).get(
                    "excluded_herb_count",
                    0,
                ),
                "metrics": {metric: metrics.get(metric) for metric in METRICS},
            }
        )
    mean_metrics = {
        metric: float(mean(values)) if values else None
        for metric, values in metric_values.items()
    }
    heldout_counts = [int(row["heldout_herb_count"]) for row in fold_rows]
    tiny_count = sum(
        1 for count in heldout_counts if count < TINY_HOLDOUT_CLUSTER_THRESHOLD
    )
    cluster_balance = {
        "min_heldout_herb_count": min(heldout_counts) if heldout_counts else 0,
        "max_heldout_herb_count": max(heldout_counts) if heldout_counts else 0,
        "tiny_holdout_cluster_threshold": TINY_HOLDOUT_CLUSTER_THRESHOLD,
        "tiny_holdout_cluster_count": tiny_count,
    }
    interpretation_caveats = []
    if tiny_count:
        interpretation_caveats.append(
            f"{tiny_count} tiny heldout clusters have fewer than "
            f"{TINY_HOLDOUT_CLUSTER_THRESHOLD} herbs; macro mean metrics should be "
            "read together with fold-level cluster sizes."
        )
    if mean_metrics.get("f1") is not None and mean_metrics["f1"] < 0.3:
        interpretation_caveats.append(
            "Thresholded F1 is low under cluster-held-out evaluation; this supports a "
            "harder generalization setting rather than a simple success claim."
        )
    return {
        "experiment": "pu_xmsat_cluster_holdout_generalization",
        "split_mode": payload.get("split_mode"),
        "fold_count": len(fold_rows),
        "mean_metrics": mean_metrics,
        "cluster_balance": cluster_balance,
        "interpretation_caveats": interpretation_caveats,
        "folds": fold_rows,
        "leakage_controls": {
            "heldout_herbs_filtered_from_pu_training": all(
                int(row.get("excluded_herb_count") or 0) == int(row.get("heldout_herb_count") or 0)
                for row in fold_rows
            ),
            "eval_positive_edges_hidden": all(
                int(row.get("hidden_eval_positive_pair_count") or 0)
                >= int(row.get("test_positive_count") or 0)
                for row in fold_rows
            ),
            "mechanism_edges_retained": True,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _fmt(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.6f}"


def write_summary(summary: dict[str, Any], output_json: str | Path, output_md: str | Path) -> None:
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# PU-XMSAT Cluster-Held-Out Generalization",
        "",
        f"- Fold count: {summary['fold_count']}",
        f"- Claim boundary: {summary['claim_boundary']}",
        f"- Heldout herbs filtered from PU training: {'yes' if summary['leakage_controls']['heldout_herbs_filtered_from_pu_training'] else 'no'}",
        f"- Eval positive CMM-ADR edges hidden: {'yes' if summary['leakage_controls']['eval_positive_edges_hidden'] else 'no'}",
        f"- Mechanism edges retained: {'yes' if summary['leakage_controls']['mechanism_edges_retained'] else 'no'}",
        f"- Tiny heldout clusters (<{summary['cluster_balance']['tiny_holdout_cluster_threshold']} herbs): {summary['cluster_balance']['tiny_holdout_cluster_count']}",
        f"- Heldout herb count range: {summary['cluster_balance']['min_heldout_herb_count']} to {summary['cluster_balance']['max_heldout_herb_count']}",
        "",
    ]
    if summary.get("interpretation_caveats"):
        lines.extend(["## Interpretation Caveats", ""])
        for caveat in summary["interpretation_caveats"]:
            lines.append(f"- {caveat}")
        lines.append("")
    lines.extend([
        "## Mean Metrics",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
    ])
    for metric in METRICS:
        lines.append(f"| {metric.upper()} | {_fmt(summary['mean_metrics'].get(metric))} |")
    lines.extend(
        [
            "",
            "## Fold Summary",
            "",
            "| Fold | Holdout cluster | Heldout herbs | Test positives | Hidden eval positives | AUC | AUPRC | F1 | MCC |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary["folds"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row.get('fold')} | {row.get('holdout_cluster')} | {row['heldout_herb_count']} | "
            f"{row['test_positive_count']} | {row['hidden_eval_positive_pair_count']} | "
            f"{_fmt(metrics.get('auc'))} | {_fmt(metrics.get('auprc'))} | "
            f"{_fmt(metrics.get('f1'))} | {_fmt(metrics.get('mcc'))} |"
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/cluster_holdout_pilot.json")
    parser.add_argument("--output-json", default="results/cluster_holdout_generalization_summary.json")
    parser.add_argument("--output-md", default="results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    summary = summarize_cluster_holdout_run(payload)
    write_summary(summary, args.output_json, args.output_md)
    print(f"Wrote {args.output_json} and {args.output_md}")


if __name__ == "__main__":
    main()
