#!/usr/bin/env python3
"""Fig.5a cold-start: FAERS-only train graph vs literature evaluation (paper §3.5.4)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import matthews_corrcoef, precision_score, roc_auc_score

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from experiments.feature_extractor import FeatureExtractor
from inference.coldstart import eval_summary_coldstart, literature_pairs


def faers_herb_set() -> set[int]:
    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    faers_mask = ea[:, 2].numpy() > 0.5
    return set(ei[0].numpy()[faers_mask].tolist())


def literature_unseen_stats() -> dict:
    lit = literature_pairs()
    faers_herbs = faers_herb_set()
    lit_herbs = {h for h, _ in lit}
    unseen_herbs = lit_herbs - faers_herbs
    unseen_pairs = [(h, a) for h, a in lit if h not in faers_herbs]
    return {
        'literature_pairs_in_graph': len(lit),
        'literature_unique_herbs': len(lit_herbs),
        'faers_unique_herbs': len(faers_herbs),
        'unseen_herb_rate': len(unseen_herbs) / len(lit_herbs) if lit_herbs else 0.0,
        'unseen_pair_rate': len(unseen_pairs) / len(lit) if lit else 0.0,
        'unseen_herbs': len(unseen_herbs),
        'unseen_pairs': len(unseen_pairs),
        'paper_target_unseen_pct': 0.965,
    }


def eval_unseen_literature_subset(summary_path: Path) -> dict:
    """Evaluate MSAT on literature pairs whose CMM herb has no FAERS supervision edge."""
    lit = literature_pairs()
    faers_herbs = faers_herb_set()
    summary = json.loads(summary_path.read_text())
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )

    y_true_all, y_score_all = [], []
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

        for i in range(len(y_true)):
            pair = (int(test_h[i]), int(test_a[i]))
            if pair not in lit or int(test_h[i]) in faers_herbs:
                continue
            y_true_all.append(int(y_true[i]))
            y_score_all.append(float(y_score[i]))

    y_true = np.asarray(y_true_all)
    y_score = np.asarray(y_score_all)
    if len(y_true) < 10 or len(np.unique(y_true)) < 2:
        return {'status': 'insufficient_samples', 'n': int(len(y_true))}

    y_pred = (y_score >= 0.5).astype(int)
    return {
        'status': 'ok',
        'n': int(len(y_true)),
        'n_pos': int((y_true == 1).sum()),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'mcc': float(matthews_corrcoef(y_true, y_pred)),
        'auc': float(roc_auc_score(y_true, y_score)),
        'note': (
            'Approximation: MSAT was trained on full curated graph in 10-fold CV, '
            'not FAERS-only. Paper §3.5.4 requires FAERS-only training for true Fig.5a.'
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='FAERS→literature cold-start diagnostics')
    parser.add_argument(
        '--summary',
        type=Path,
        default=MSAT_ROOT / 'results' / 'summary.json',
    )
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'faers_literature_coldstart.json',
    )
    args = parser.parse_args()

    stats = literature_unseen_stats()
    cv_proxy = eval_summary_coldstart(json.loads(args.summary.read_text()))
    unseen_subset = eval_unseen_literature_subset(args.summary)

    payload = {
        'created_at': datetime.now().isoformat(),
        'protocol_paper': 'Train FAERS-only; evaluate literature expert-curated hold-out (§3.5.4)',
        'unseen_cmm_stats': stats,
        'cv_literature_holdout_proxy': {
            k: cv_proxy[k]
            for k in (
                'precision', 'mcc', 'auc', 'n_pairs_mean', 'n_pos_mean',
                'unseen_cmm_rate_herbs', 'status',
            )
            if k in cv_proxy
        },
        'unseen_herb_literature_subset': unseen_subset,
        'next_step': 'Retrain MSAT on FAERS-only edges (25734) then evaluate literature pairs',
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f'[SAVED] {args.out}')
    print(f"unseen_herb_rate={stats['unseen_herb_rate']:.1%} (paper target 96.5%)")
    if unseen_subset.get('status') == 'ok':
        print(
            f"unseen-subset MSAT: P={unseen_subset['precision']:.4f} "
            f"MCC={unseen_subset['mcc']:.4f} AUC={unseen_subset['auc']:.4f} "
            f"n={unseen_subset['n']}"
        )


if __name__ == '__main__':
    main()
