"""Paper Table 5/6 reference lookups (§3.5.6, §4.4.2)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'


def _norm_pt(text: str) -> str:
    return ' '.join(text.lower().strip().split())


@lru_cache(maxsize=1)
def load_table6_adr_mapping() -> dict[str, str]:
    path = DATA_DIR / 'paper_table6_reference.json'
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding='utf-8'))
    return {_norm_pt(row['adr_pt']): row['tcm_system_mapping'] for row in payload.get('rows', [])}


def paper_table6_mapping(adr_pt: str) -> str | None:
    return load_table6_adr_mapping().get(_norm_pt(adr_pt))
