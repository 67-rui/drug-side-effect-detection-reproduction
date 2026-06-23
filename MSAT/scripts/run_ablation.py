#!/usr/bin/env python3
"""Run MSAT ablation variants (Table 3) and aggregate results."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import ModelConfig
import train

ABLATION_VARIANTS = {
    'full': {
        'USE_GATED_EDGE_ENCODER': True,
        'USE_BOTTLENECK_TRANSFORM': True,
        'USE_LATE_FUSION': True,
    },
    'wo_esa': {
        'USE_GATED_EDGE_ENCODER': False,
        'USE_BOTTLENECK_TRANSFORM': True,
        'USE_LATE_FUSION': True,
    },
    'wo_hsp': {
        'USE_GATED_EDGE_ENCODER': True,
        'USE_BOTTLENECK_TRANSFORM': False,
        'USE_LATE_FUSION': True,
    },
    'wo_hci': {
        'USE_GATED_EDGE_ENCODER': True,
        'USE_BOTTLENECK_TRANSFORM': True,
        'USE_LATE_FUSION': False,
    },
    'only_esa': {
        'USE_GATED_EDGE_ENCODER': True,
        'USE_BOTTLENECK_TRANSFORM': False,
        'USE_LATE_FUSION': False,
    },
    'only_hsp': {
        'USE_GATED_EDGE_ENCODER': False,
        'USE_BOTTLENECK_TRANSFORM': True,
        'USE_LATE_FUSION': False,
    },
    'only_hci': {
        'USE_GATED_EDGE_ENCODER': False,
        'USE_BOTTLENECK_TRANSFORM': False,
        'USE_LATE_FUSION': True,
    },
}


def apply_variant(name: str) -> None:
    flags = ABLATION_VARIANTS[name]
    ModelConfig.USE_GATED_EDGE_ENCODER = flags['USE_GATED_EDGE_ENCODER']
    ModelConfig.USE_BOTTLENECK_TRANSFORM = flags['USE_BOTTLENECK_TRANSFORM']
    ModelConfig.USE_LATE_FUSION = flags['USE_LATE_FUSION']


def load_summary(tag: str) -> dict:
    if tag:
        path = MSAT_ROOT / 'results' / f'summary_{tag}.json'
    else:
        path = MSAT_ROOT / 'results' / 'summary.json'
    with open(path) as f:
        return json.load(f)


def aggregate(variant_names: list[str]) -> dict:
    rows = []
    for name in variant_names:
        tag = '' if name == 'full' else name
        path = MSAT_ROOT / 'results' / (f'summary_{tag}.json' if tag else 'summary.json')
        if not path.exists():
            rows.append({'variant': name, 'status': 'missing'})
            continue
        summary = load_summary(tag)
        om = summary['overall_metrics']
        rows.append({
            'variant': name,
            'flags': ABLATION_VARIANTS[name],
            'auc': om['auc']['mean'],
            'auc_std': om['auc']['std'],
            'auprc': om['auprc']['mean'],
            'f1': om['f1']['mean'],
            'mcc': om['mcc']['mean'],
        })

    return {
        'timestamp': datetime.now().isoformat(),
        'variants': rows,
        'expected_trend': 'full > wo_hsp > wo_esa > wo_hci; only_* < full',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Run MSAT ablation study (Table 3)')
    parser.add_argument(
        '--variant',
        choices=list(ABLATION_VARIANTS.keys()),
        help='Run a single ablation variant (10-fold CV)',
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run wo_esa, wo_hsp, wo_hci sequentially (skip full if summary.json exists)',
    )
    parser.add_argument(
        '--only',
        action='store_true',
        help='Run only_esa, only_hsp, only_hci sequentially',
    )
    parser.add_argument(
        '--aggregate-only',
        action='store_true',
        help='Only build ablation_summary.json from existing result files',
    )
    args = parser.parse_args()

    all_variants = list(ABLATION_VARIANTS.keys())

    if args.aggregate_only:
        out = aggregate(all_variants)
        out_path = MSAT_ROOT / 'results' / 'ablation_summary.json'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump(out, f, indent=2)
        print(f'[SAVED] {out_path}')
        for row in out['variants']:
            if 'auc' in row:
                print(f"  {row['variant']:8s} AUC={row['auc']:.4f}")
        return

    if args.only:
        for name in ('only_esa', 'only_hsp', 'only_hci'):
            apply_variant(name)
            print(f'\n{"=" * 80}\nRunning ablation: {name}\n{"=" * 80}')
            train.run_10fold_cv(experiment_tag=name)
        out = aggregate(all_variants)
        out_path = MSAT_ROOT / 'results' / 'ablation_summary.json'
        with open(out_path, 'w') as f:
            json.dump(out, f, indent=2)
        print(f'\n[SAVED] {out_path}')
        return

    if args.all:
        for name in ('wo_esa', 'wo_hsp', 'wo_hci'):
            apply_variant(name)
            print(f'\n{"=" * 80}\nRunning ablation: {name}\n{"=" * 80}')
            train.run_10fold_cv(experiment_tag=name)
        out = aggregate(all_variants)
        out_path = MSAT_ROOT / 'results' / 'ablation_summary.json'
        with open(out_path, 'w') as f:
            json.dump(out, f, indent=2)
        print(f'\n[SAVED] {out_path}')
        return

    if not args.variant:
        parser.error('Specify --variant NAME or --all')

    apply_variant(args.variant)
    tag = '' if args.variant == 'full' else args.variant
    train.run_10fold_cv(experiment_tag=tag)


if __name__ == '__main__':
    main()
