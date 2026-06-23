import numpy as np
import pytest

import train
from baselines import gnn_models


def test_prediction_payload_uses_supplied_threshold_for_y_pred():
    payload = train.prediction_payload(
        labels=np.array([1, 0, 1], dtype=np.float32),
        scores=np.array([0.62, 0.58, 0.81], dtype=np.float32),
        threshold=0.6,
    )

    assert payload['y_true'] == [1.0, 0.0, 1.0]
    assert payload['y_score'] == pytest.approx([0.62, 0.58, 0.81])
    assert payload['y_pred'] == [1, 0, 1]


def test_gnn_metrics_can_use_validation_optimal_threshold():
    metrics = gnn_models.metrics_with_validation_threshold(
        val_y=np.array([1, 0], dtype=np.float32),
        val_scores=np.array([0.4, 0.3], dtype=np.float32),
        test_y=np.array([1, 0], dtype=np.float32),
        test_scores=np.array([0.4, 0.3], dtype=np.float32),
        use_optimal_threshold=True,
    )

    assert metrics['threshold'] < 0.5
    assert metrics['f1'] == 1.0
