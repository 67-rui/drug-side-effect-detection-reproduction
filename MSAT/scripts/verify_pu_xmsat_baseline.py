from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = [
    "results/summary.json",
    "results/baseline_summary.json",
    "results/summary_neg10.json",
    "results/faers_only_coldstart_summary.json",
    "results/table5_summary.json",
    "results/reproduction_state_audit.json",
    "results/TABLE5_PROTOCOL_DECISION.md",
    "results/PU_XMSAT_BASELINE_LOCK.md",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def verify_baseline(root: Path) -> dict:
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        return {"ok": False, "missing": missing}

    summary = _load_json(root / "results/summary.json")
    table5 = _load_json(root / "results/table5_summary.json")
    audit = _load_json(root / "results/reproduction_state_audit.json")

    protocol = summary.get("protocol", {})
    metrics = summary["overall_metrics"]

    checks = {
        "summary_auc": metrics["auc"]["mean"],
        "summary_auprc": metrics["auprc"]["mean"],
        "summary_f1": metrics["f1"]["mean"],
        "summary_mcc": metrics["mcc"]["mean"],
        "table5_supported_count": table5["supported_count"],
        "table5_support_rate": table5["support_rate"],
        "audit_issue_count": len(audit.get("issues", [])),
        "protocol_version": protocol.get("version"),
    }

    ok = (
        checks["summary_auc"] > 0.97
        and checks["summary_auprc"] > 0.97
        and checks["table5_supported_count"] == 1
        and checks["audit_issue_count"] == 0
        and protocol.get("validation_and_test_positive_edges_hidden") is True
    )
    return {"ok": ok, "missing": [], **checks}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    result = verify_baseline(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
