from pathlib import Path


def test_server_pu_xmsat_run_uses_safe_outputs():
    text = Path("scripts/server_pu_xmsat_run.sh").read_text()
    assert "pu_training_summary.json" in text
    assert "summary.json" not in text.split("pu_training_summary.json")[0]
    assert "set -euo pipefail" in text


def test_server_pu_xmsat_run_defaults_to_bounded_full_backend():
    text = Path("scripts/server_pu_xmsat_run.sh").read_text()
    assert "PU_XMSAT_BACKEND:-full_msat_pu" in text
    assert "PU_XMSAT_THRESHOLD_STRATEGY:-fixed_0_5" in text
    assert "PU_XMSAT_MAX_FOLDS:-1" in text
    assert "PU_XMSAT_MAX_EPOCHS:-5" in text
    assert "--backend" in text
    assert "--threshold-strategy" in text
