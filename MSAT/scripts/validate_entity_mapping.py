#!/usr/bin/env python3
"""Validate entity_names.json (Phase 8A gate)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.paper_herbs import PAPER_HERB_SEEDS

DEFAULT_PATH = MSAT_ROOT / 'data' / 'entity_names.json'


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f'missing file: {path}']

    payload = json.loads(path.read_text(encoding='utf-8'))
    herbs = payload.get('herbs', {})
    adrs = payload.get('adrs', {})
    meta = payload.get('meta', {})

    if len(herbs) != 651:
        errors.append(f'expected 651 herbs, got {len(herbs)}')
    if len(adrs) != 5974:
        errors.append(f'expected 5974 adrs, got {len(adrs)}')

    id_map = meta.get('paper_herb_id_map', {})
    if not id_map:
        errors.append('meta.paper_herb_id_map is empty')
    else:
        seen_ids: set[int] = set()
        for seed in PAPER_HERB_SEEDS:
            latin = seed['latin']
            hid = id_map.get(latin)
            if hid is None:
                errors.append(f'paper seed not mapped: {latin} ({seed.get("chinese")})')
                continue
            hid = int(hid)
            if hid in seen_ids:
                errors.append(f'duplicate paper herb node id {hid} for {latin}')
            seen_ids.add(hid)
            rec = herbs.get(str(hid), {})
            if not rec:
                errors.append(f'paper mapped herb_id {hid} missing from herbs dict')

    primaries = [v.get('primary') for v in herbs.values() if v.get('primary')]
    dup = len(primaries) - len(set(primaries))
    if dup > 50:
        errors.append(f'too many duplicate herb primary labels: {dup}')

    method = meta.get('method', '')
    if 'linear assignment' not in method.lower() and 'hungarian' not in method.lower():
        errors.append(f'unexpected mapping method: {method!r}')

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate MSAT entity mapping (Phase 8A)')
    parser.add_argument('--path', type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()

    errors = validate(args.path)
    if errors:
        print('[FAIL] entity mapping validation')
        for e in errors:
            print(f'  - {e}')
        sys.exit(1)

    payload = json.loads(args.path.read_text(encoding='utf-8'))
    id_map = payload['meta']['paper_herb_id_map']
    print('[OK] entity mapping validation passed')
    print(f'  herbs={len(payload["herbs"])} adrs={len(payload["adrs"])}')
    print('  paper seeds:')
    for seed in PAPER_HERB_SEEDS:
        hid = id_map.get(seed['latin'])
        print(f'    {seed["chinese"]:6s} {seed["latin"][:40]:40s} -> herb #{hid}')


if __name__ == '__main__':
    main()
