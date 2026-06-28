from __future__ import annotations

import copy
import re
from collections.abc import Callable

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


def _path_node_matches(path: str) -> list[tuple[int, str, int]]:
    patterns = [
        ("compound", re.compile(r"Compound\s+#(\d+)", flags=re.IGNORECASE)),
        ("target", re.compile(r"Target\s+#(\d+)", flags=re.IGNORECASE)),
    ]
    matches: list[tuple[int, str, int]] = []
    for node_type, pattern in patterns:
        for match in pattern.finditer(path):
            matches.append((match.start(), node_type, int(match.group(1))))
    return sorted(matches, key=lambda item: item[0])


def extract_node_refs_from_path(path: str) -> list[dict]:
    refs: list[dict] = []
    for _, node_type, node_id in _path_node_matches(path):
        feature = f"{node_type}:{node_id}"
        refs.append(
            {
                "feature": feature,
                "node_type": node_type,
                "node_id": node_id,
                "label": f"{node_type.title()} #{node_id}",
            }
        )
    return refs


def extract_node_refs_from_paths(paths: list[str]) -> list[dict]:
    refs: list[dict] = []
    seen: set[str] = set()
    for path in paths:
        for ref in extract_node_refs_from_path(path):
            feature = ref["feature"]
            if feature in seen:
                continue
            seen.add(feature)
            refs.append(ref)
    return refs


def build_key_mechanism_subgraph(paths: list[str]) -> dict:
    node_by_feature: dict[str, dict] = {}
    edge_paths: dict[tuple[str, str], set[int]] = {}
    path_rows: list[dict] = []

    for path_index, path_text in enumerate(paths, start=1):
        refs = extract_node_refs_from_path(path_text)
        for ref in refs:
            node_by_feature.setdefault(ref["feature"], dict(ref))

        features = [ref["feature"] for ref in refs]
        path_rows.append(
            {
                "path_index": path_index,
                "path_text": path_text,
                "features": features,
                "feature_refs": refs,
            }
        )
        for source, target in zip(features, features[1:]):
            edge_paths.setdefault((source, target), set()).add(path_index)

    nodes = sorted(node_by_feature.values(), key=lambda row: (row["node_type"], row["node_id"]))
    edges = [
        {"source": source, "target": target, "path_indices": sorted(path_indices)}
        for (source, target), path_indices in sorted(edge_paths.items())
    ]
    return {
        "nodes": nodes,
        "edges": edges,
        "paths": path_rows,
    }


def zero_x_dict_node_features(
    x_dict: dict[str, torch.Tensor],
    node_type: str,
    node_id: int,
) -> dict[str, torch.Tensor]:
    masked = dict(x_dict)
    masked[node_type] = x_dict[node_type].clone()
    masked[node_type][int(node_id)] = torch.zeros_like(masked[node_type][int(node_id)])
    return masked


def zero_x_dict_feature_refs(
    x_dict: dict[str, torch.Tensor],
    refs: list[dict],
) -> dict[str, torch.Tensor]:
    masked = dict(x_dict)
    cloned_types: set[str] = set()
    for ref in refs:
        node_type = ref["node_type"]
        node_id = int(ref["node_id"])
        if node_type not in cloned_types:
            masked[node_type] = x_dict[node_type].clone()
            cloned_types.add(node_type)
        masked[node_type][node_id] = torch.zeros_like(masked[node_type][node_id])
    return masked


def score_node_perturbations(
    original_score: float,
    node_refs: list[dict],
    score_masked: Callable[[dict], float],
) -> list[dict]:
    rows = []
    for ref in node_refs:
        masked_score = float(score_masked(ref))
        rows.append(
            {
                **ref,
                "masked_score": masked_score,
                "score_drop": round(float(original_score) - masked_score, 10),
            }
        )
    return sorted(rows, key=lambda row: (-row["score_drop"], row["feature"]))


def score_path_perturbations(
    original_score: float,
    paths: list[dict],
    score_masked_path: Callable[[dict], float],
) -> list[dict]:
    rows = []
    for path in paths:
        masked_score = float(score_masked_path(path))
        rows.append(
            {
                "feature": f"path:{path['path_index']}",
                "path_index": int(path["path_index"]),
                "path_text": path["path_text"],
                "features": list(path["features"]),
                "masked_score": masked_score,
                "score_drop": round(float(original_score) - masked_score, 10),
            }
        )
    return sorted(rows, key=lambda row: (-row["score_drop"], row["feature"]))
