from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from scripts.verify_pu_xmsat_baseline import verify_baseline


REQUIRED_SMOKE_FILES = [
    "results/pu_candidate_scores.sample.jsonl",
    "results/pu_negative_sampling_summary.json",
    "results/pu_training_smoke_summary.json",
    "results/explanation_case_studies.json",
    "results/evidence_screening_summary.json",
    "results/evidence_screening_table.csv",
    "results/PU_XMSAT_EXPERIMENT_REPORT.md",
]

OPTIONAL_TRAINING_SUMMARY = "results/pu_training_summary.json"


def default_audit_output() -> Path:
    return Path(tempfile.gettempdir()) / "pu_xmsat_reproduction_state_audit.final.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _count_jsonl(path: Path) -> int:
    with path.open() as fh:
        return sum(1 for line in fh if line.strip())


def verify_smoke_artifacts(root: Path) -> dict:
    missing = [rel for rel in REQUIRED_SMOKE_FILES if not (root / rel).exists()]
    if missing:
        return {"ok": False, "missing": missing}

    candidate_count = _count_jsonl(root / "results/pu_candidate_scores.sample.jsonl")
    negative_sampling = _load_json(root / "results/pu_negative_sampling_summary.json")
    training = _load_json(root / "results/pu_training_smoke_summary.json")
    explanation = _load_json(root / "results/explanation_case_studies.json")
    evidence = _load_json(root / "results/evidence_screening_summary.json")
    report = (root / "results/PU_XMSAT_EXPERIMENT_REPORT.md").read_text()

    fold_results = training.get("fold_results", [])
    first_fold = fold_results[0] if fold_results else {}
    initial_loss = first_fold.get("initial_loss")
    final_loss = first_fold.get("final_loss")
    strategies = set(negative_sampling.get("strategies", []))

    checks = {
        "missing": [],
        "candidate_count": candidate_count,
        "negative_sampling_strategies": sorted(strategies),
        "training_executed": bool(training.get("training_executed")),
        "training_backend": training.get("training_backend"),
        "smoke_initial_loss": initial_loss,
        "smoke_final_loss": final_loss,
        "explanation_rows": len(explanation.get("rows", [])),
        "evidence_rows": len(evidence.get("rows", [])),
        "report_training_executed": "Training executed: True" in report,
    }
    ok = (
        candidate_count >= 1000
        and {"random", "low_score", "hybrid"}.issubset(strategies)
        and checks["training_executed"] is True
        and checks["training_backend"] == "weighted_embedding_smoke"
        and isinstance(initial_loss, int | float)
        and isinstance(final_loss, int | float)
        and math.isfinite(float(initial_loss))
        and math.isfinite(float(final_loss))
        and float(final_loss) < float(initial_loss)
        and checks["explanation_rows"] >= 5
        and checks["evidence_rows"] >= 15
        and checks["report_training_executed"] is True
    )
    return {"ok": ok, **checks}


def verify_training_summary(root: Path) -> dict:
    path = root / OPTIONAL_TRAINING_SUMMARY
    if not path.exists():
        return {"ok": True, "present": False}

    training = _load_json(path)
    fold_results = training.get("fold_results", [])
    mean_metrics = training.get("mean_metrics", {})
    backend = training.get("training_backend")
    final_loss = mean_metrics.get("final_loss")
    metric_values = {
        key: mean_metrics.get(key)
        for key in ["auc", "auprc", "f1", "mcc", "final_loss"]
        if mean_metrics.get(key) is not None
    }
    finite_metrics = all(
        isinstance(value, int | float) and math.isfinite(float(value))
        for value in metric_values.values()
    )
    ok = (
        bool(training.get("training_executed"))
        and backend in {"weighted_embedding_smoke", "full_msat_pu"}
        and bool(fold_results)
        and finite_metrics
    )
    return {
        "ok": ok,
        "present": True,
        "training_backend": backend,
        "fold_count": len(fold_results),
        "final_loss": final_loss,
        "mean_metrics": metric_values,
    }


def run_reproduction_audit(root: Path, audit_out: Path | None = None) -> dict:
    out = audit_out or default_audit_output()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_reproduction_state.py",
            "--out",
            str(out),
            "--fail-on-error",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    payload = _load_json(out) if out.exists() else {}
    return {
        "ok": result.returncode == 0 and payload.get("issues", []) == [],
        "audit_out": str(out),
        "returncode": result.returncode,
        "issues": payload.get("issues", []),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def verify_final(root: Path, audit_out: Path | None = None, run_audit: bool = True) -> dict:
    baseline = verify_baseline(root)
    smoke = verify_smoke_artifacts(root)
    training_summary = verify_training_summary(root)
    audit = run_reproduction_audit(root, audit_out=audit_out) if run_audit else {"ok": True}
    ok = (
        baseline.get("ok") is True
        and smoke.get("ok") is True
        and training_summary.get("ok") is True
        and audit.get("ok") is True
    )
    return {
        "ok": ok,
        "baseline": baseline,
        "smoke": smoke,
        "training_summary": training_summary,
        "audit": audit,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(MSAT_ROOT))
    parser.add_argument("--audit-out", default=str(default_audit_output()))
    parser.add_argument("--skip-audit", action="store_true")
    args = parser.parse_args()

    result = verify_final(
        Path(args.root),
        audit_out=Path(args.audit_out),
        run_audit=not args.skip_audit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
