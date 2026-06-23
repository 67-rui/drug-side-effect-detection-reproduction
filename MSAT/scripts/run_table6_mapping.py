#!/usr/bin/env python3
"""Map Table 5 ADRs to TCM systems (Table 6, Phase 8F)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.tcm_mapping import map_adr_to_tcm_systems


def main() -> None:
    parser = argparse.ArgumentParser(description='Table 6 TCM mapping export')
    parser.add_argument(
        '--input',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table5_top15.csv',
    )
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table6_mapping.csv',
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df['tcm_system_mapping'] = df['adr_pt'].map(lambda pt: map_adr_to_tcm_systems(str(pt)))
    df.to_csv(args.out, index=False)

    summary = {
        'created_at': datetime.now().isoformat(),
        'input': str(args.input),
        'output': str(args.out),
        'n_rows': len(df),
    }
    summary_path = args.out.with_suffix('.json')
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[SAVED] {args.out}')
    print(f'[SAVED] {summary_path}')


if __name__ == '__main__':
    main()
