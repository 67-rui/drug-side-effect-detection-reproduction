#!/usr/bin/env python3
"""Build graph node id -> human-readable names via BioBERT alignment."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from inference.biobert_encoder import encode_texts, score_nodes
from inference.paper_herbs import PAPER_HERB_SEEDS


@dataclass
class Candidate:
    text: str
    latin: str | None = None
    chinese: str | None = None
    pinyin: str | None = None
    meddra_pt: str | None = None
    source: str = 'unknown'


def _first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


def load_meddra_terms(path: Path) -> list[Candidate]:
    terms: set[str] = set()
    with path.open(encoding='utf-8', errors='ignore') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 6 and parts[3] in ('PT', 'LLT'):
                term = parts[5].strip()
                if term:
                    terms.add(term)
    return [Candidate(text=t, meddra_pt=t, source='meddra') for t in sorted(terms)]


def load_itcm_herbs(path: Path) -> list[Candidate]:
    out: list[Candidate] = []
    seen: set[str] = set()
    with path.open(encoding='utf-8', errors='ignore') as f:
        header = f.readline().strip().split('\t')
        idx = {k: i for i, k in enumerate(header)}
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < len(header):
                continue
            latin = parts[idx.get('LATIN', -1)].strip() if 'LATIN' in idx else ''
            chinese = parts[idx.get('CHN', -1)].strip() if 'CHN' in idx else ''
            pinyin = parts[idx.get('PINYIN', -1)].strip() if 'PINYIN' in idx else ''
            english = parts[idx.get('English_Name', -1)].strip() if 'English_Name' in idx else ''

            for text in (latin, english):
                if not text or text in seen:
                    continue
                seen.add(text)
                out.append(
                    Candidate(
                        text=text,
                        latin=latin or None,
                        chinese=chinese or None,
                        pinyin=pinyin or None,
                        source='itcm',
                    )
                )
    return out


def load_paper_herb_seeds() -> list[Candidate]:
    out: list[Candidate] = []
    for row in PAPER_HERB_SEEDS:
        out.append(
            Candidate(
                text=row['latin'],
                latin=row['latin'],
                chinese=row.get('chinese'),
                pinyin=row.get('pinyin'),
                source='paper_table5',
            )
        )
    return out


def assign_entities(
    node_x: np.ndarray,
    candidates: list[Candidate],
    batch_encode: int = 128,
    unique_candidates: bool = False,
) -> tuple[list[dict], dict]:
    texts = [c.text for c in candidates]
    cand_emb = encode_texts(texts, batch_size=batch_encode)
    sim = score_nodes(node_x, cand_emb)

    n_nodes, n_cands = sim.shape
    if unique_candidates and n_cands >= n_nodes:
        row_ind, col_ind = linear_sum_assignment(-sim)
        pairs = list(zip(row_ind.tolist(), col_ind.tolist()))
    else:
        pairs = [(i, int(sim[i].argmax())) for i in range(n_nodes)]

    records: list[dict] = []
    confidences: list[float] = []
    for row, col in pairs:
        cand = candidates[col]
        score = float(sim[int(row), int(col)])
        row_scores = sim[int(row)]
        order = np.argsort(row_scores)[::-1]
        margin = float(row_scores[order[0]] - row_scores[order[1]]) if len(order) > 1 else score
        confidences.append(score)
        records.append(
            {
                'id': int(row),
                'primary': cand.text,
                'latin': cand.latin,
                'chinese': cand.chinese,
                'pinyin': cand.pinyin,
                'meddra_pt': cand.meddra_pt,
                'confidence': score,
                'margin': margin,
                'source': cand.source,
            }
        )

    stats = {
        'n_nodes': n_nodes,
        'n_candidates': n_cands,
        'score_mean': float(np.mean(confidences)),
        'score_min': float(np.min(confidences)),
        'score_max': float(np.max(confidences)),
    }
    return records, stats


def assign_paper_herb_ids(node_x: np.ndarray, batch_encode: int = 128) -> dict[str, int]:
    """Map each Table 5 seed to a unique herb node via Hungarian assignment."""
    texts = [s['latin'] for s in PAPER_HERB_SEEDS]
    seed_emb = encode_texts(texts, batch_size=batch_encode)
    sim = seed_emb @ node_x.T
    row_ind, col_ind = linear_sum_assignment(-sim)
    out: dict[str, int] = {}
    for row, col in zip(row_ind.tolist(), col_ind.tolist()):
        out[PAPER_HERB_SEEDS[row]['latin']] = int(col)
    return out


def validate_paper_herbs(
    herb_records: dict[str, dict],
    node_x: np.ndarray,
    paper_id_map: dict[str, int],
) -> list[dict]:
    checks: list[dict] = []
    for seed in PAPER_HERB_SEEDS:
        latin = seed['latin']
        mapped_id = paper_id_map.get(latin)
        emb = encode_texts([latin])[0]
        sims = node_x @ emb
        top_id = int(sims.argmax())
        checks.append(
            {
                'latin': latin,
                'chinese': seed.get('chinese'),
                'mapped_id': mapped_id,
                'top_dot_id': top_id,
                'top_dot_score': float(sims[top_id]),
                'mapped_score': float(sims[mapped_id]) if mapped_id is not None else None,
            }
        )
    return checks


def write_cctcm_index(herb_records: list[dict], path: Path) -> None:
    rows = []
    for rec in sorted(herb_records, key=lambda r: r['id']):
        rows.append(
            {
                'id': rec['id'],
                'primary': rec['primary'],
                'latin': rec.get('latin'),
                'chinese': rec.get('chinese'),
                'pinyin': rec.get('pinyin'),
                'confidence': rec.get('confidence'),
                'source': rec.get('source'),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description='Build MSAT entity name mapping')
    parser.add_argument(
        '--output',
        type=Path,
        default=MSAT_ROOT / 'data' / 'entity_names.json',
    )
    parser.add_argument(
        '--index-output',
        type=Path,
        default=MSAT_ROOT / 'data' / 'cctcm_herb_index.json',
    )
    parser.add_argument('--meddra', type=Path, default=None)
    parser.add_argument('--itcm-herbs', type=Path, default=None)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument(
        '--online',
        action='store_true',
        help='Allow HuggingFace download for BioBERT (default: local cache only)',
    )
    args = parser.parse_args()

    if args.online:
        os.environ['MSAT_BIOBERT_LOCAL_ONLY'] = '0'
    else:
        os.environ.setdefault('MSAT_BIOBERT_LOCAL_ONLY', '1')
        print('[biobert] offline mode: local HuggingFace cache only')

    meddra_path = args.meddra or _first_existing(
        [MSAT_ROOT / 'data' / 'raw' / 'meddra_all_se.tsv']
    )
    itcm_path = args.itcm_herbs or _first_existing(
        [
            MSAT_ROOT / 'data' / 'raw' / 'itcm' / 'herb_detail.txt',
            MSAT_ROOT / 'data' / 'raw' / 'itcm_herb_detail.txt',
        ]
    )

    if meddra_path is None:
        raise FileNotFoundError('MedDRA TSV not found; use --meddra')
    if itcm_path is None:
        raise FileNotFoundError('ITCM herb_detail.txt not found; use --itcm-herbs')

    print(f'[load] graph: {DataConfig.GRAPH_PATH}')
    print(f'[load] meddra: {meddra_path}')
    print(f'[load] itcm: {itcm_path}')

    graph = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    herb_x = graph['herb'].x.numpy()
    adr_x = graph['adr'].x.numpy()

    herb_candidates = load_paper_herb_seeds() + load_itcm_herbs(itcm_path)
    adr_candidates = load_meddra_terms(meddra_path)
    print(f'[candidates] herb={len(herb_candidates)} adr={len(adr_candidates)}')

    paper_id_map = assign_paper_herb_ids(herb_x, args.batch_size)
    print('[paper] Hungarian seed -> node ids:')
    for seed in PAPER_HERB_SEEDS:
        print(f'  {seed["chinese"]} -> #{paper_id_map[seed["latin"]]}')

    herb_records, herb_stats = assign_entities(
        herb_x, herb_candidates, args.batch_size, unique_candidates=True
    )
    adr_records, adr_stats = assign_entities(
        adr_x, adr_candidates, args.batch_size, unique_candidates=True
    )

    herbs = {str(r['id']): {k: v for k, v in r.items() if k != 'id'} for r in herb_records}
    adrs = {str(r['id']): {k: v for k, v in r.items() if k != 'id'} for r in adr_records}

    payload = {
        'meta': {
            'created_at': datetime.now().isoformat(),
            'method': 'BioBERT CLS dot-product + Hungarian linear assignment (651 herbs, 5974 ADRs)',
            'biobert_model': 'dmis-lab/biobert-base-cased-v1.2',
            'sources': {
                'meddra': str(meddra_path),
                'itcm_herbs': str(itcm_path),
                'paper_table5': len(PAPER_HERB_SEEDS),
            },
            'herb_stats': herb_stats,
            'adr_stats': adr_stats,
            'paper_herb_id_map': paper_id_map,
            'paper_herb_checks': validate_paper_herbs(herbs, herb_x, paper_id_map),
        },
        'herbs': herbs,
        'adrs': adrs,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    write_cctcm_index(herb_records, args.index_output)
    print(f'[saved] {args.output}')
    print(f'[saved] {args.index_output}')
    print(f'[herb] score mean={herb_stats["score_mean"]:.2f}')
    print(f'[adr] score mean={adr_stats["score_mean"]:.2f}')


if __name__ == '__main__':
    main()
