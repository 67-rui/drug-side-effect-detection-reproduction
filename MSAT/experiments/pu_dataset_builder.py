from __future__ import annotations

from pathlib import Path

import numpy as np

from experiments.reliable_negative_sampling import CandidateScore


Pair = tuple[int, int]


def build_pu_training_arrays(
    positive_pairs: list[Pair],
    reliable_negatives: list[CandidateScore],
    unlabeled_pairs: list[Pair],
    unlabeled_weight: float = 0.20,
    reliable_negative_weight: float = 0.80,
) -> dict[str, np.ndarray]:
    herbs: list[int] = []
    adrs: list[int] = []
    labels: list[int] = []
    weights: list[float] = []
    pair_types: list[str] = []

    for herb_id, adr_id in positive_pairs:
        herbs.append(int(herb_id))
        adrs.append(int(adr_id))
        labels.append(1)
        weights.append(1.0)
        pair_types.append("positive")

    for row in reliable_negatives:
        herbs.append(int(row.herb_id))
        adrs.append(int(row.adr_id))
        labels.append(0)
        weights.append(float(reliable_negative_weight))
        pair_types.append("reliable_negative")

    for herb_id, adr_id in unlabeled_pairs:
        herbs.append(int(herb_id))
        adrs.append(int(adr_id))
        labels.append(0)
        weights.append(float(unlabeled_weight))
        pair_types.append("unlabeled")

    return {
        "herb_idx": np.asarray(herbs, dtype=np.int64),
        "adr_idx": np.asarray(adrs, dtype=np.int64),
        "label": np.asarray(labels, dtype=np.int64),
        "sample_weight": np.asarray(weights, dtype=np.float32),
        "pair_type": np.asarray(pair_types, dtype=object),
    }


def save_pu_arrays(path: str | Path, arrays: dict[str, np.ndarray]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **arrays)


def load_pu_arrays(path: str | Path) -> dict[str, np.ndarray]:
    loaded = np.load(Path(path), allow_pickle=True)
    return {key: loaded[key] for key in loaded.files}
