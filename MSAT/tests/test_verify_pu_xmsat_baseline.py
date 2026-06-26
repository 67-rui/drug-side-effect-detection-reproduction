from pathlib import Path

from scripts.verify_pu_xmsat_baseline import verify_baseline


def test_verify_baseline_accepts_current_results():
    root = Path(__file__).resolve().parents[1]
    result = verify_baseline(root)
    assert result["ok"] is True
    assert result["summary_auc"] > 0.97
    assert result["table5_supported_count"] == 1
