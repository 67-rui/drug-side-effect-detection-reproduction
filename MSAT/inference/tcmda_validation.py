"""TCMDA (organchem.csdb.cn) validation — paper §3.5.6 database verification channel.

TCMDA has no public API; this module reads a human-verified cache populated by
manual queries at https://organchem.csdb.cn/ (login required).

Populate cache: scripts/import_tcmda_cache.py or edit data/tcmda_cache.json directly.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_CACHE_PATH = Path(__file__).resolve().parents[1] / 'data' / 'tcmda_cache.json'


def _norm(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', ' ', t)
    return ' '.join(t.split())


def adr_match(predicted_pt: str, db_phenotype: str) -> bool:
    a, b = _norm(predicted_pt), _norm(db_phenotype)
    if not a or not b:
        return False
    return a == b or a in b or b in a


@dataclass
class TcmdaHit:
    herb_query: str
    adr_pt: str
    matched_phenotype: str
    source_url: str | None = None
    notes: str | None = None
    verified_at: str | None = None
    verified_by: str | None = None


@lru_cache(maxsize=1)
def load_cache(path: str | None = None) -> list[dict]:
    p = Path(path or DEFAULT_CACHE_PATH)
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding='utf-8')).get('entries', [])


def lookup_tcmda(
    herb_names: list[str],
    adr_pt: str,
    cache_path: str | Path | None = None,
) -> TcmdaHit | None:
    """Return hit if cache lists a TCMDA adverse phenotype matching adr_pt for any herb alias."""
    entries = load_cache(str(cache_path) if cache_path else None)
    name_set = {_norm(n) for n in herb_names if n}
    for row in entries:
        row_names = {_norm(x) for x in row.get('herb_aliases', []) if x}
        if not name_set & row_names:
            continue
        phenotypes = row.get('adverse_phenotypes') or []
        for phen in phenotypes:
            if adr_match(adr_pt, phen):
                return TcmdaHit(
                    herb_query=row.get('herb_query', ''),
                    adr_pt=adr_pt,
                    matched_phenotype=phen,
                    source_url=row.get('source_url'),
                    notes=row.get('notes'),
                    verified_at=row.get('verified_at'),
                    verified_by=row.get('verified_by'),
                )
    return None


def database_verified(
    herb_names: list[str],
    adr_pt: str,
    cache_path: str | Path | None = None,
) -> tuple[bool, dict | None]:
    hit = lookup_tcmda(herb_names, adr_pt, cache_path)
    if not hit:
        return False, None
    return True, {
        'matched_phenotype': hit.matched_phenotype,
        'source_url': hit.source_url,
        'verified_at': hit.verified_at,
    }
