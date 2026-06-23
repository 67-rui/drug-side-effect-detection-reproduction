#!/usr/bin/env python3
"""Diagnose Fig.5a / Table 5 / unseen-CMM gaps vs paper expectations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import matthews_corrcoef, precision_score, roc_auc_score

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.common import positive_pair_set, remove_cmm_adr_pairs
from config import DataConfig
from experiments.feature_extractor import FeatureExtractor
from inference.coldstart import (
    eval_summary_coldstart,
    literature_holdout_mask,
    literature_pairs,
    train_herb_degree_for_fold,
)


def load_summary(name: str) -> dict:
    path = MSAT_ROOT / 'results' / name
    return json.loads(path.read_text())


def metrics_at_threshold(y_true, y_score, threshold: float) -> dict:
    y_pred = (y_score >= threshold).astype(int)
    return {
        'threshold': threshold,
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'mcc': float(matthews_corrcoef(y_true, y_pred)),
        'auc': float(roc_auc_score(y_true, y_score)),
    }


def sweep_thresholds(y_true, y_score) -> dict:
    best_f1 = {'f1': -1.0}
    best_mcc = {'mcc': -1.0}
    for t in np.linspace(0.05, 0.95, 19):
        m = metrics_at_threshold(y_true, y_score, float(t))
        pred = (y_score >= t).astype(int)
        f1 = 2 * m['precision'] * (pred & (y_true == 1)).sum() / max(
            (pred.sum() + (y_true == 1).sum()), 1
        )
        if f1 > best_f1.get('f1', -1):
            best_f1 = {**m, 'f1': float(f1)}
        if m['mcc'] > best_mcc.get('mcc', -1):
            best_mcc = m
    return {'best_mcc': best_mcc, 'at_0.5': metrics_at_threshold(y_true, y_score, 0.5)}


def pooled_coldstart_metrics(summary: dict, lit: set[tuple[int, int]]) -> dict:
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    y_all, s_all = [], []
    for fold_idx, fold in enumerate(summary['fold_results']):
        preds = fold['predictions']
        y_true = np.asarray(preds['y_true'])
        y_score = np.asarray(preds['y_score'])
        if 'herb_indices' in preds:
            test_h = np.asarray(preds['herb_indices'])
            test_a = np.asarray(preds['adr_indices'])
        else:
            _, test_data = extractor.load_fold_data(fold_idx)
            test_h = test_data['herb_indices']
            test_a = test_data['adr_indices']
        mask = literature_holdout_mask(y_true, test_h, test_a, lit)
        y_all.append(y_true[mask])
        s_all.append(y_score[mask])
    y = np.concatenate(y_all)
    s = np.concatenate(s_all)
    return sweep_thresholds(y, s)


def unseen_cmm_diagnostics() -> dict:
    lit = literature_pairs()
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    data_full = extractor.get_graph_data()

    rates = {
        'adr_edge_degree_zero': [],
        'any_herb_causes_degree_zero': [],
        'herb_not_in_train_fold_dev': [],
        'herb_not_in_train_pos_or_neg': [],
    }

    for fold_idx in range(10):
        train_data, test_data = extractor.load_fold_data(fold_idx)
        rng = np.random.RandomState(42 + fold_idx)
        n_dev = len(train_data['labels'])
        indices = rng.permutation(n_dev)
        n_val = int(n_dev * 0.1)
        val_sub = indices[:n_val]
        train_sub = indices[n_val:]

        test_pos = positive_pair_set(
            test_data['herb_indices'], test_data['adr_indices'], test_data['labels']
        )
        data = remove_cmm_adr_pairs(data_full.clone(), test_pos)
        pos_ei = data['herb', 'causes', 'adr'].edge_index
        herb_causes_deg = np.bincount(pos_ei[0].numpy(), minlength=data['herb'].x.size(0))

        train_herbs_dev = set(train_data['herb_indices'][train_sub].tolist())
        train_herbs_all = set(train_data['herb_indices'].tolist())

        lit_pos_in_test = []
        for i in range(len(test_data['labels'])):
            if test_data['labels'][i] != 1:
                continue
            pair = (int(test_data['herb_indices'][i]), int(test_data['adr_indices'][i]))
            if pair not in lit:
                continue
            lit_pos_in_test.append(int(test_data['herb_indices'][i]))

        if not lit_pos_in_test:
            continue

        h_arr = np.array(lit_pos_in_test)
        rates['adr_edge_degree_zero'].append(float((herb_causes_deg[h_arr] == 0).mean()))
        rates['herb_not_in_train_fold_dev'].append(float(np.mean([h not in train_herbs_dev for h in h_arr])))
        rates['herb_not_in_train_pos_or_neg'].append(float(np.mean([h not in train_herbs_all for h in h_arr])))

        # any-edge degree on train graph (all edge types ending at herb)
        any_deg = np.zeros(data['herb'].x.size(0))
        for et, ei in data.edge_index_dict.items():
            if et[2] == 'herb':
                any_deg += np.bincount(ei[1].numpy(), minlength=any_deg.size)
            if et[0] == 'herb':
                any_deg += np.bincount(ei[0].numpy(), minlength=any_deg.size)
        rates['any_herb_causes_degree_zero'].append(float((any_deg[h_arr] == 0).mean()))

    return {k: {'mean': float(np.mean(v)), 'values': v} for k, v in rates.items() if v}


def table5_diagnostics() -> dict:
    from scripts.run_table5_validation import (
        collect_oof_scores,
        faers_positive_pairs,
        graph_positive_pairs,
        literature_positive_pairs,
    )

    summary_path = MSAT_ROOT / 'results' / 'summary.json'
    oof = collect_oof_scores(summary_path)
    faers = faers_positive_pairs()
    all_pos = graph_positive_pairs()
    lit = literature_positive_pairs()

    def top_k(excluded: set, k=15):
        cands = [(p, s) for p, s in oof.items() if p not in excluded]
        cands.sort(key=lambda x: x[1], reverse=True)
        return cands[:k]

    oof_top = top_k(all_pos)
    faers_top = top_k(faers)
    lit_in_top = sum(1 for p, _ in faers_top if p in lit)
    return {
        'oof_exclude_all_positives': {
            'top1_score': oof_top[0][1] if oof_top else None,
            'lit_edges_in_top15': lit_in_top,
        },
        'oof_exclude_faers_only': {
            'top1_score': faers_top[0][1] if faers_top else None,
            'lit_edges_in_top15': lit_in_top,
            'n_lit_in_graph': len(lit),
        },
        'n_faers_pairs': len(faers),
        'n_lit_pairs': len(lit),
        'n_all_pos': len(all_pos),
    }


def main() -> None:
    lit = literature_pairs()
    models = [
        ('MSAT', load_summary('summary.json')),
    ]
    cold = MSAT_ROOT / 'results' / 'coldstart_summary.json'
    if cold.exists():
        for row in json.loads(cold.read_text()).get('models', []):
            if row.get('model') == 'GAT':
                pass  # GAT not stored separately

    print('=' * 60)
    print('Fig.5a threshold sensitivity (pooled 10-fold literature hold-out)')
    print('=' * 60)
    for label, summary in [('MSAT', load_summary('summary.json'))]:
        sweep = pooled_coldstart_metrics(summary, lit)
        print(f'\n{label} @0.5: P={sweep["at_0.5"]["precision"]:.4f} MCC={sweep["at_0.5"]["mcc"]:.4f}')
        bm = sweep['best_mcc']
        print(f'{label} best-MCC @τ={bm["threshold"]:.2f}: P={bm["precision"]:.4f} MCC={bm["mcc"]:.4f}')

    if cold.exists():
        payload = json.loads(cold.read_text())
        for row in payload.get('models', []):
            if row.get('status') != 'ok':
                continue
            print(
                f'{row["model"]:12s} reported: P={row["precision"]["mean"]:.4f} '
                f'MCC={row["mcc"]["mean"]:.4f} AUC={row["auc"]["mean"]:.4f}'
            )

    print('\n' + '=' * 60)
    print('Unseen CMM rate definitions (literature positives in test fold)')
    print('=' * 60)
    unseen = unseen_cmm_diagnostics()
    for name, block in unseen.items():
        print(f'  {name:32s} mean={block["mean"]:.4f}')

    print('\n' + '=' * 60)
    print('Table 5 candidate pool diagnostics (OOF scores)')
    print('=' * 60)
    t5 = table5_diagnostics()
    print(json.dumps(t5, indent=2))

    out = MSAT_ROOT / 'results' / 'reproduction_gap_diagnosis.json'
    out.write_text(
        json.dumps(
            {
                'unseen_cmm': unseen,
                'table5': t5,
                'coldstart_reported': [
                    {k: row[k] for k in ('model', 'precision', 'mcc', 'auc') if k in row}
                    for row in json.loads(cold.read_text()).get('models', [])
                    if row.get('status') == 'ok'
                ]
                if cold.exists()
                else [],
            },
            indent=2,
        ),
        encoding='utf-8',
    )
    print(f'\n[SAVED] {out}')


if __name__ == '__main__':
    main()
