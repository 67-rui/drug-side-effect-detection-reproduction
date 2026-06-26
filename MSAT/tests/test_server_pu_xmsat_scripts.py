from pathlib import Path


def test_server_pu_xmsat_run_uses_safe_outputs():
    text = Path("scripts/server_pu_xmsat_run.sh").read_text()
    assert "pu_training_summary.json" in text
    assert "summary.json" not in text.split("pu_training_summary.json")[0]
    assert "set -euo pipefail" in text
