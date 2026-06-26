import numpy as np

from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.reliable_negative_sampling import CandidateScore


def test_build_pu_training_arrays_marks_positive_reliable_negative_and_unlabeled():
    arrays = build_pu_training_arrays(
        positive_pairs=[(0, 1), (1, 2)],
        reliable_negatives=[
            CandidateScore(herb_id=2, adr_id=2, reliability_score=0.9),
        ],
        unlabeled_pairs=[(0, 0), (2, 1)],
        unlabeled_weight=0.20,
        reliable_negative_weight=0.80,
    )
    assert arrays["herb_idx"].tolist() == [0, 1, 2, 0, 2]
    assert arrays["adr_idx"].tolist() == [1, 2, 2, 0, 1]
    assert arrays["label"].tolist() == [1, 1, 0, 0, 0]
    assert arrays["pair_type"].tolist() == [
        "positive",
        "positive",
        "reliable_negative",
        "unlabeled",
        "unlabeled",
    ]
    np.testing.assert_allclose(
        arrays["sample_weight"], [1.0, 1.0, 0.8, 0.2, 0.2]
    )
