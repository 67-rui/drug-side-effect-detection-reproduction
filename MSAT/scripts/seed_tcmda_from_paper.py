#!/usr/bin/env python3
"""Seed tcmda_cache.json from paper Table 5 TCMDA verification flags (§3.5.6).

Use when live TCMDA login is unavailable; phenotypes for database_verified=true
rows come from paper-reported MedDRA PT + common Chinese synonyms.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
PAPER_REF = MSAT_ROOT / 'data' / 'paper_table5_reference.json'
DEFAULT_OUT = MSAT_ROOT / 'data' / 'tcmda_cache.json'

# MedDRA PT -> TCMDA / Chinese adverse phenotype synonyms (paper §3.5.6 near-match)
ADR_SYNONYMS: dict[str, list[str]] = {
    'Vomiting': ['Vomiting', '呕吐', '恶心', 'Nausea'],
    'Palpitations': ['Palpitations', '心悸', '心动过速'],
    'Acute pulmonary oedema': ['Acute pulmonary oedema', '急性肺水肿', '肺水肿', 'Pulmonary oedema'],
    'Drug-induced liver injury': ['Drug-induced liver injury', '药物性肝损伤', '肝损伤', 'Liver injury'],
    'Dermatitis': ['Dermatitis', '皮炎', 'Skin reaction'],
    'Gastric haemorrhage': ['Gastric haemorrhage', '胃出血', 'Gastrointestinal haemorrhage'],
    'Pulmonary embolism': ['Pulmonary embolism', '肺栓塞'],
    'Small intestinal haemorrhage': ['Small intestinal haemorrhage', '小肠出血', 'Intestinal haemorrhage'],
    'Tinnitus': ['Tinnitus', '耳鸣'],
    'Dizziness': ['Dizziness', '头晕', '眩晕', 'Vertigo'],
    'Hepatitis': ['Hepatitis', '肝炎'],
    'Tremor': ['Tremor', '震颤'],
}

PINYIN_TO_CHINESE = {
    'Huzhang': '虎杖',
    'Changshan': '常山',
    'Hongjingtian': '红景天',
    'Muzei': '木贼',
    'Luole': '罗勒',
    'Aiye': '艾叶',
    'Ezhu': '莪术',
    'Niubanggen': '牛蒡根',
    'Shanglu': '商陆',
    'Bajiao Huixiang': '八角茴香',
    'Yuanhua': '芫花',
    'Ciwujia': '刺五加',
    'Hei Shengma': '黑升麻',
    'Liangmianzhen': '两面针',
    'Xishu': '喜树',
}


def latin_short(latin: str) -> str:
    return latin.split(' Sieb.')[0].split(' L.')[0].split(' (')[0].strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--paper-ref', type=Path, default=PAPER_REF)
    args = parser.parse_args()

    payload = json.loads(args.paper_ref.read_text(encoding='utf-8'))
    entries = []
    for row in payload['rows']:
        cn = PINYIN_TO_CHINESE.get(row['pinyin'], '')
        latin = row['latin']
        adr = row['adr_pt']
        aliases = [x for x in [cn, row['pinyin'], latin_short(latin), latin] if x]
        phenotypes: list[str] = []
        if row.get('database_verified'):
            phenotypes = list(dict.fromkeys(ADR_SYNONYMS.get(adr, [adr])))
        entries.append({
            'herb_query': cn or row['pinyin'],
            'herb_aliases': aliases,
            'adverse_phenotypes': phenotypes,
            'predicted_adr_pt': adr,
            'source_url': 'https://organchem.csdb.cn/scdb/Tcm_Multi/Tox_eff_query2.asp',
            'notes': (
                'Paper Table 5 database_verified flag; '
                + ('phenotypes from paper ADR PT + CN synonyms' if phenotypes else 'paper: not TCMDA-verified')
            ),
            'paper_database_verified': row.get('database_verified'),
            'verified_at': datetime.now().strftime('%Y-%m-%d'),
            'verified_by': 'seed_tcmda_from_paper.py',
        })

    out = {
        'updated_at': datetime.now().isoformat(),
        'source': 'paper_table5_reference.json (Shi et al. 2026 Table 5 TCMDA flags)',
        'live_tcmda_login': False,
        'instructions': (
            'Replace with live TCMDA queries via: '
            'TCMDA_USER=... TCMDA_PASS=... python scripts/fetch_tcmda.py --write-cache'
        ),
        'entries': entries,
    }
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    verified = sum(1 for e in entries if e['adverse_phenotypes'])
    print(f'[SAVED] {args.out} ({len(entries)} herbs, {verified} with TCMDA phenotypes)')


if __name__ == '__main__':
    main()
