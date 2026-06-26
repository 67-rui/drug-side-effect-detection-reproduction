from __future__ import annotations

import copy

import torch


def rank_score_drops(original_score: float, masked_scores: dict[str, float]) -> list[dict]:
    rows = [
        {
            "feature": feature,
            "masked_score": float(masked_score),
            "score_drop": round(float(original_score) - float(masked_score), 10),
        }
        for feature, masked_score in masked_scores.items()
    ]
    return sorted(rows, key=lambda row: (-row["score_drop"], row["feature"]))


def zero_node_features(data, node_type: str, node_ids: list[int]):
    copied = copy.deepcopy(data)
    if node_ids:
        copied[node_type].x[node_ids] = torch.zeros_like(copied[node_type].x[node_ids])
    return copied
