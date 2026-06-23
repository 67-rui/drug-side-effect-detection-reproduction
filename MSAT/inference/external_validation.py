"""External validation helpers (paper Table 5 / TCMDA evidence)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DEFAULT_EVIDENCE_PATH = (
    Path(__file__).resolve().parents[1] / 'data' / 'paper_table5_reference.json'
)


def _norm_pt(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return ' '.join(t.split())


@lru_cache(maxsize=1)
def load_paper_table5_evidence(path: str | None = None) -> dict[tuple[str, str], dict]:
    p = Path(path or DEFAULT_EVIDENCE_PATH)
    if not p.is_file():
        return {}
    payload = json.loads(p.read_text(encoding='utf-8'))
    out: dict[tuple[str, str], dict] = {}
    for row in payload.get('rows', []):
        key = (_norm_pt(row['latin']), _norm_pt(row['adr_pt']))
        out[key] = row
    return out


def lookup_paper_evidence(latin: str, adr_pt: str, path: str | None = None) -> dict | None:
    return load_paper_table5_evidence(path).get((_norm_pt(latin), _norm_pt(adr_pt)))


def adr_match(a: str, b: str) -> bool:
    na, nb = _norm_pt(a), _norm_pt(b)
    return na == nb or na in nb or nb in na


def paper_herb_evidence_for_prediction(
    latin: str,
    adr_pt: str,
    path: str | None = None,
) -> dict | None:
    """Match prediction to paper Table 5 row by latin + fuzzy ADR."""
    evidence = load_paper_table5_evidence(path)
    latin_n = _norm_pt(latin)
    for (ref_latin, ref_adr), row in evidence.items():
        if ref_latin != latin_n:
            continue
        if adr_match(adr_pt, row['adr_pt']):
            return row
    return None
