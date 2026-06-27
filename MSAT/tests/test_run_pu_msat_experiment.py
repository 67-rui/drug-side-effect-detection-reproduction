import math

import experiments.full_msat_pu_training as full_training
from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.full_msat_pu_training import (
    FullMSATPUConfig,
    choose_threshold,
    summarize_full_fold_results,
)
from experiments.reliable_negative_sampling import CandidateScore
from experiments.run_pu_msat_experiment import (
    build_experiment_config,
    resolve_training_backend,
    run_weighted_pu_smoke_training,
)


def test_build_experiment_config_records_protocol():
    cfg = build_experiment_config(
        sampling_strategy="hybrid",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        max_folds=1,
        max_epochs=2,
    )
    assert cfg["experiment"] == "pu_xmsat"
    assert cfg["sampling_strategy"] == "hybrid"
    assert cfg["loss"] == "weighted_pu_bce"
    assert cfg["max_folds"] == 1


def test_build_experiment_config_records_full_backend():
    cfg = build_experiment_config(
        sampling_strategy="hybrid",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        max_folds=1,
        max_epochs=1,
        training_backend="full_msat_pu",
        threshold_strategy="val_f1",
    )
    assert cfg["training_backend"] == "full_msat_pu"
    assert cfg["threshold_strategy"] == "val_f1"


def test_resolve_training_backend_rejects_unknown_backend():
    try:
        resolve_training_backend("unknown")
    except ValueError as exc:
        assert "unknown backend" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_run_weighted_pu_smoke_training_executes_epochs():
    arrays = build_pu_training_arrays(
        positive_pairs=[(0, 1), (1, 2)],
        reliable_negatives=[
            CandidateScore(herb_id=2, adr_id=2, reliability_score=0.9),
        ],
        unlabeled_pairs=[(0, 0), (2, 1)],
    )
    result = run_weighted_pu_smoke_training(
        arrays,
        num_herbs=3,
        num_adrs=3,
        max_epochs=2,
        seed=7,
    )
    assert result["training_executed"] is True
    assert result["pair_count"] == 5
    assert len(result["loss_history"]) == 2
    assert all(math.isfinite(value) for value in result["loss_history"])


def test_full_msat_pu_config_uses_pu_checkpoint_names():
    cfg = FullMSATPUConfig(max_epochs=1, max_pairs=96)
    assert cfg.training_backend == "full_msat_pu"
    assert cfg.checkpoint_prefix == "pu_xmsat"
    assert cfg.threshold_strategy == "fixed_0_5"


def test_seed_fold_training_resets_numpy_and_torch_rng():
    full_training._seed_fold_training(123)
    first_numpy = full_training.np.random.rand(3)
    first_torch = full_training.torch.rand(3)

    full_training._seed_fold_training(123)
    second_numpy = full_training.np.random.rand(3)
    second_torch = full_training.torch.rand(3)

    assert (first_numpy == second_numpy).all()
    assert full_training.torch.equal(first_torch, second_torch)


def test_choose_threshold_can_use_validation_f1():
    threshold, val_f1 = choose_threshold(
        val_probs=[0.2, 0.45, 0.55, 0.9],
        val_labels=[0, 1, 0, 1],
        strategy="val_f1",
    )
    assert 0.2 < threshold < 0.9
    assert val_f1 > 0


def test_choose_threshold_fixed_strategy_returns_half():
    threshold, val_f1 = choose_threshold(
        val_probs=[0.2, 0.8],
        val_labels=[0, 1],
        strategy="fixed_0_5",
    )
    assert threshold == 0.5
    assert val_f1 is None


def test_summarize_full_fold_results_reports_metric_means():
    payload = summarize_full_fold_results(
        [
            {
                "fold": 0,
                "test_metrics": {"auc": 0.7, "auprc": 0.6, "f1": 0.5, "mcc": 0.4},
                "training_history": {"train_loss": [0.9, 0.8]},
            },
            {
                "fold": 1,
                "test_metrics": {"auc": 0.9, "auprc": 0.8, "f1": 0.7, "mcc": 0.6},
                "training_history": {"train_loss": [0.7, 0.6]},
            },
        ]
    )
    assert payload["auc"] == 0.8
    assert payload["auprc"] == 0.7
    assert payload["final_loss"] == 0.7


def test_run_full_msat_pu_experiment_aggregates_fold_results(monkeypatch):
    calls = []

    def fake_run_fold(fold_idx, config, sampling_strategy, unlabeled_weight,
                      reliable_negative_weight, candidate_cache, seed):
        calls.append(
            (
                fold_idx,
                config.max_epochs,
                config.max_pairs,
                sampling_strategy,
                config.threshold_strategy,
            )
        )
        return {
            "fold": fold_idx,
            "test_metrics": {
                "auc": 0.7 + fold_idx * 0.1,
                "auprc": 0.6 + fold_idx * 0.1,
                "f1": 0.5,
                "mcc": 0.4,
            },
            "training_history": {"train_loss": [0.9, 0.8 - fold_idx * 0.1]},
        }

    monkeypatch.setattr(full_training, "run_full_msat_pu_fold", fake_run_fold)

    result = full_training.run_full_msat_pu_experiment(
        sampling_strategy="hybrid",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        max_folds=2,
        max_epochs=3,
        max_pairs=96,
        candidate_cache="results/pu_candidate_scores.sample.jsonl",
        seed=42,
        threshold_strategy="val_f1",
    )

    assert calls == [(0, 3, 96, "hybrid", "val_f1"), (1, 3, 96, "hybrid", "val_f1")]
    assert result["status"] == "completed"
    assert result["training_executed"] is True
    assert result["training_backend"] == "full_msat_pu"
    assert result["threshold_strategy"] == "val_f1"
    assert result["mean_metrics"]["auc"] == 0.75
    assert result["mean_metrics"]["final_loss"] == 0.75
