from experiments.run_pu_msat_experiment import build_experiment_config


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
