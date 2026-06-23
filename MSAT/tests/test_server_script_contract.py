from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _script(name: str) -> str:
    return (ROOT / 'scripts' / name).read_text(encoding='utf-8')


def test_paper_retrain_script_uses_valid_long_run_entrypoints():
    text = _script('server_paper_retrain.sh')

    assert 'set -euo pipefail' in text
    assert '--models' not in text
    assert 'scripts/run_baselines.py --ml' in text
    assert 'scripts/run_baselines.py --gnn' in text
    assert 'scripts/run_ablation.py --all' in text
    assert 'scripts/run_ablation.py --only' in text
    assert 'scripts/run_ablation.py --aggregate-only' in text
    assert 'validation/test-positive graph removal' in text


def test_phase9_script_fails_fast_and_uses_explicit_checkpoint_for_predictor_outputs():
    text = _script('server_phase9_run.sh')

    assert 'set -euo pipefail' in text
    assert 'CKPT="${CKPT:-saved_models/best_model_for_prediction.pt}"' in text
    assert 'scripts/run_case_zhishi.py --checkpoint "$CKPT"' in text
    assert 'scripts/run_table5_validation.py --use-predictor --checkpoint "$CKPT"' in text


def test_partial_artifact_rerun_requires_explicit_opt_in():
    text = _script('rerun_after_artifact_fix.sh')

    assert 'ALLOW_PARTIAL_RERUN' in text
    assert 'server_paper_retrain.sh' in text
