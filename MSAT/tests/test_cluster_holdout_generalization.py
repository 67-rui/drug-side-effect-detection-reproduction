import numpy as np

from experiments.cluster_holdout_generalization import (
    build_cluster_holdout_split,
    cluster_herb_features,
    summarize_cluster_holdout_split,
)


def test_cluster_herb_features_is_deterministic_and_uses_requested_cluster_count():
    features = np.array(
        [
            [0.0, 0.0],
            [0.1, 0.0],
            [10.0, 10.0],
            [10.1, 10.0],
        ],
        dtype=float,
    )

    first = cluster_herb_features(features, n_clusters=2, seed=7)
    second = cluster_herb_features(features, n_clusters=2, seed=7)

    assert first.tolist() == second.tolist()
    assert sorted(set(first.tolist())) == [0, 1]
    assert first[0] == first[1]
    assert first[2] == first[3]


def test_build_cluster_holdout_split_hides_heldout_cluster_positive_labels():
    positive_pairs = np.array(
        [
            [0, 0],
            [0, 1],
            [1, 0],
            [2, 2],
            [3, 3],
        ],
        dtype=np.int64,
    )
    cluster_labels = np.array([0, 0, 1, 1], dtype=np.int64)

    split = build_cluster_holdout_split(
        positive_pairs=positive_pairs,
        cluster_labels=cluster_labels,
        holdout_cluster=1,
        num_adrs=5,
        neg_ratio=1,
        seed=11,
    )

    train_pairs = set(zip(split["train_data"]["herb_indices"], split["train_data"]["adr_indices"]))
    test_pairs = set(zip(split["test_data"]["herb_indices"], split["test_data"]["adr_indices"]))

    assert (2, 2) not in train_pairs
    assert (3, 3) not in train_pairs
    assert (2, 2) in test_pairs
    assert (3, 3) in test_pairs
    assert all(cluster_labels[h] != 1 for h, label in zip(split["train_data"]["herb_indices"], split["train_data"]["labels"]) if label == 1)
    assert all(cluster_labels[h] == 1 for h, label in zip(split["test_data"]["herb_indices"], split["test_data"]["labels"]) if label == 1)
    assert split["hidden_eval_positive_pairs"] == [(2, 2), (3, 3)]


def test_summarize_cluster_holdout_split_reports_publishable_protocol_metadata():
    split = {
        "holdout_cluster": 2,
        "heldout_herbs": [4, 5],
        "train_data": {"labels": np.array([1, 1, 0], dtype=float)},
        "test_data": {"labels": np.array([1, 0, 1, 0], dtype=float)},
        "hidden_eval_positive_pairs": [(4, 10), (5, 11)],
    }

    summary = summarize_cluster_holdout_split(split)

    assert summary["protocol"] == "cluster_held_out_generalization"
    assert summary["holdout_cluster"] == 2
    assert summary["heldout_herb_count"] == 2
    assert summary["train_positive_count"] == 2
    assert summary["test_positive_count"] == 2
    assert summary["hidden_eval_positive_pair_count"] == 2
    assert "held-out cluster" in summary["claim_boundary"]
