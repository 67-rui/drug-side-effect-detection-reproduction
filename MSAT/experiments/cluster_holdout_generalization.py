from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "Cluster-held-out evaluation measures generalization to a held-out cluster of "
    "CMM/herb nodes under the available graph protocol; it is not external clinical "
    "validation and does not prove causal transportability."
)


def cluster_herb_features(
    herb_features: np.ndarray,
    n_clusters: int,
    seed: int = 42,
) -> np.ndarray:
    features = np.asarray(herb_features, dtype=float)
    if features.ndim != 2:
        raise ValueError("herb_features must be a 2D array")
    if n_clusters <= 1 or n_clusters > features.shape[0]:
        raise ValueError("n_clusters must be in [2, number of herbs]")
    rng = np.random.RandomState(int(seed))
    first_center = int(rng.randint(0, features.shape[0]))
    center_indices = [first_center]
    while len(center_indices) < int(n_clusters):
        centers = features[np.asarray(center_indices, dtype=np.int64)]
        distances = ((features[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        min_distances = distances.min(axis=1)
        for used in center_indices:
            min_distances[used] = -1.0
        center_indices.append(int(np.argmax(min_distances)))

    centers = features[np.asarray(center_indices, dtype=np.int64)].copy()
    labels = np.zeros(features.shape[0], dtype=np.int64)
    for _ in range(100):
        distances = ((features[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = distances.argmin(axis=1).astype(np.int64)
        new_centers = centers.copy()
        for cluster_idx in range(int(n_clusters)):
            members = features[new_labels == cluster_idx]
            if members.size:
                new_centers[cluster_idx] = members.mean(axis=0)
            else:
                farthest = int(np.argmax(distances.min(axis=1)))
                new_centers[cluster_idx] = features[farthest]
                new_labels[farthest] = cluster_idx
        if np.array_equal(new_labels, labels) and np.allclose(new_centers, centers):
            labels = new_labels
            break
        labels = new_labels
        centers = new_centers
    return labels.astype(np.int64)


def _positive_set(positive_pairs: np.ndarray) -> set[tuple[int, int]]:
    return {(int(h), int(a)) for h, a in np.asarray(positive_pairs, dtype=np.int64)}


def _sample_negatives_for_positives(
    positive_pairs: list[tuple[int, int]],
    all_positive_pairs: set[tuple[int, int]],
    num_adrs: int,
    neg_ratio: int,
    seed: int,
) -> list[tuple[int, int]]:
    rng = np.random.RandomState(int(seed))
    negatives: list[tuple[int, int]] = []
    used = set(all_positive_pairs)
    for herb_id, _ in positive_pairs:
        sampled = 0
        attempts = 0
        while sampled < int(neg_ratio) and attempts < num_adrs * 20:
            attempts += 1
            adr_id = int(rng.randint(0, num_adrs))
            pair = (int(herb_id), adr_id)
            if pair in used:
                continue
            negatives.append(pair)
            used.add(pair)
            sampled += 1
    return negatives


def _pack_split(
    positives: list[tuple[int, int]],
    negatives: list[tuple[int, int]],
) -> dict[str, np.ndarray]:
    pairs = [*positives, *negatives]
    labels = [1.0] * len(positives) + [0.0] * len(negatives)
    if not pairs:
        return {
            "herb_indices": np.array([], dtype=np.int64),
            "adr_indices": np.array([], dtype=np.int64),
            "labels": np.array([], dtype=np.float32),
        }
    herbs, adrs = zip(*pairs)
    return {
        "herb_indices": np.asarray(herbs, dtype=np.int64),
        "adr_indices": np.asarray(adrs, dtype=np.int64),
        "labels": np.asarray(labels, dtype=np.float32),
    }


def build_cluster_holdout_split(
    positive_pairs: np.ndarray,
    cluster_labels: np.ndarray,
    holdout_cluster: int,
    num_adrs: int,
    neg_ratio: int = 1,
    seed: int = 42,
) -> dict[str, Any]:
    pairs = np.asarray(positive_pairs, dtype=np.int64)
    labels = np.asarray(cluster_labels, dtype=np.int64)
    if pairs.ndim != 2 or pairs.shape[1] != 2:
        raise ValueError("positive_pairs must be an Nx2 array")
    if num_adrs <= 0:
        raise ValueError("num_adrs must be positive")
    if neg_ratio < 0:
        raise ValueError("neg_ratio must be non-negative")
    if pairs.size and int(pairs[:, 0].max()) >= labels.shape[0]:
        raise ValueError("cluster_labels does not cover every herb in positive_pairs")

    heldout_herbs = [
        int(idx) for idx, cluster in enumerate(labels.tolist()) if int(cluster) == int(holdout_cluster)
    ]
    heldout_set = set(heldout_herbs)
    train_pos = [(int(h), int(a)) for h, a in pairs if int(h) not in heldout_set]
    test_pos = [(int(h), int(a)) for h, a in pairs if int(h) in heldout_set]
    all_pos = _positive_set(pairs)
    train_neg = _sample_negatives_for_positives(
        train_pos,
        all_positive_pairs=all_pos,
        num_adrs=int(num_adrs),
        neg_ratio=int(neg_ratio),
        seed=int(seed),
    )
    test_neg = _sample_negatives_for_positives(
        test_pos,
        all_positive_pairs=all_pos | set(train_neg),
        num_adrs=int(num_adrs),
        neg_ratio=int(neg_ratio),
        seed=int(seed) + 1009,
    )
    return {
        "protocol": "cluster_held_out_generalization",
        "holdout_cluster": int(holdout_cluster),
        "heldout_herbs": heldout_herbs,
        "train_positive_pairs": train_pos,
        "test_positive_pairs": test_pos,
        "hidden_eval_positive_pairs": test_pos,
        "train_data": _pack_split(train_pos, train_neg),
        "test_data": _pack_split(test_pos, test_neg),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def summarize_cluster_holdout_split(split: dict[str, Any]) -> dict[str, Any]:
    train_labels = np.asarray(split["train_data"]["labels"], dtype=float)
    test_labels = np.asarray(split["test_data"]["labels"], dtype=float)
    return {
        "protocol": "cluster_held_out_generalization",
        "holdout_cluster": int(split["holdout_cluster"]),
        "heldout_herb_count": len(split.get("heldout_herbs", [])),
        "train_pair_count": int(train_labels.size),
        "train_positive_count": int(train_labels.sum()),
        "test_pair_count": int(test_labels.size),
        "test_positive_count": int(test_labels.sum()),
        "hidden_eval_positive_pair_count": len(split.get("hidden_eval_positive_pairs", [])),
        "claim_boundary": CLAIM_BOUNDARY,
    }
