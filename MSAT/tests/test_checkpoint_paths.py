from pathlib import Path

import train


def test_prediction_checkpoint_path_uses_legacy_default_for_main_run():
    assert train.prediction_checkpoint_path(None) == Path('saved_models/best_model_for_prediction.pt')
    assert train.prediction_checkpoint_path('') == Path('saved_models/best_model_for_prediction.pt')


def test_prediction_checkpoint_path_is_tagged_for_auxiliary_runs():
    assert train.prediction_checkpoint_path('testneg10') == Path(
        'saved_models/best_model_for_prediction_testneg10.pt'
    )
