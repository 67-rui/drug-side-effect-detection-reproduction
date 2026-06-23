#!/usr/bin/env python3
"""Build tcmda_cache.json rows from Table 5 CSV + entity names (manual phenotype fill-in)."""

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


def main() -> None:
    parser = argparse.ArgumentParser(description='Template TCMDA cache from Table 5 Top-15')
    parser.add_argument(
        '--input',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table5_top15.csv',
    )
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'data' / 'tcmda_cache.json',
    )
    args = parser.parse_args()

    names = EntityNames.load()
    df = pd.read_csv(args.input)
    entries = []
    for _, row in df.iterrows():
        h = int(row['herb_id'])
        rec = names.herbs.get(h)
        aliases = []
        for v in (row.get('chinese'), row.get('latin'), row.get('pinyin'), rec.chinese if rec else None, rec.latin if rec else None, rec.pinyin if rec else None):
            if v and str(v).strip() and str(v) not in aliases:
                aliases.append(str(v).strip())
        entries.append({
            'herb_query': aliases[0] if aliases else f'herb_{h}',
            'herb_aliases': aliases,
            'adverse_phenotypes': [],
            'source_url': None,
            'notes': f"Fill after TCMDA lookup for ADR: {row['adr_pt']}",
            'predicted_adr_pt': str(row['adr_pt']),
            'verified_at': None,
            'verified_by': None,
        })

    payload = {
        'updated_at': datetime.now().isoformat(),
        'source': 'https://organchem.csdb.cn/',
        'instructions': (
            'Login → 中药成分毒副作用数据库 or 中药药材检索 → '
            'record adverse phenotypes in adverse_phenotypes (CN/EN); '
            'set verified_at when done.'
        ),
        'entries': entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'[SAVED] {args.out} ({len(entries)} template rows)')


if __name__ == '__main__':
    main()
