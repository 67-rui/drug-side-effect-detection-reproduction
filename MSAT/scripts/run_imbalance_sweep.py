#!/usr/bin/env python3
"""Fig.6 test-set imbalance sweep (train 1:1, test 1:R)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig, TrainingConfig
import train

FIG6_MODELS = ['msat', 'hgt', 'simple_hgn', 'gat']
FIG6_RATIOS = [2, 5, 10]


def run_msat(ratio: int, out_tag: str) -> None:
    DataConfig.NEG_RATIO = 1
    DataConfig.TEST_NEG_RATIO = ratio
    TrainingConfig.USE_OPTIMAL_THRESHOLD = True
    train.run_10fold_cv(experiment_tag=out_tag)


def run_gnn(name: str, ratio: int) -> dict:
    from baselines.gnn_models import run_gnn_cv

    DataConfig.NEG_RATIO = 1
    DataConfig.TEST_NEG_RATIO = ratio
    TrainingConfig.USE_OPTIMAL_THRESHOLD = True
    return run_gnn_cv(name, n_folds=DataConfig.N_FOLDS)


def main() -> None:
    parser = argparse.ArgumentParser(description='Fig.6 imbalance sweep (Phase 8D)')
    parser.add_argument('--ratio', type=int, choices=FIG6_RATIOS, help='Test neg:pos ratio')
    parser.add_argument('--model', choices=FIG6_MODELS, help='Model to run')
    parser.add_argument('--all', action='store_true', help='Run MSAT for all ratios')
    parser.add_argument('--aggregate-only', action='store_true')
    args = parser.parse_args()

    results_dir = MSAT_ROOT / 'results'
    summary_path = results_dir / 'fig6_summary.json'

    if args.aggregate_only:
        rows = []
        for ratio in FIG6_RATIOS:
            for model in FIG6_MODELS:
                if model == 'msat':
                    path = results_dir / f'summary_testneg{ratio}.json'
                else:
                    path = results_dir / f'baseline_{model}_testneg{ratio}.json'
                if not path.exists():
                    rows.append({'ratio': ratio, 'model': model, 'status': 'missing'})
                    continue
                data = json.loads(path.read_text())
                om = data['overall_metrics']
                rows.append({
                    'ratio': ratio,
                    'model': model,
                    'auc': om['auc']['mean'],
                    'auc_std': om['auc']['std'],
                    'f1': om['f1']['mean'],
                    'auprc': om['auprc']['mean'],
                    'mcc': om['mcc']['mean'],
                    'source': path.name,
                })
        payload = {'timestamp': datetime.now().isoformat(), 'rows': rows}
        summary_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        print(f'[SAVED] {summary_path}')
        return

    if args.all:
        for ratio in FIG6_RATIOS:
            run_msat(ratio, out_tag=f'testneg{ratio}')
        return

    if args.ratio and args.model:
        if args.model == 'msat':
            run_msat(args.ratio, out_tag=f'testneg{args.ratio}')
        else:
            result = run_gnn(args.model, args.ratio)
            out = results_dir / f'baseline_{args.model}_testneg{args.ratio}.json'
            out.write_text(json.dumps({**result, 'timestamp': datetime.now().isoformat()}, indent=2))
            print(f'[SAVED] {out}')
        return

    parser.error('Use --all, or --ratio R --model M, or --aggregate-only')


if __name__ == '__main__':
    main()
