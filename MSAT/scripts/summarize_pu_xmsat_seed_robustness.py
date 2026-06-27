from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev


DEFAULT_METRICS = ("auc", "auprc", "f1", "mcc")


def _baseline_mean(payload: dict, metric: str) -> float:
    if "overall_metrics" in payload:
        return float(payload["overall_metrics"][metric]["mean"])
    if "mean_metrics" in payload:
        return float(payload["mean_metrics"][metric])
    raise ValueError(f"baseline does not contain metric {metric!r}")


def _fold_metric_values(payload: dict, metric: str) -> list[float]:
    values = [
        float(row["test_metrics"][metric])
        for row in payload.get("fold_results", [])
        if metric in row.get("test_metrics", {})
    ]
    if values:
        return values
    if "mean_metrics" in payload and metric in payload["mean_metrics"]:
        return [float(payload["mean_metrics"][metric])]
    raise ValueError(f"run does not contain metric {metric!r}")


def summarize_runs(
    baseline: dict,
    runs: list[tuple[str, dict]],
    metrics: tuple[str, ...] = DEFAULT_METRICS,
    baseline_label: str = "reproduced MSAT baseline",
) -> dict:
    if not runs:
        raise ValueError("at least one run is required")

    run_summaries = []
    fold_count = None
    for label, payload in runs:
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
        run_summaries.append({"label": label, "metrics": metric_summary})

    seed_spread = {}
    for metric in metrics:
        means = [row["metrics"][metric]["mean"] for row in run_summaries]
        seed_spread[metric] = {
            "min": float(min(means)),
            "max": float(max(means)),
            "range": float(max(means) - min(means)),
        }

    return {
        "baseline_label": baseline_label,
        "run_count": len(run_summaries),
        "fold_count": int(fold_count or 0),
        "runs": run_summaries,
        "seed_spread": seed_spread,
        "interpretation": (
            "Use this summary to describe whether the same PU-XMSAT setting remains "
            "stable across seeds. Small seed-spread values support robustness, but "
            "do not replace protocol checks or paired fold-level comparisons."
        ),
    }


def csv_rows(summary: dict) -> list[dict[str, str]]:
    rows = []
    for run in summary["runs"]:
        for metric, values in run["metrics"].items():
            rows.append(
                {
                    "run_label": run["label"],
                    "metric": metric,
                    "mean": f"{values['mean']:.6f}",
                    "std": f"{values['std']:.6f}",
                    "delta_vs_baseline": f"{values['delta_vs_baseline']:+.6f}",
                    "seed_spread_range": f"{summary['seed_spread'][metric]['range']:.6f}",
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


def _parse_run_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must use LABEL=PATH")
    label, path = value.rsplit("=", 1)
    if not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("--run must use non-empty LABEL=PATH")
    return label.strip(), Path(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument("--baseline-label", default="reproduced MSAT baseline")
    parser.add_argument("--run", action="append", type=_parse_run_arg, required=True)
    parser.add_argument("--output-json", default="results/pu_xmsat_seed_robustness_summary.json")
    parser.add_argument("--output-csv", default="results/pu_xmsat_seed_robustness_summary.csv")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    runs = [
        (label, json.loads(path.read_text()))
        for label, path in args.run
    ]
    summary = summarize_runs(
        baseline=baseline,
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
