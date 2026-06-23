"""Load entity id -> name mapping for MSAT graph nodes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from inference.paper_herbs import PAPER_HERB_SEEDS

DEFAULT_MAPPING_PATH = Path(__file__).resolve().parents[1] / 'data' / 'entity_names.json'


@dataclass
class EntityRecord:
    id: int
    primary: str
    latin: str | None = None
    chinese: str | None = None
    pinyin: str | None = None
    meddra_pt: str | None = None
    confidence: float | None = None
    source: str | None = None

    def display(self, fallback_prefix: str) -> str:
        if self.chinese and self.latin:
            return f'{self.chinese}（{self.latin}）'
        if self.chinese:
            return self.chinese
        if self.latin:
            return self.latin
        if self.meddra_pt:
            return self.meddra_pt
        if self.primary:
            return self.primary
        return f'{fallback_prefix} #{self.id}'

    def short_label(self, fallback_prefix: str) -> str:
        name = self.chinese or self.latin or self.meddra_pt or self.primary
        if name:
            return f'{name} · {fallback_prefix} #{self.id}'
        return f'{fallback_prefix} #{self.id}'


@dataclass
class EntityNames:
    herbs: dict[int, EntityRecord]
    adrs: dict[int, EntityRecord]
    meta: dict[str, Any]

    @classmethod
    def load(cls, path: str | Path | None = None) -> EntityNames:
        mapping_path = Path(path or DEFAULT_MAPPING_PATH)
        if not mapping_path.is_file():
            return cls(herbs={}, adrs={}, meta={'loaded': False})

        payload = json.loads(mapping_path.read_text(encoding='utf-8'))
        herbs = {}
        for k, v in payload.get('herbs', {}).items():
            herbs[int(k)] = EntityRecord(
                id=int(k),
                primary=v.get('primary', ''),
                latin=v.get('latin'),
                chinese=v.get('chinese'),
                pinyin=v.get('pinyin'),
                meddra_pt=v.get('meddra_pt'),
                confidence=v.get('confidence'),
                source=v.get('source'),
            )
        adrs = {}
        for k, v in payload.get('adrs', {}).items():
            adrs[int(k)] = EntityRecord(
                id=int(k),
                primary=v.get('primary', ''),
                latin=v.get('latin'),
                chinese=v.get('chinese'),
                pinyin=v.get('pinyin'),
                meddra_pt=v.get('meddra_pt'),
                confidence=v.get('confidence'),
                source=v.get('source'),
            )
        return cls(herbs=herbs, adrs=adrs, meta=payload.get('meta', {}))

    def paper_herb_display(self, herb_id: int) -> str | None:
        id_map = self.meta.get('paper_herb_id_map') or {}
        latin_by_id = {int(v): k for k, v in id_map.items()}
        latin = latin_by_id.get(herb_id)
        if not latin:
            return None
        seed_by_latin = {s['latin']: s for s in PAPER_HERB_SEEDS}
        seed = seed_by_latin.get(latin)
        if seed and seed.get('chinese'):
            return f"{seed['chinese']}（{latin}）"
        return latin

    def herb_display(self, herb_id: int) -> str:
        paper = self.paper_herb_display(herb_id)
        if paper:
            return paper
        rec = self.herbs.get(herb_id)
        return rec.display('CMM') if rec else f'CMM #{herb_id}'

    def herb_short(self, herb_id: int, known_edges: int | None = None) -> str:
        rec = self.herbs.get(herb_id)
        base = rec.short_label('CMM') if rec else f'CMM #{herb_id}'
        if known_edges is not None:
            return f'{base}（已知 ADR 边 {known_edges}）'
        return base

    def adr_display(self, adr_id: int) -> str:
        rec = self.adrs.get(adr_id)
        return rec.display('ADR') if rec else f'ADR #{adr_id}'

    def paper_herb_id(self, latin: str) -> int | None:
        id_map = self.meta.get('paper_herb_id_map') or {}
        hid = id_map.get(latin)
        return int(hid) if hid is not None else None

    @property
    def loaded(self) -> bool:
        return bool(self.herbs or self.adrs)
