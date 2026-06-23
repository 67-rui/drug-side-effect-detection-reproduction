#!/usr/bin/env python3
"""Case study: 枳实 (Citrus aurantium) -> diarrhoea path (Section 4.5.1)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from inference.artifact_manifest import artifact_status, file_manifest
from inference.entity_mapping import EntityNames
from inference.paper_herbs import ZHISHI_LATIN
from inference.graph_utils import explain_herb_adr
from inference.predictor import MSATPredictor

DIARRHEA_RE = re.compile(r'diarrh(o)?ea', flags=re.IGNORECASE)
NOBILETIN_CID = 72344


def find_mechanistic_paths(
    data, herb_id: int, adr_id: int, herb_label: str, adr_label: str
) -> list[str]:
    """Prefer CMM -> compound -> target -> ADR chains (paper Supplementary Fig S5 style)."""
    hc = data['herb', 'contains', 'compound'].edge_index
    tb = data['target', 'binds', 'compound'].edge_index
    at = data['adr', 'causes', 'target'].edge_index

    herb_compounds = hc[1][hc[0] == herb_id].tolist()
    adr_targets = set(at[1][at[0] == adr_id].tolist())

    paths: list[str] = []
    for c in herb_compounds:
        bound_targets = tb[0][tb[1] == int(c)].tolist()
        for t in bound_targets:
            if int(t) not in adr_targets:
                continue
            label = (
                f'{herb_label} → nobiletin (CID {NOBILETIN_CID}) → Target #{int(t)} → {adr_label}'
                if int(c) == 435
                else f'{herb_label} → Compound #{int(c)} → Target #{int(t)} → {adr_label}'
            )
            paths.append(label)
    return paths[:8]


def main() -> None:
    parser = argparse.ArgumentParser(description='Zhishi -> diarrhoea case study')
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'case_zhishi_diarrhoea.json',
    )
    parser.add_argument(
        '--checkpoint',
        type=Path,
        default=None,
        help='Prediction checkpoint. Defaults to saved_models/best_model_for_prediction.pt',
    )
    args = parser.parse_args()

    names = EntityNames.load()
    herb_id = names.paper_herb_id(ZHISHI_LATIN)
    if herb_id is None:
        raise SystemExit(
            '枳实 herb_id not found in paper_herb_id_map; run build_entity_mapping.py first'
        )

    predictor = MSATPredictor(checkpoint=args.checkpoint)
    checkpoint = args.checkpoint or MSATPredictor.DEFAULT_CHECKPOINT
    scores = predictor.score_herb_all_adrs(herb_id)
    adr_id, score = max(
        ((a, float(scores[a])) for a in range(predictor.n_adr) if DIARRHEA_RE.search(predictor.adr_label(a))),
        key=lambda x: x[1],
    )

    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    paths = explain_herb_adr(
        data,
        herb_id,
        adr_id,
        herb_label=names.herb_display(herb_id),
        adr_label=names.adr_display(adr_id),
    )
    mech = find_mechanistic_paths(data, herb_id, adr_id, names.herb_display(herb_id), names.adr_display(adr_id))
    if mech:
        paths = mech + paths

    rank = int((scores >= score).sum())
    payload = {
        'created_at': datetime.now().isoformat(),
        'artifact_status': artifact_status(stale=False),
        'checkpoint': file_manifest(checkpoint),
        'herb_id': herb_id,
        'herb_latin': ZHISHI_LATIN,
        'herb_label': names.herb_display(herb_id),
        'adr_id': adr_id,
        'adr_label': names.adr_display(adr_id),
        'score': score,
        'rank': rank,
        'rank_total': predictor.n_adr,
        'paths': paths,
        'paper_targets': {'nobiletin_cid': NOBILETIN_CID, 'transporter': 'ABCG2 (BCRP)'},
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[SAVED] {args.out}')
    print(json.dumps({k: payload[k] for k in ('herb_label', 'adr_label', 'score', 'rank')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
