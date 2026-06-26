from pathlib import Path

from scripts.verify_pu_xmsat_final import default_audit_output, verify_smoke_artifacts


def test_default_audit_output_does_not_overwrite_baseline_audit():
    assert default_audit_output().name == "pu_xmsat_reproduction_state_audit.final.json"
    assert "results/reproduction_state_audit.json" not in str(default_audit_output())


def test_verify_smoke_artifacts_accepts_current_outputs():
    root = Path(__file__).resolve().parents[1]
    result = verify_smoke_artifacts(root)
    assert result["ok"] is True
    assert result["training_executed"] is True
    assert result["training_backend"] == "weighted_embedding_smoke"
    assert result["smoke_final_loss"] < result["smoke_initial_loss"]
    assert result["evidence_rows"] == 15
