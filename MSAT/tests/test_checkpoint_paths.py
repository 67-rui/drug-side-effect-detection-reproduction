from pathlib import Path

import train
from config import TrainingConfig


def test_prediction_checkpoint_path_uses_legacy_default_for_main_run():
    assert train.prediction_checkpoint_path(None) == Path('saved_models/best_model_for_prediction.pt')
    assert train.prediction_checkpoint_path('') == Path('saved_models/best_model_for_prediction.pt')


def test_prediction_checkpoint_path_is_tagged_for_auxiliary_runs():
    assert train.prediction_checkpoint_path('testneg10') == Path(
        'saved_models/best_model_for_prediction_testneg10.pt'
    )


def test_fold_checkpoint_path_uses_legacy_default_for_main_run():
    assert train.fold_checkpoint_path(2, None) == Path('saved_models/best_model_fold2.pt')
    assert train.fold_checkpoint_path(2, '') == Path('saved_models/best_model_fold2.pt')


def test_fold_checkpoint_path_is_tagged_for_auxiliary_runs():
    assert train.fold_checkpoint_path(2, 'testneg10') == Path(
        'saved_models/best_model_fold2_testneg10.pt'
    )


def test_model_selection_score_uses_validation_auc_not_test_auc():
    fold_result = {
        'best_val_auc': 0.42,
        'test_metrics': {'auc': 0.99},
    }

    assert train.model_selection_score(fold_result) == 0.42


def test_fold_checkpoints_are_disabled_by_default():
    assert TrainingConfig.SAVE_FOLD_CHECKPOINTS is False
