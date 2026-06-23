#!/usr/bin/env python3
"""Degree stratification and cold-start analysis (Phase 6 Task 6.3, Fig.5)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.common import positive_pair_set, prepare_fold, remove_cmm_adr_pairs
from config import DataConfig
from experiments.feature_extractor import FeatureExtractor


def _subset_metrics(y_true, y_score, threshold=0.5) -> dict | None:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    if len(y_true) < 10 or len(np.unique(y_true)) < 2:
        return None
    pred = (y_score >= threshold).astype(int)
    return {
        'n': int(len(y_true)),
        'n_pos': int((y_true == 1).sum()),
        'auc': float(roc_auc_score(y_true, y_score)),
        'auprc': float(average_precision_score(y_true, y_score)),
        'f1': float(f1_score(y_true, pred, zero_division=0)),
    }


def _build_literature_pairs() -> set[tuple[int, int]]:
    graph_path = DataConfig.GRAPH_PATH
    data = torch.load(graph_path, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    lit_mask = ea[:, 2].numpy() == 0
    pairs = set(
        (int(h), int(a))
        for h, a in zip(ei[0].numpy()[lit_mask], ei[1].numpy()[lit_mask])
    )
    return pairs


def analyze_fold(fold_idx: int, summary_path: Path, literature_pairs: set[tuple[int, int]]) -> dict:
    with open(summary_path) as f:
        summary = json.load(f)

    fold_result = summary['fold_results'][fold_idx]
    preds = fold_result['predictions']
    y_true = np.asarray(preds['y_true'])
    y_score = np.asarray(preds['y_score'])

    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    train_data, test_data = extractor.load_fold_data(fold_idx)

    rng = np.random.RandomState(42 + fold_idx)
    n_dev = len(train_data['labels'])
    indices = rng.permutation(n_dev)
    n_val = int(n_dev * (1 - 0.9))
    val_sub = indices[:n_val]

    test_pos = positive_pair_set(
        test_data['herb_indices'], test_data['adr_indices'], test_data['labels']
    )

    data = extractor.get_graph_data()
    data = remove_cmm_adr_pairs(data.clone(), test_pos)
    pos_ei = data['herb', 'causes', 'adr'].edge_index
    herb_degree = np.bincount(pos_ei[0].numpy(), minlength=data['herb'].x.size(0))

    test_h = test_data['herb_indices']
    test_a = test_data['adr_indices']

    pos_mask = y_true == 1
    test_pos_degrees = herb_degree[test_h[pos_mask]]
    q33, q66 = np.percentile(test_pos_degrees, [33.33, 66.67])

    def degree_group(h_idx):
        d = herb_degree[h_idx]
        if d >= q66:
            return 'head'
        if d >= q33:
            return 'medium'
        return 'tail'

    groups = {'head': [], 'medium': [], 'tail': []}
    for i in range(len(y_true)):
        g = degree_group(test_h[i])
        groups[g].append(i)

    group_metrics = {}
    for name, idxs in groups.items():
        idxs = np.asarray(idxs)
        m = _subset_metrics(y_true[idxs], y_score[idxs])
        if m:
            group_metrics[name] = m

    lit_mask = np.zeros(len(y_true), dtype=bool)
    for i in range(len(y_true)):
        pair = (int(test_h[i]), int(test_a[i]))
        if y_true[i] == 0:
            lit_mask[i] = True
        elif pair in literature_pairs:
            lit_mask[i] = True

    literature_metrics = _subset_metrics(y_true[lit_mask], y_score[lit_mask])

    cold_mask = herb_degree[test_h] == 0
    cold_start_metrics = _subset_metrics(y_true[cold_mask], y_score[cold_mask])

    return {
        'fold': fold_idx,
        'degree_tertiles_on_test_pos': {'q33': float(q33), 'q66': float(q66)},
        'degree_groups': group_metrics,
        'literature_positives': literature_metrics,
        'zero_degree_herb_pairs': cold_start_metrics,
    }


def aggregate_stratified(fold_rows: list[dict]) -> dict:
    def agg_block(key_path: tuple[str, ...]):
        vals_auc, vals_f1, ns = [], [], []
        for row in fold_rows:
            cur = row
            for k in key_path:
                cur = cur.get(k) if cur else None
            if cur and 'auc' in cur:
                vals_auc.append(cur['auc'])
                vals_f1.append(cur['f1'])
                ns.append(cur['n'])
        if not vals_auc:
            return None
        return {
            'auc_mean': float(np.mean(vals_auc)),
            'auc_std': float(np.std(vals_auc)),
            'f1_mean': float(np.mean(vals_f1)),
            'avg_n': float(np.mean(ns)),
            'fold_aucs': vals_auc,
        }

    return {
        'head': agg_block(('degree_groups', 'head')),
        'medium': agg_block(('degree_groups', 'medium')),
        'tail': agg_block(('degree_groups', 'tail')),
        'literature_positives': agg_block(('literature_positives',)),
        'zero_degree_herb_pairs': agg_block(('zero_degree_herb_pairs',)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='MSAT stratified / cold-start analysis')
    parser.add_argument(
        '--summary',
        default=str(MSAT_ROOT / 'results' / 'summary.json'),
        help='Path to MSAT summary.json with per-fold predictions',
    )
    parser.add_argument(
        '--output',
        default=str(MSAT_ROOT / 'results' / 'stratified_summary.json'),
    )
    args = parser.parse_args()

    summary_path = Path(args.summary)
    literature_pairs = _build_literature_pairs()
    print(f'Literature CMM-ADR pairs in graph: {len(literature_pairs)}')

    fold_rows = []
    for fold_idx in range(10):
        print(f'Analyzing fold {fold_idx + 1}/10...')
        fold_rows.append(analyze_fold(fold_idx, summary_path, literature_pairs))

    overall = aggregate_stratified(fold_rows)
    out = {
        'timestamp': datetime.now().isoformat(),
        'source_summary': str(summary_path),
        'fold_results': fold_rows,
        'overall': overall,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'[SAVED] {out_path}')

    for group in ['head', 'medium', 'tail', 'literature_positives', 'zero_degree_herb_pairs']:
        block = overall.get(group)
        if block:
            print(f"  {group:24s} AUC={block['auc_mean']:.4f} ± {block['auc_std']:.4f}")


if __name__ == '__main__':
    main()
