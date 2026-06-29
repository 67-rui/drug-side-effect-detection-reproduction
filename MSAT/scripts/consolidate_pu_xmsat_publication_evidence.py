from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any


METRICS = ("auc", "auprc", "f1", "mcc")
CLAIM_BOUNDARY = (
    "PU-XMSAT evidence supports incomplete-label mitigation and risk-prioritization "
    "under the reproduced MSAT protocol; it is not causal validation, clinical "
    "confirmation, or proof that unobserved pairs are true negatives."
)


def _baseline_metric(payload: dict[str, Any], metric: str) -> float:
    if "overall_metrics" in payload:
        return float(payload["overall_metrics"][metric]["mean"])
    if "mean_metrics" in payload:
        return float(payload["mean_metrics"][metric])
    raise ValueError(f"baseline payload missing metric: {metric}")


def _metric_values(payload: dict[str, Any], metric: str) -> list[float]:
    values = [
        float(row["test_metrics"][metric])
        for row in payload.get("fold_results", [])
        if metric in row.get("test_metrics", {})
    ]
    if values:
        return values
    if metric in payload.get("mean_metrics", {}):
        return [float(payload["mean_metrics"][metric])]
    raise ValueError(f"run payload missing metric: {metric}")


def _summarize_run(label: str, payload: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    metrics = {}
    for metric in METRICS:
        values = _metric_values(payload, metric)
        metric_mean = float(mean(values))
        metrics[metric] = {
            "mean": metric_mean,
            "std": float(stdev(values)) if len(values) > 1 else 0.0,
            "fold_count": len(values),
            "delta_vs_baseline": metric_mean - _baseline_metric(baseline, metric),
        }
    return {"label": label, "metrics": metrics}


def _seed_spread(seed_robustness: dict[str, Any]) -> dict[str, Any]:
    spread = seed_robustness.get("seed_spread") or {}
    ranges = {
        metric: float(values.get("range", 0.0))
        for metric, values in spread.items()
        if isinstance(values, dict)
    }
    return {
        "metrics": ranges,
        "max_seed_spread": max(ranges.values(), default=0.0),
    }


def build_publication_evidence_summary(
    baseline: dict[str, Any],
    main_runs: list[tuple[str, dict[str, Any]]],
    ablation_runs: list[tuple[str, dict[str, Any]]],
    seed_robustness: dict[str, Any],
    weight_sensitivity: dict[str, Any],
) -> dict[str, Any]:
    main = [_summarize_run(label, payload, baseline) for label, payload in main_runs]
    ablation = [_summarize_run(label, payload, baseline) for label, payload in ablation_runs]
    baseline_metrics = {metric: _baseline_metric(baseline, metric) for metric in METRICS}
    supported_metrics = [
        metric
        for metric in METRICS
        if main and all(row["metrics"][metric]["delta_vs_baseline"] > 0 for row in main)
    ]
    seed_summary = _seed_spread(seed_robustness)
    weight_runs = weight_sensitivity.get("runs") or []
    return {
        "experiment": "pu_xmsat_publication_evidence_consolidation",
        "baseline": {
            "label": "reproduced MSAT baseline",
            "metrics": baseline_metrics,
        },
        "main_runs": main,
        "ablation": {
            "run_count": len(ablation),
            "runs": ablation,
        },
        "seed_robustness": {
            **seed_summary,
            "source_available": bool(seed_robustness),
        },
        "weight_sensitivity": {
            "reference_label": weight_sensitivity.get("reference_label", ""),
            "run_count": len(weight_runs),
            "source_available": bool(weight_sensitivity),
        },
        "main_claim": {
            "supported_metrics": supported_metrics,
            "unsupported_or_borderline_metrics": [
                metric for metric in METRICS if metric not in supported_metrics
            ],
            "claim_text": (
                "Full-positive hybrid PU-XMSAT shows positive reproduced-protocol "
                "deltas on the supported metrics across the consolidated main runs."
            ),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _format_metric(value: float) -> str:
    return f"{float(value):.6f}"


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# PU-XMSAT Publication Evidence Consolidation",
        "",
        f"- Claim boundary: {summary['claim_boundary']}",
        f"- Supported metrics: {', '.join(summary['main_claim']['supported_metrics']) or 'none'}",
        f"- Ablation runs consolidated: {summary['ablation']['run_count']}",
        f"- Seed robustness max spread: {_format_metric(summary['seed_robustness']['max_seed_spread'])}",
        f"- Weight sensitivity runs consolidated: {summary['weight_sensitivity']['run_count']}",
        "",
        "## Baseline",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
    ]
    for metric, value in summary["baseline"]["metrics"].items():
        lines.append(f"| {metric.upper()} | {_format_metric(value)} |")
    lines.extend(
        [
            "",
            "## Main PU-XMSAT Runs",
            "",
            "| Run | Metric | Mean | Delta vs baseline |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for run in summary["main_runs"]:
        for metric, values in run["metrics"].items():
            lines.append(
                f"| {run['label']} | {metric.upper()} | "
                f"{_format_metric(values['mean'])} | {values['delta_vs_baseline']:+.6f} |"
            )
    return "\n".join(lines) + "\n"


def write_publication_evidence_artifacts(
    summary: dict[str, Any],
    output_json: str | Path,
    output_md: str | Path,
) -> None:
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(summary), encoding="utf-8")


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("run arguments must use LABEL=PATH")
    label, path = value.rsplit("=", 1)
    return label.strip(), Path(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument("--main-run", action="append", type=_parse_run, required=True)
    parser.add_argument("--ablation-run", action="append", type=_parse_run, default=[])
    parser.add_argument("--seed-robustness", default="results/pu_xmsat_hybrid_seed_robustness_summary.json")
    parser.add_argument("--weight-sensitivity", default="results/pu_xmsat_hybrid_weight_sensitivity_summary.json")
    parser.add_argument("--output-json", default="results/pu_xmsat_publication_evidence_consolidation.json")
    parser.add_argument("--output-md", default="results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md")
    args = parser.parse_args()

    summary = build_publication_evidence_summary(
        baseline=_load(args.baseline),
        main_runs=[(label, _load(path)) for label, path in args.main_run],
        ablation_runs=[(label, _load(path)) for label, path in args.ablation_run],
        seed_robustness=_load(args.seed_robustness) if Path(args.seed_robustness).exists() else {},
        weight_sensitivity=_load(args.weight_sensitivity) if Path(args.weight_sensitivity).exists() else {},
    )
    write_publication_evidence_artifacts(summary, args.output_json, args.output_md)
    print(f"Wrote {args.output_json} and {args.output_md}")


if __name__ == "__main__":
    main()
