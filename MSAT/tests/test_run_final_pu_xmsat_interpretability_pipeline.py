import json
import subprocess

import pytest


def _module():
    from scripts import run_final_pu_xmsat_interpretability_pipeline as pipeline

    return pipeline


def _command(commands, name):
    for command in commands:
        if command.name == name:
            return command.argv
    raise AssertionError(f"missing command {name}")


def test_default_pipeline_uses_full_final_configuration():
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(["--dry-run"])

    pipeline.validate_args(args)
    commands = pipeline.build_pipeline_commands(args)

    training = _command(commands, "train_final_checkpoint")
    assert training[0].endswith("python") or "python" in training[0]
    assert training[1] == "experiments/run_pu_msat_experiment.py"
    assert training[training.index("--backend") + 1] == "full_msat_pu"
    assert training[training.index("--sampling-strategy") + 1] == "hybrid"
    assert training[training.index("--seed") + 1] == "2026"
    assert training[training.index("--max-folds") + 1] == "10"
    assert training[training.index("--max-epochs") + 1] == "200"
    assert training[training.index("--max-pairs") + 1] == "66015"
    assert training[training.index("--threshold-strategy") + 1] == "val_f1"
    assert training[training.index("--unlabeled-weight") + 1] == "0.2"
    assert training[training.index("--reliable-negative-weight") + 1] == "0.8"
    assert "--save-checkpoints" in training
    assert "saved_models/pu_xmsat_formal" in training
    assert "best_model_for_prediction" not in " ".join(training)

    top_predictions = _command(commands, "export_top_predictions")
    assert "--checkpoint-is-final-pu-xmsat" in top_predictions
    assert top_predictions[top_predictions.index("--top-k") + 1] == "50"
    assert "results/pu_xmsat_top_predictions.json" in top_predictions

    contribution = _command(commands, "quantify_contributions")
    assert "--checkpoint-is-final-pu" in contribution
    assert contribution[contribution.index("--max-cases") + 1] == "50"
    assert contribution[contribution.index("--device") + 1] == "cuda"


def test_pipeline_rejects_nonfinal_fold_count_without_override():
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(["--max-folds", "1", "--dry-run"])

    with pytest.raises(ValueError, match="full 10-fold"):
        pipeline.validate_args(args)


def test_dry_run_writes_manifest_without_executing(tmp_path):
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(
        [
            "--dry-run",
            "--manifest",
            str(tmp_path / "manifest.json"),
        ]
    )
    executed = []

    pipeline.run_pipeline(args, runner=lambda *a, **k: executed.append(a))

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert executed == []
    assert manifest["dry_run"] is True
    assert manifest["commands"][0]["name"] == "train_final_checkpoint"
    assert manifest["commands"][1]["name"] == "export_top_predictions"
    assert manifest["final_checkpoint_path"].endswith("_fold0.pt")


def test_runner_stops_when_a_step_fails(tmp_path):
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(
        [
            "--manifest",
            str(tmp_path / "manifest.json"),
        ]
    )
    calls = []

    def runner(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 2)

    with pytest.raises(RuntimeError, match="train_final_checkpoint failed"):
        pipeline.run_pipeline(args, runner=runner)

    assert len(calls) == 1
