import math

from experiments.pu_dataset_builder import build_pu_training_arrays
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
