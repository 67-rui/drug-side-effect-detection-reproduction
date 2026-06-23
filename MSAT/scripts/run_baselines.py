#!/usr/bin/env python3
"""Run Table 2 baseline comparison (Phase 6 Task 6.2)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

ML_MODELS = ['lr', 'rf', 'xgb']
GNN_MODELS = ['gcn', 'gat', 'rgcn', 'hgt', 'hetnn', 'simple_hgn']
ALL_MODELS = ML_MODELS + GNN_MODELS


def load_msat_reference(neg_suffix: str = '') -> dict | None:
    name = 'summary_neg10.json' if neg_suffix else 'summary.json'
    path = MSAT_ROOT / 'results' / name
    if not path.exists():
        return None
    with open(path) as f:
        summary = json.load(f)
    om = summary['overall_metrics']
    return {
        'model': 'msat',
        'overall_metrics': om,
        'source': str(path),
    }


def save_model_result(result: dict, neg_suffix: str = '') -> Path:
    out_dir = MSAT_ROOT / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"baseline_{result['model']}{neg_suffix}.json"
    with open(path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f'[SAVED] {path}')
    return path


def aggregate_existing(models: list[str], neg_suffix: str = '', summary_name: str | None = None) -> dict:
    rows = []
    msat = load_msat_reference(neg_suffix)
    if msat:
        om = msat['overall_metrics']
        rows.append({
            'model': 'MSAT',
            'auc': om['auc']['mean'],
            'auc_std': om['auc']['std'],
            'f1': om['f1']['mean'],
            'auprc': om['auprc']['mean'],
            'mcc': om['mcc']['mean'],
            'source': summary_name or ('summary_neg10.json' if neg_suffix else 'summary.json'),
        })

    for name in models:
        path = MSAT_ROOT / 'results' / f'baseline_{name}{neg_suffix}.json'
        if not path.exists():
            rows.append({'model': name, 'status': 'missing'})
            continue
        with open(path) as f:
            data = json.load(f)
        om = data['overall_metrics']
        rows.append({
            'model': name.upper() if len(name) <= 4 else name,
            'auc': om['auc']['mean'],
            'auc_std': om['auc']['std'],
            'f1': om['f1']['mean'],
            'auprc': om['auprc']['mean'],
            'mcc': om['mcc']['mean'],
            'source': path.name,
        })

    out = {
        'timestamp': datetime.now().isoformat(),
        'models': rows,
    }
    out_path = MSAT_ROOT / 'results' / (
        'baseline_neg10_summary.json' if neg_suffix else 'baseline_summary.json'
    )
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'[SAVED] {out_path}')
    return out


def run_model(name: str, n_folds: int) -> dict:
    if name in ML_MODELS:
        from baselines.ml_models import run_ml_cv
        return run_ml_cv(name, n_folds=n_folds)

    if name in GNN_MODELS:
        from baselines.gnn_models import run_gnn_cv
        return run_gnn_cv(name, n_folds=n_folds)

    raise ValueError(f'Unknown model: {name}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run MSAT baseline comparison (Table 2)')
    parser.add_argument('--model', choices=ALL_MODELS, help='Run a single baseline')
    parser.add_argument('--ml', action='store_true', help='Run all ML baselines')
    parser.add_argument('--gnn', action='store_true', help='Run all GNN baselines')
    parser.add_argument('--all', action='store_true', help='Run all 9 baselines')
    parser.add_argument('--n-folds', type=int, default=10)
    parser.add_argument(
        '--neg-ratio',
        type=int,
        default=1,
        choices=[1, 10],
        help='Negative sampling ratio (10 = Table 4 end-to-end imbalanced)',
    )
    parser.add_argument('--aggregate-only', action='store_true')
    args = parser.parse_args()

    neg_suffix = '_neg10' if args.neg_ratio == 10 else ''

    if args.neg_ratio == 10:
        from config import DataConfig, TrainingConfig
        DataConfig.NEG_RATIO = 10
        DataConfig.TEST_NEG_RATIO = 10
        TrainingConfig.USE_OPTIMAL_THRESHOLD = True

    if args.aggregate_only:
        aggregate_existing(ALL_MODELS, neg_suffix=neg_suffix)
        return

    if args.all:
        targets = ALL_MODELS
    elif args.ml:
        targets = ML_MODELS
    elif args.gnn:
        targets = GNN_MODELS
    elif args.model:
        targets = [args.model]
    else:
        parser.error('Specify --model NAME, --ml, --gnn, --all, or --aggregate-only')

    for name in targets:
        print(f'\n{"=" * 80}\nBaseline: {name}\n{"=" * 80}')
        result = {
            **run_model(name, args.n_folds),
            'timestamp': datetime.now().isoformat(),
            'n_folds': args.n_folds,
        }
        save_model_result(result, neg_suffix=neg_suffix)

    aggregate_existing(ALL_MODELS, neg_suffix=neg_suffix)


if __name__ == '__main__':
    main()
