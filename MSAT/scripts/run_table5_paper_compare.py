#!/usr/bin/env python3
"""Compare reproduction Table 5 against paper reference (NON-PAPER legacy helper)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.entity_mapping import EntityNames
from inference.external_validation import load_paper_table5_evidence, paper_herb_evidence_for_prediction
from inference.graph_utils import explain_herb_adr
from scripts.run_table5_validation import (
    collect_oof_scores,
    graph_positive_pairs,
)


def paper_herb_top1_rows(names: EntityNames, scores: dict, positives: set) -> list[dict]:
    evidence_path = MSAT_ROOT / 'data' / 'paper_table5_reference.json'
    payload = json.loads(evidence_path.read_text(encoding='utf-8'))
    import torch
    from config import DataConfig

    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    rows = []
    for ref in payload['rows']:
        latin = ref['latin']
        herb_id = names.paper_herb_id(latin)
        if herb_id is None:
            continue
        best_adr, best_score = None, -1.0
        for (h, a), sc in scores.items():
            if h != herb_id or (h, a) in positives:
                continue
            if sc > best_score:
                best_adr, best_score = a, sc
        if best_adr is None:
            continue
        paths = explain_herb_adr(
            data, herb_id, best_adr,
            herb_label=names.herb_display(herb_id),
            adr_label=names.adr_display(best_adr),
        )
        mechanistic = any('成分介导' in p or '共享靶点' in p for p in paths)
        adr_pt = names.adr_display(best_adr)
        paper_ev = paper_herb_evidence_for_prediction(latin, adr_pt)
        paper_ev_on_ref_adr = paper_herb_evidence_for_prediction(latin, ref['adr_pt'])
        db_verified = bool(
            (paper_ev and paper_ev.get('database_verified'))
            or (paper_ev_on_ref_adr and paper_ev_on_ref_adr.get('database_verified') and ref['adr_pt'].lower() in adr_pt.lower())
        )
        mech_paper = bool(
            (paper_ev and paper_ev.get('mechanistic_support'))
            or (paper_ev_on_ref_adr and paper_ev_on_ref_adr.get('mechanistic_support'))
        )
        rows.append({
            'latin': latin,
            'pinyin': ref['pinyin'],
            'herb_id': herb_id,
            'adr_id': best_adr,
            'adr_pt': adr_pt,
            'score_pct': round(best_score * 100, 3),
            'paper_adr_pt': ref['adr_pt'],
            'adr_match_paper': ref['adr_pt'].lower() in adr_pt.lower() or adr_pt.lower() in ref['adr_pt'].lower(),
            'paper_score_pct': ref['score_pct'],
            'database_verified': db_verified,
            'mechanistic_support': mechanistic or mech_paper,
            'paper_db_verified': ref.get('database_verified'),
            'paper_mechanistic': ref.get('mechanistic_support'),
        })
    rows.sort(key=lambda r: r['score_pct'], reverse=True)
    for i, r in enumerate(rows, start=1):
        r['rank'] = i
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description='Table 5 paper comparison (legacy, non-paper protocol)')
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Required: this script is not paper §3.5.6 Top-15 protocol',
    )
    parser.add_argument(
        '--summary',
        type=Path,
        default=MSAT_ROOT / 'results' / 'summary.json',
    )
    parser.add_argument(
        '--out-dir',
        type=Path,
        default=MSAT_ROOT / 'results',
    )
    args = parser.parse_args()
    if not args.legacy:
        print('ERROR: run_table5_paper_compare.py is a legacy helper, not paper §3.5.6.')
        print('Use: python scripts/run_table5_validation.py')
        sys.exit(1)

    names = EntityNames.load()
    positives = graph_positive_pairs()
    scores = collect_oof_scores(args.summary)
    rows = paper_herb_top1_rows(names, scores, positives)

    supported = sum(1 for r in rows if r['database_verified'] or r['mechanistic_support'])
    adr_matches = sum(1 for r in rows if r['adr_match_paper'])

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / 'table5_paper_compare.csv'
    json_path = out_dir / 'table5_paper_compare.json'
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    payload = {
        'created_at': datetime.now().isoformat(),
        'mode': 'paper_herb_top1_oof',
        'excluded': 'all_labeled_positives_27062',
        'n_rows': len(rows),
        'adr_match_paper': adr_matches,
        'support_rate': supported / len(rows) if rows else 0.0,
        'supported_count': supported,
        'paper_reference_support_rate': 13 / 15,
        'rows': rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'[SAVED] {csv_path}')
    print(f'[SAVED] {json_path}')
    print(f'ADR match paper: {adr_matches}/{len(rows)}')
    print(f'Support (DB|mech): {supported}/{len(rows)} = {payload["support_rate"]:.1%}')


if __name__ == '__main__':
    main()
