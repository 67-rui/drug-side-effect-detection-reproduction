from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean

from scipy import stats


DEFAULT_METRICS = ("auc", "auprc", "f1", "mcc")


def _fold_metric_values(payload: dict, metric: str) -> list[float]:
    fold_results = payload.get("fold_results", [])
    values = []
    for row in fold_results:
        metrics = row.get("test_metrics", {})
        if metric not in metrics:
            raise ValueError(f"missing metric {metric!r} in fold {row.get('fold')}")
        values.append(float(metrics[metric]))
    if not values:
        raise ValueError(f"no fold values found for metric {metric!r}")
    return values


def _paired_ttest(pu_values: list[float], baseline_values: list[float]) -> tuple[float | None, float | None]:
    result = stats.ttest_rel(pu_values, baseline_values)
    statistic = float(result.statistic)
    p_value = float(result.pvalue)
    if math.isnan(statistic) or math.isnan(p_value):
        return None, None
    return statistic, p_value


def build_comparison(
    baseline: dict,
    pu: dict,
    metrics: tuple[str, ...] = DEFAULT_METRICS,
    baseline_label: str = "reproduced MSAT baseline",
    pu_label: str = "PU-XMSAT",
) -> dict:
    rows = []
    fold_count = None
    for metric in metrics:
        baseline_values = _fold_metric_values(baseline, metric)
        pu_values = _fold_metric_values(pu, metric)
        if len(baseline_values) != len(pu_values):
            raise ValueError(
                f"fold count mismatch for {metric}: "
                f"baseline={len(baseline_values)}, pu={len(pu_values)}"
            )
        if fold_count is None:
            fold_count = len(pu_values)
        elif fold_count != len(pu_values):
            raise ValueError("metric fold counts are inconsistent")

        deltas = [pu_value - baseline_value for pu_value, baseline_value in zip(pu_values, baseline_values)]
        statistic, p_value = _paired_ttest(pu_values, baseline_values)
        rows.append(
            {
                "metric": metric,
                "baseline_mean": float(mean(baseline_values)),
                "pu_mean": float(mean(pu_values)),
                "mean_delta": float(mean(deltas)),
                "pu_wins": int(sum(delta > 0 for delta in deltas)),
                "pu_losses": int(sum(delta < 0 for delta in deltas)),
                "ties": int(sum(delta == 0 for delta in deltas)),
                "paired_ttest_statistic": statistic,
                "paired_ttest_p": p_value,
                "baseline_values": baseline_values,
                "pu_values": pu_values,
                "deltas": deltas,
            }
        )

    return {
        "fold_count": int(fold_count or 0),
        "baseline_label": baseline_label,
        "pu_label": pu_label,
        "metrics": rows,
        "interpretation": (
            f"Use paired fold-level statistics to describe {pu_label} relative to "
            f"{baseline_label}. Small non-significant mean deltas should be reported "
            "cautiously, not as definitive superiority."
        ),
    }


def _format_float(value: float | None, signed: bool = False) -> str:
    if value is None:
        return ""
    prefix = "+" if signed and value >= 0 else ""
    return f"{prefix}{value:.6f}"


def csv_rows(comparison: dict) -> list[dict[str, str]]:
    rows = []
    for row in comparison["metrics"]:
        rows.append(
            {
                "metric": row["metric"],
                "baseline_mean": _format_float(row["baseline_mean"]),
                "pu_mean": _format_float(row["pu_mean"]),
                "mean_delta": _format_float(row["mean_delta"], signed=True),
                "pu_wins": str(row["pu_wins"]),
                "pu_losses": str(row["pu_losses"]),
                "ties": str(row["ties"]),
                "paired_ttest_p": _format_float(row.get("paired_ttest_p")),
            }
        )
    return rows


def write_csv(path: str | Path, comparison: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = csv_rows(comparison)
    if not rows:
        out.write_text("")
        return
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument(
        "--pu",
        default="results/pu_training_summary_10fold_random_200e_66015p_valf1_random50k.json",
    )
    parser.add_argument("--output-json", default="results/pu_xmsat_baseline_comparison.json")
    parser.add_argument("--output-csv", default="results/pu_xmsat_baseline_comparison.csv")
    parser.add_argument("--baseline-label", default="reproduced MSAT baseline")
    parser.add_argument("--pu-label", default="PU-XMSAT")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    pu = json.loads(Path(args.pu).read_text())
    comparison = build_comparison(
        baseline,
        pu,
        baseline_label=args.baseline_label,
        pu_label=args.pu_label,
    )

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_csv, comparison)
    print(f"Wrote {out_json} and {args.output_csv}")


if __name__ == "__main__":
    main()
