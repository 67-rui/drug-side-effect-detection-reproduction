import sys

from config import DataConfig, TrainingConfig
from scripts import run_baselines, run_imbalanced


def _reset_protocol_config(monkeypatch):
    monkeypatch.setattr(DataConfig, 'NEG_RATIO', 1)
    monkeypatch.setattr(DataConfig, 'TEST_NEG_RATIO', 1)
    monkeypatch.setattr(TrainingConfig, 'USE_OPTIMAL_THRESHOLD', False)


def test_run_imbalanced_sets_train_and_test_neg_ratio(monkeypatch):
    _reset_protocol_config(monkeypatch)
    called = {}

    def fake_run_10fold_cv(experiment_tag=''):
        called['experiment_tag'] = experiment_tag

    monkeypatch.setattr(run_imbalanced.train, 'run_10fold_cv', fake_run_10fold_cv)

    run_imbalanced.main()

    assert called['experiment_tag'] == 'neg10'
    assert DataConfig.NEG_RATIO == 10
    assert DataConfig.TEST_NEG_RATIO == 10
    assert TrainingConfig.USE_OPTIMAL_THRESHOLD is True


def test_run_baselines_neg10_sets_train_and_test_neg_ratio(monkeypatch):
    _reset_protocol_config(monkeypatch)
    called = {}

    def fake_aggregate_existing(models, neg_suffix='', summary_name=None):
        called['neg_suffix'] = neg_suffix
        return {'models': []}

    monkeypatch.setattr(run_baselines, 'aggregate_existing', fake_aggregate_existing)
    monkeypatch.setattr(
        sys,
        'argv',
        ['run_baselines.py', '--neg-ratio', '10', '--aggregate-only'],
    )

    run_baselines.main()

    assert called['neg_suffix'] == '_neg10'
    assert DataConfig.NEG_RATIO == 10
    assert DataConfig.TEST_NEG_RATIO == 10
    assert TrainingConfig.USE_OPTIMAL_THRESHOLD is True
