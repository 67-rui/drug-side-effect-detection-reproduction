#!/usr/bin/env python3
"""Run Fig.5a cold-start eval for GNN baselines (Phase 9E+, requires GPU)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.gnn_models import train_eval_gnn
from baselines.common import prepare_fold
from inference.coldstart import eval_summary_coldstart, literature_pairs

import torch


GNN_MODELS = ['gat', 'hgt', 'simple_hgn']


def run_coldstart_gnn(model_name: str, n_folds: int, device: torch.device) -> dict:
    fold_results = []
    for fold_idx in range(n_folds):
        print(f'  [{model_name}] fold {fold_idx + 1}/{n_folds}')
        fold = prepare_fold(fold_idx)
        metrics = train_eval_gnn(model_name, fold, device)
        preds = metrics.pop('predictions')
        fold_results.append({'predictions': preds})
        print(f"    AUC={metrics['auc']:.4f} MCC={metrics['mcc']:.4f}")

    summary = {'fold_results': fold_results}
    return eval_summary_coldstart(summary, literature_pairs())


def merge_coldstart_models(out_path: Path, new_rows: list[dict]) -> dict:
    payload = {'timestamp': datetime.now().isoformat(), 'models': [], 'protocol': 'Fig.5a literature hold-out'}
    if out_path.exists():
        payload = json.loads(out_path.read_text())
    for row in new_rows:
        payload['models'] = [m for m in payload.get('models', []) if m.get('model') != row.get('model')]
        payload['models'].append(row)
    payload['timestamp'] = datetime.now().isoformat()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='GNN cold-start eval (Fig.5a)')
    parser.add_argument('--models', nargs='+', default=GNN_MODELS)
    parser.add_argument('--n-folds', type=int, default=10)
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'coldstart_summary.json',
    )
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    out_path = args.out

    new_rows = []
    for name in args.models:
        display = 'Simple-HGN' if name == 'simple_hgn' else name.upper()
        row = {'model': display, **run_coldstart_gnn(name, args.n_folds, device)}
        new_rows.append(row)

    payload = merge_coldstart_models(out_path, new_rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f'[SAVED] {out_path}')


if __name__ == '__main__':
    main()
