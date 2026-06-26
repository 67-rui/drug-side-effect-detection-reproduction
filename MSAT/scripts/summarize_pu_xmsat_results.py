from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def markdown_metric_row(name: str, metrics: dict) -> str:
    return f"| {name} | {metrics['auc']:.4f} | {metrics['auprc']:.4f} |"


def _load_json_optional(path: str | Path) -> dict | None:
    candidate = Path(path)
    if not candidate.exists():
        return None
    return json.loads(candidate.read_text())


def _evidence_grade_lines(evidence: dict | None) -> list[str]:
    if not evidence:
        return ["Evidence screening table has not been generated yet."]
    counts = Counter(row.get("evidence_grade", "NA") for row in evidence.get("rows", []))
    if not counts:
        return ["Evidence screening table contains no rows."]
    return [
        f"- Grade {grade}: {count}"
        for grade, count in sorted(counts.items())
    ]


def _threshold_lines(pu_smoke: dict | None) -> list[str]:
    if not pu_smoke:
        return []
    rows = []
    for row in pu_smoke.get("fold_results", []):
        threshold = row.get("optimal_threshold")
        val_f1 = row.get("val_f1_at_threshold")
        if threshold is None:
            continue
        val_f1_text = "NA" if val_f1 is None else f"{float(val_f1):.4f}"
        rows.append(
            f"| Fold {row.get('fold', 'NA')} | {float(threshold):.4f} | {val_f1_text} |"
        )
    if not rows:
        return []
    return [
        "",
        "| Fold | Selected threshold | Validation F1 |",
        "| --- | ---: | ---: |",
        *rows,
    ]


def build_report(
    baseline: dict,
    pu_smoke: dict | None,
    evidence: dict | None,
) -> str:
    baseline_metrics = {
        "auc": baseline["overall_metrics"]["auc"]["mean"],
        "auprc": baseline["overall_metrics"]["auprc"]["mean"],
    }
    pu_metrics = None
    if pu_smoke:
        mean_metrics = pu_smoke.get("mean_metrics", {})
        if mean_metrics.get("auc") is not None and mean_metrics.get("auprc") is not None:
            pu_metrics = {
                "auc": float(mean_metrics["auc"]),
                "auprc": float(mean_metrics["auprc"]),
            }
    pu_status = (
        pu_smoke.get("status", "unknown") if pu_smoke else "not_generated"
    )
    training_executed = (
        bool(pu_smoke.get("training_executed")) if pu_smoke else False
    )
    training_backend = (
        pu_smoke.get("training_backend", "not_generated") if pu_smoke else "not_generated"
    )
    threshold_strategy = (
        pu_smoke.get("threshold_strategy", "not_generated") if pu_smoke else "not_generated"
    )

    lines = [
        "# PU-XMSAT Experiment Report",
        "",
        "## Baseline",
        "",
        "| Model | AUC | AUPRC |",
        "| --- | ---: | ---: |",
        markdown_metric_row("MSAT", baseline_metrics),
    ]
    if pu_metrics:
        lines.append(markdown_metric_row("PU-XMSAT", pu_metrics))
    lines.extend([
        "",
        "## Current PU-XMSAT Status",
        "",
        f"- Status: {pu_status}",
        f"- Backend: {training_backend}",
        f"- Threshold strategy: {threshold_strategy}",
        f"- Training executed: {training_executed}",
        "- Interpretation: first-round research prototype; full multi-seed training is pending.",
        *_threshold_lines(pu_smoke),
        "",
        "## Evidence Screening",
        "",
        *_evidence_grade_lines(evidence),
        "",
        "## Reproduction Guardrail",
        "",
        "- Baseline tag: baseline/msat-reproduction-20260626",
        "- Default MSAT training behavior remains the comparison anchor.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument("--pu", default="results/pu_training_smoke_summary.json")
    parser.add_argument("--evidence", default="results/evidence_screening_summary.json")
    parser.add_argument("--output", default="results/PU_XMSAT_EXPERIMENT_REPORT.md")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    pu_smoke = _load_json_optional(args.pu)
    evidence = _load_json_optional(args.evidence)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_report(baseline, pu_smoke, evidence))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
