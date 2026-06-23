"""Literature hold-out evaluation (paper Fig.5a / analyze_stratified protocol)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from sklearn.metrics import matthews_corrcoef, precision_score, roc_auc_score

from baselines.common import positive_pair_set, remove_cmm_adr_pairs
from experiments.feature_extractor import FeatureExtractor
from config import DataConfig


def literature_pairs() -> set[tuple[int, int]]:
    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    lit_mask = ea[:, 2].numpy() == 0
    return {
        (int(h), int(a))
        for h, a in zip(ei[0].numpy()[lit_mask], ei[1].numpy()[lit_mask])
    }


def literature_holdout_mask(
    y_true: np.ndarray,
    test_h: np.ndarray,
    test_a: np.ndarray,
    literature_pairs: set[tuple[int, int]],
) -> np.ndarray:
    """Test pairs for Fig.5a: all negatives + literature-sourced positives."""
    mask = np.zeros(len(y_true), dtype=bool)
    for i in range(len(y_true)):
        if y_true[i] == 0:
            mask[i] = True
        elif (int(test_h[i]), int(test_a[i])) in literature_pairs:
            mask[i] = True
    return mask


@dataclass
class FoldColdstart:
    fold: int
    n: int
    n_pos: int
    n_neg: int
    unseen_cmm_pos: int
    total_lit_pos: int
    unique_lit_herbs: int
    unique_unseen_herbs: int
    precision: float
    mcc: float
    auc: float


def _metrics(y_true: np.ndarray, y_score: np.ndarray, threshold: float = 0.5) -> dict | None:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    if len(y_true) < 10 or len(np.unique(y_true)) < 2:
        return None
    y_pred = (y_score >= threshold).astype(int)
    return {
        'n': int(len(y_true)),
        'n_pos': int((y_true == 1).sum()),
        'n_neg': int((y_true == 0).sum()),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'mcc': float(matthews_corrcoef(y_true, y_pred)),
        'auc': float(roc_auc_score(y_true, y_score)),
    }


def eval_fold_coldstart(
    fold_idx: int,
    y_true: np.ndarray,
    y_score: np.ndarray,
    test_h: np.ndarray,
    test_a: np.ndarray,
    herb_train_degree: np.ndarray,
    literature_pairs: set[tuple[int, int]],
) -> FoldColdstart | None:
    lit_mask = literature_holdout_mask(y_true, test_h, test_a, literature_pairs)
    m = _metrics(y_true[lit_mask], y_score[lit_mask])
    if not m:
        return None

    unseen = 0
    lit_pos_total = 0
    lit_herbs: set[int] = set()
    unseen_herbs: set[int] = set()
    for i in np.where(lit_mask)[0]:
        if y_true[i] != 1:
            continue
        lit_pos_total += 1
        h = int(test_h[i])
        lit_herbs.add(h)
        if herb_train_degree[h] == 0:
            unseen += 1
            unseen_herbs.add(h)

    return FoldColdstart(
        fold=fold_idx,
        unseen_cmm_pos=unseen,
        total_lit_pos=lit_pos_total,
        unique_lit_herbs=len(lit_herbs),
        unique_unseen_herbs=len(unseen_herbs),
        **m,
    )


def train_herb_degree_for_fold(fold_idx: int) -> np.ndarray:
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    train_data, test_data = extractor.load_fold_data(fold_idx)
    rng = np.random.RandomState(42 + fold_idx)
    n_dev = len(train_data['labels'])
    indices = rng.permutation(n_dev)
    n_val = int(n_dev * 0.1)
    val_sub = indices[:n_val]

    test_pos = positive_pair_set(
        test_data['herb_indices'], test_data['adr_indices'], test_data['labels']
    )
    data = remove_cmm_adr_pairs(extractor.get_graph_data().clone(), test_pos)
    pos_ei = data['herb', 'causes', 'adr'].edge_index
    return np.bincount(pos_ei[0].numpy(), minlength=data['herb'].x.size(0))


def aggregate_coldstart(folds: list[FoldColdstart]) -> dict:
    if not folds:
        return {'status': 'insufficient_samples', 'n_folds': 0}

    def agg(attr: str) -> dict:
        vals = [getattr(f, attr) for f in folds]
        return {'mean': float(np.mean(vals)), 'std': float(np.std(vals)), 'values': vals}

    unseen_total = sum(f.unseen_cmm_pos for f in folds)
    lit_pos_total = sum(f.total_lit_pos for f in folds)
    lit_herbs_total = sum(f.unique_lit_herbs for f in folds)
    unseen_herbs_total = sum(f.unique_unseen_herbs for f in folds)
    return {
        'n_folds': len(folds),
        'n_pairs_mean': float(np.mean([f.n for f in folds])),
        'n_pos_mean': float(np.mean([f.n_pos for f in folds])),
        'unseen_cmm_rate_pairs': float(unseen_total / lit_pos_total) if lit_pos_total else 0.0,
        'unseen_cmm_rate_herbs': float(unseen_herbs_total / lit_herbs_total) if lit_herbs_total else 0.0,
        'unseen_cmm_pos_total': unseen_total,
        'literature_pos_total': lit_pos_total,
        'unique_lit_herbs_total': lit_herbs_total,
        'unique_unseen_herbs_total': unseen_herbs_total,
        'precision': agg('precision'),
        'mcc': agg('mcc'),
        'auc': agg('auc'),
    }


def eval_summary_coldstart(summary: dict, lit_pairs: set[tuple[int, int]] | None = None) -> dict:
    """Evaluate Fig.5a metrics from MSAT-style summary with fold_results."""
    lit = lit_pairs if lit_pairs is not None else literature_pairs()
    if 'fold_results' not in summary:
        return {'status': 'missing_fold_results'}

    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )

    fold_rows: list[FoldColdstart] = []
    for fold_idx, fold in enumerate(summary['fold_results']):
        preds = fold['predictions']
        y_true = np.asarray(preds['y_true'])
        y_score = np.asarray(preds['y_score'])

        if 'herb_indices' in preds and 'adr_indices' in preds:
            test_h = np.asarray(preds['herb_indices'])
            test_a = np.asarray(preds['adr_indices'])
        else:
            _, test_data = extractor.load_fold_data(fold_idx)
            test_h = test_data['herb_indices']
            test_a = test_data['adr_indices']

        herb_deg = train_herb_degree_for_fold(fold_idx)
        row = eval_fold_coldstart(fold_idx, y_true, y_score, test_h, test_a, herb_deg, lit)
        if row:
            fold_rows.append(row)

    out = aggregate_coldstart(fold_rows)
    out['literature_edge_pairs_in_graph'] = len(lit)
    out['fold_details'] = [f.__dict__ for f in fold_rows]
    if 'status' not in out:
        out['status'] = 'ok'
    return out
