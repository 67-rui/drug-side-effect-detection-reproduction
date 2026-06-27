from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev


DEFAULT_METRICS = ("auc", "auprc", "f1", "mcc")


def _baseline_mean(payload: dict, metric: str) -> float:
    return float(payload["overall_metrics"][metric]["mean"])


def _fold_metric_values(payload: dict, metric: str) -> list[float]:
    values = [
        float(row["test_metrics"][metric])
        for row in payload.get("fold_results", [])
        if metric in row.get("test_metrics", {})
    ]
    if not values:
        raise ValueError(f"run does not contain metric {metric!r}")
    return values


def summarize_weight_runs(
    baseline: dict,
    reference_label: str,
    runs: list[tuple[str, float, float, dict]],
    metrics: tuple[str, ...] = DEFAULT_METRICS,
    baseline_label: str = "reproduced MSAT baseline",
) -> dict:
    if not runs:
        raise ValueError("at least one run is required")

    run_summaries = []
    fold_count = None
    reference_metrics = None

    for label, unlabeled_weight, reliable_negative_weight, payload in runs:
        metric_summary = {}
        for metric in metrics:
            values = _fold_metric_values(payload, metric)
            if fold_count is None:
                fold_count = len(values)
            elif fold_count != len(values):
                raise ValueError("run fold counts are inconsistent")
            metric_mean = float(mean(values))
            metric_summary[metric] = {
                "mean": metric_mean,
                "std": float(stdev(values)) if len(values) > 1 else 0.0,
                "delta_vs_baseline": metric_mean - _baseline_mean(baseline, metric),
            }
        row = {
            "label": label,
            "unlabeled_weight": float(unlabeled_weight),
            "reliable_negative_weight": float(reliable_negative_weight),
            "metrics": metric_summary,
        }
        run_summaries.append(row)
        if label == reference_label:
            reference_metrics = metric_summary

    if reference_metrics is None:
        raise ValueError(f"reference label not found: {reference_label!r}")

    for row in run_summaries:
        for metric in metrics:
            row["metrics"][metric]["delta_vs_reference"] = (
                row["metrics"][metric]["mean"] - reference_metrics[metric]["mean"]
            )

    return {
        "baseline_label": baseline_label,
        "reference_label": reference_label,
        "run_count": len(run_summaries),
        "fold_count": int(fold_count or 0),
        "runs": run_summaries,
        "interpretation": (
            "Use this summary to describe whether the PU-XMSAT full-positive hybrid "
            "result is sensitive to PU sample weights. Prefer settings that preserve "
            "baseline gains while keeping thresholded metrics stable."
        ),
    }


def csv_rows(summary: dict) -> list[dict[str, str]]:
    rows = []
    for run in summary["runs"]:
        for metric, values in run["metrics"].items():
            rows.append(
                {
                    "run_label": run["label"],
                    "unlabeled_weight": f"{run['unlabeled_weight']:.3f}",
                    "reliable_negative_weight": f"{run['reliable_negative_weight']:.3f}",
                    "metric": metric,
                    "mean": f"{values['mean']:.6f}",
                    "std": f"{values['std']:.6f}",
                    "delta_vs_baseline": f"{values['delta_vs_baseline']:+.6f}",
                    "delta_vs_reference": f"{values['delta_vs_reference']:+.6f}",
                }
            )
    return rows


def write_csv(path: str | Path, summary: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = csv_rows(summary)
    if not rows:
        out.write_text("")
        return
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _parse_run_arg(value: str) -> tuple[str, float, float, Path]:
    parts = value.split("=", 3)
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--run must use LABEL=UNLABELED_WEIGHT=RN_WEIGHT=PATH")
    label, unlabeled_weight, reliable_negative_weight, path = parts
    if not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("--run must use non-empty LABEL and PATH")
    return label.strip(), float(unlabeled_weight), float(reliable_negative_weight), Path(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument("--baseline-label", default="reproduced MSAT baseline")
    parser.add_argument("--reference-label", required=True)
    parser.add_argument("--run", action="append", type=_parse_run_arg, required=True)
    parser.add_argument("--output-json", default="results/pu_xmsat_weight_sensitivity_summary.json")
    parser.add_argument("--output-csv", default="results/pu_xmsat_weight_sensitivity_summary.csv")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    runs = [
        (label, unlabeled_weight, reliable_negative_weight, json.loads(path.read_text()))
        for label, unlabeled_weight, reliable_negative_weight, path in args.run
    ]
    summary = summarize_weight_runs(
        baseline=baseline,
        reference_label=args.reference_label,
        runs=runs,
        baseline_label=args.baseline_label,
    )

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_csv, summary)
    print(f"Wrote {out_json} and {args.output_csv}")


if __name__ == "__main__":
    main()
