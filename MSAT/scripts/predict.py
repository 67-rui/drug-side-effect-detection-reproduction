#!/usr/bin/env python3
"""CLI for MSAT CMM–ADR link prediction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.predictor import MSATPredictor


def main() -> None:
    parser = argparse.ArgumentParser(description='MSAT CMM–ADR link prediction')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_herb = sub.add_parser('herb', help='Top-K ADR for one CMM')
    p_herb.add_argument('herb_id', type=int)
    p_herb.add_argument('--top-k', type=int, default=15)
    p_herb.add_argument('--threshold', type=float, default=0.5)

    p_pair = sub.add_parser('pair', help='Score one CMM–ADR pair')
    p_pair.add_argument('herb_id', type=int)
    p_pair.add_argument('adr_id', type=int)

    p_formula = sub.add_parser('formula', help='Aggregate multiple CMM nodes')
    p_formula.add_argument('herb_ids', type=int, nargs='+')
    p_formula.add_argument('--mode', choices=['max', 'mean'], default='max')
    p_formula.add_argument('--top-k', type=int, default=15)

    args = parser.parse_args()
    predictor = MSATPredictor()

    if args.cmd == 'herb':
        out = predictor.predict_herb(args.herb_id, top_k=args.top_k, threshold=args.threshold)
    elif args.cmd == 'pair':
        out = predictor.predict_pair(args.herb_id, args.adr_id)
    else:
        out = predictor.predict_formula(args.herb_ids, mode=args.mode, top_k=args.top_k)

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
