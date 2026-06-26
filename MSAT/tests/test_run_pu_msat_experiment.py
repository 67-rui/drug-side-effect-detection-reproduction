import math

from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.full_msat_pu_training import (
    FullMSATPUConfig,
    summarize_full_fold_results,
)
from experiments.reliable_negative_sampling import CandidateScore
from experiments.run_pu_msat_experiment import (
    build_experiment_config,
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
