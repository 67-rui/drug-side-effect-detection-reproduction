#!/usr/bin/env python3
"""Legacy 10-fold CV literature subset (NOT paper §3.5.4 Fig.5a)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.coldstart import eval_summary_coldstart, literature_pairs


DEFAULT_GNN = ['gat', 'hgt', 'simple_hgn']


def main() -> None:
    parser = argparse.ArgumentParser(description='Cold-start / literature eval (Fig.5a)')
    parser.add_argument(
        '--summary',
        type=Path,
        default=MSAT_ROOT / 'results' / 'summary.json',
        help='Summary JSON with fold_results and per-fold predictions',
    )
    parser.add_argument('--model-name', default='MSAT')
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'coldstart_summary.json',
    )
    parser.add_argument(
        '--all-models',
        action='store_true',
        help='Also evaluate GAT/HGT/Simple-HGN if fold_results exist in baseline JSON',
    )
    parser.add_argument('--aggregate-only', action='store_true')
    args = parser.parse_args()
    print(
        'WARNING: 10-fold CV literature subset is NOT paper Fig.5a (§3.5.4). '
        'Use scripts/run_faers_only_coldstart_train.py instead.'
    )

    lit = literature_pairs()
    out_path = args.out

    if args.aggregate_only and out_path.exists():
        payload = json.loads(out_path.read_text())
    else:
        payload = {
            'timestamp': datetime.now().isoformat(),
            'models': [],
            'protocol': 'legacy_10fold_cv_literature_subset_not_paper_fig5a',
        }

    def add_model(name: str, summary_path: Path) -> None:
        if not summary_path.is_file():
            print(f'[SKIP] {name}: missing {summary_path}')
            return
        summary = json.loads(summary_path.read_text())
        metrics = eval_summary_coldstart(summary, lit)
        row = {'model': name, 'summary': str(summary_path), **metrics}
        payload['models'] = [m for m in payload.get('models', []) if m.get('model') != name]
        payload['models'].append(row)
        print(json.dumps({k: row[k] for k in row if k != 'fold_details'}, indent=2))

    add_model(args.model_name, args.summary)

    if args.all_models:
        print('[INFO] GNN models require fold predictions; run scripts/run_coldstart_gnn.py on GPU.')

    payload['timestamp'] = datetime.now().isoformat()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f'[SAVED] {out_path}')


if __name__ == '__main__':
    main()
