#!/usr/bin/env python3
"""Phase 7 downstream explanation artifacts for MSAT reproduction."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.paper_herbs import ZHISHI_LATIN
from inference.predictor import MSATPredictor


DEFAULT_KEYWORDS = ['枳实', 'Citrus aurantium']
DIARRHEA_RE = re.compile(r'diarrh(o)?ea', flags=re.IGNORECASE)


def resolve_herb_ids(predictor: MSATPredictor, keywords: list[str]) -> list[int]:
    options = predictor.list_herb_options()
    picks: list[int] = []
    for kw in keywords:
        kw_l = kw.lower()
        for hid, label in options:
            if kw_l in label.lower():
                picks.append(hid)
        if kw_l in ZHISHI_LATIN.lower() or kw in ('枳实',):
            hid = predictor.names.paper_herb_id(ZHISHI_LATIN)
            if hid is not None:
                picks.append(hid)
        checks = predictor.names.meta.get('paper_herb_checks', []) if predictor.names.meta else []
        for row in checks:
            latin = str(row.get('latin', '')).lower()
            chinese = str(row.get('chinese', '')).lower()
            if kw_l in latin or kw_l in chinese:
                mapped = row.get('mapped_id')
                if isinstance(mapped, int):
                    picks.append(mapped)
    return list(dict.fromkeys(picks))


def pick_diarrhea_adr_id(predictor: MSATPredictor, herb_id: int) -> tuple[int, float]:
    scores = predictor.score_herb_all_adrs(herb_id)
    candidates: list[tuple[int, float]] = []
    for adr_id in range(predictor.n_adr):
        name = predictor.adr_label(adr_id)
        if DIARRHEA_RE.search(name):
            candidates.append((adr_id, float(scores[adr_id])))
    if not candidates:
        raise RuntimeError('未找到包含 diarrhoea / diarrhea 的 ADR 节点')
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description='Run Phase 7 downstream explanations')
    parser.add_argument('--top-k', type=int, default=15)
    parser.add_argument(
        '--keywords',
        nargs='*',
        default=DEFAULT_KEYWORDS,
        help='Herb keyword(s) to export Top-K ADR predictions',
    )
    parser.add_argument(
        '--out-dir',
        type=Path,
        default=MSAT_ROOT / 'results',
        help='Output directory for phase7 artifacts',
    )
    args = parser.parse_args()

    predictor = MSATPredictor()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    herb_ids = resolve_herb_ids(predictor, args.keywords)
    if not herb_ids:
        raise RuntimeError(f'未匹配到 herb，关键词: {args.keywords}')

    table_rows: list[dict] = []
    herb_payloads: list[dict] = []
    for herb_id in herb_ids:
        result = predictor.predict_herb(herb_id, top_k=args.top_k, threshold=0.5)
        herb_payloads.append(result)
        for row in result['top_adr']:
            table_rows.append(
                {
                    'herb_id': herb_id,
                    'herb': result['herb'],
                    'known_adr_count': result['known_adr_count'],
                    'rank': row['rank'],
                    'adr_id': row['adr_id'],
                    'adr': row['adr'],
                    'score': row['score'],
                    'known_edge': row['known_edge'],
                }
            )

    table_df = pd.DataFrame(table_rows)
    table_csv = out_dir / 'phase7_top15_table6_style.csv'
    table_json = out_dir / 'phase7_top15_table6_style.json'
    table_df.to_csv(table_csv, index=False, encoding='utf-8')
    table_json.write_text(json.dumps(herb_payloads, ensure_ascii=False, indent=2), encoding='utf-8')

    # Case study: Zhishi -> diarrhoea
    case_herb_id = herb_ids[0]
    diarrhea_adr_id, diarrhea_score = pick_diarrhea_adr_id(predictor, case_herb_id)
    case_result = predictor.predict_pair(case_herb_id, diarrhea_adr_id)
    case_result['diarrhea_candidate_score'] = diarrhea_score

    case_json = out_dir / 'phase7_case_zhishi_diarrhoea.json'
    case_json.write_text(json.dumps(case_result, ensure_ascii=False, indent=2), encoding='utf-8')

    summary = {
        'created_at': datetime.now().isoformat(),
        'herb_keywords': args.keywords,
        'resolved_herb_ids': herb_ids,
        'topk': args.top_k,
        'table6_csv': str(table_csv),
        'table6_json': str(table_json),
        'case_json': str(case_json),
        'case_herb': case_result['herb'],
        'case_adr': case_result['adr'],
        'case_score': case_result['score'],
        'case_rank': case_result['rank'],
        'case_rank_total': case_result['rank_total'],
        'case_known_edge': case_result['known_edge'],
        'case_paths': case_result['paths'],
    }
    summary_path = out_dir / 'phase7_summary.json'
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'[saved] {table_csv}')
    print(f'[saved] {table_json}')
    print(f'[saved] {case_json}')
    print(f'[saved] {summary_path}')
    print(
        f"[case] {summary['case_herb']} -> {summary['case_adr']} | "
        f"score={summary['case_score']:.4f}, rank={summary['case_rank']}/{summary['case_rank_total']}, "
        f"known={summary['case_known_edge']}"
    )


if __name__ == '__main__':
    main()
