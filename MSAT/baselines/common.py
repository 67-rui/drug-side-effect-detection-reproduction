"""Shared fold preparation and metrics for baseline experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import torch
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from config import DataConfig, TrainingConfig
from experiments.feature_extractor import FeatureExtractor


def positive_pair_set(herb_indices, adr_indices, labels) -> set[tuple[int, int]]:
    mask = labels == 1
    return {
        (int(h), int(a))
        for h, a in zip(herb_indices[mask], adr_indices[mask])
    }


def evaluation_positive_pair_set(val_h, val_a, val_y, test_h, test_a, test_y) -> set[tuple[int, int]]:
    """Positive CMM-ADR pairs hidden from the graph during validation/test."""
    return (
        positive_pair_set(val_h, val_a, val_y)
        | positive_pair_set(test_h, test_a, test_y)
    )


def remove_cmm_adr_pairs(data, pairs_to_remove):
    pair_set = set(pairs_to_remove)
    for edge_index_key in [
        ('herb', 'causes', 'adr'),
        ('adr', 'rev_causes', 'herb'),
    ]:
        edge_index = data[edge_index_key].edge_index
        keep = []
        for i in range(edge_index.size(1)):
            if edge_index_key[0] == 'herb':
                pair = (int(edge_index[0, i]), int(edge_index[1, i]))
            else:
                pair = (int(edge_index[1, i]), int(edge_index[0, i]))
            keep.append(pair not in pair_set)

        keep_mask = torch.tensor(keep)
        data[edge_index_key].edge_index = edge_index[:, keep_mask]
        if hasattr(data[edge_index_key], 'edge_attr') and data[edge_index_key].edge_attr is not None:
            data[edge_index_key].edge_attr = data[edge_index_key].edge_attr[keep_mask]
    return data


@dataclass
class FoldSplit:
    fold_idx: int
    data: torch.utils.data.Dataset  # HeteroData (CPU)
    train_h: np.ndarray
    train_a: np.ndarray
    train_y: np.ndarray
    val_h: np.ndarray
    val_a: np.ndarray
    val_y: np.ndarray
    test_h: np.ndarray
    test_a: np.ndarray
    test_y: np.ndarray
    herb_x: np.ndarray
    adr_x: np.ndarray
    herb_train_degree: np.ndarray
    edge_attr_map: dict[tuple[int, int], np.ndarray]


def build_edge_attr_map(data) -> dict[tuple[int, int], np.ndarray]:
    """CMM–ADR 6-dim evidence features (paper §3.2), keyed by (herb, adr)."""
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    out: dict[tuple[int, int], np.ndarray] = {}
    for i in range(ei.size(1)):
        out[(int(ei[0, i]), int(ei[1, i]))] = ea[i].numpy().astype(np.float32)
    return out


def prepare_fold(fold_idx: int) -> FoldSplit:
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
        n_folds=DataConfig.N_FOLDS,
        neg_ratio=DataConfig.NEG_RATIO,
        test_neg_ratio=getattr(DataConfig, 'TEST_NEG_RATIO', DataConfig.NEG_RATIO),
        random_seed=DataConfig.RANDOM_SEED,
    )
    data = extractor.get_graph_data()
    train_data, test_data = extractor.load_fold_data(fold_idx)

    rng = np.random.RandomState(TrainingConfig.RANDOM_STATE + fold_idx)
    n_dev = len(train_data['labels'])
    indices = rng.permutation(n_dev)
    n_val = int(n_dev * (1 - TrainingConfig.TRAIN_VAL_SPLIT))
    val_sub = indices[:n_val]
    train_sub = indices[n_val:]

    hidden_eval_pos = evaluation_positive_pair_set(
        train_data['herb_indices'][val_sub],
        train_data['adr_indices'][val_sub],
        train_data['labels'][val_sub],
        test_data['herb_indices'],
        test_data['adr_indices'],
        test_data['labels'],
    )
    data = remove_cmm_adr_pairs(data, hidden_eval_pos)
    edge_attr_map = build_edge_attr_map(data)

    pos_ei = data['herb', 'causes', 'adr'].edge_index
    herb_train_degree = np.bincount(
        pos_ei[0].numpy(), minlength=data['herb'].x.size(0)
    ).astype(np.float32)

    return FoldSplit(
        fold_idx=fold_idx,
        data=data,
        train_h=train_data['herb_indices'][train_sub],
        train_a=train_data['adr_indices'][train_sub],
        train_y=train_data['labels'][train_sub],
        val_h=train_data['herb_indices'][val_sub],
        val_a=train_data['adr_indices'][val_sub],
        val_y=train_data['labels'][val_sub],
        test_h=test_data['herb_indices'],
        test_a=test_data['adr_indices'],
        test_y=test_data['labels'],
        herb_x=data['herb'].x.numpy(),
        adr_x=data['adr'].x.numpy(),
        herb_train_degree=herb_train_degree,
        edge_attr_map=edge_attr_map,
    )


def pair_features(
    herb_x: np.ndarray,
    adr_x: np.ndarray,
    h: np.ndarray,
    a: np.ndarray,
    edge_attr_map: dict[tuple[int, int], np.ndarray] | None = None,
    edge_dim: int = 6,
    include_edge_attr: bool = False,
) -> np.ndarray:
    """Node concat features for ML baselines.

    CMM-ADR edge evidence is label-carrying for positive graph edges, so ML
    baselines exclude it by default. It can be enabled only for diagnostics.
    """
    node_part = np.concatenate([herb_x[h], adr_x[a]], axis=1)
    if edge_attr_map is None or not include_edge_attr:
        return node_part
    edge_part = np.zeros((len(h), edge_dim), dtype=np.float32)
    for i, (hi, ai) in enumerate(zip(h, a)):
        feat = edge_attr_map.get((int(hi), int(ai)))
        if feat is not None:
            edge_part[i] = feat
    return np.concatenate([node_part, edge_part], axis=1)


def compute_metrics(labels, scores, threshold: float = 0.5) -> Dict[str, float]:
    labels = np.asarray(labels)
    scores = np.asarray(scores)
    pred = (scores >= threshold).astype(int)
    return {
        'precision': float(precision_score(labels, pred, zero_division=0)),
        'recall': float(recall_score(labels, pred, zero_division=0)),
        'f1': float(f1_score(labels, pred, zero_division=0)),
        'auc': float(roc_auc_score(labels, scores)),
        'auprc': float(average_precision_score(labels, scores)),
        'mcc': float(matthews_corrcoef(labels, pred)),
    }


def aggregate_fold_metrics(fold_metrics: list[Dict[str, float]]) -> Dict[str, dict]:
    overall = {}
    for key in ['precision', 'recall', 'f1', 'auc', 'auprc', 'mcc']:
        vals = [m[key] for m in fold_metrics]
        overall[key] = {
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals)),
            'values': vals,
        }
    return overall
