#!/usr/bin/env python3
"""Export global Top-15 predictions for Table 5 validation (paper §3.5.6)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from inference.artifact_manifest import artifact_status, file_manifest
from experiments.feature_extractor import FeatureExtractor
from inference.entity_mapping import EntityNames
from inference.graph_utils import build_known_herb_adr_map, explain_herb_adr
from inference.tcmda_validation import database_verified as tcmda_database_verified


def graph_positive_pairs() -> set[tuple[int, int]]:
    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    return {(int(h), int(a)) for h, a in zip(ei[0].tolist(), ei[1].tolist())}


def faers_positive_pairs() -> set[tuple[int, int]]:
    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    faers_mask = ea[:, 2].numpy() > 0.5
    return {
        (int(h), int(a))
        for h, a in zip(ei[0].numpy()[faers_mask], ei[1].numpy()[faers_mask])
    }


def collect_predictor_scores(checkpoint: Path | None = None) -> dict[tuple[int, int], float]:
    from inference.predictor import MSATPredictor

    predictor = MSATPredictor(checkpoint=checkpoint)
    scores: dict[tuple[int, int], float] = {}
    for h in range(predictor.n_herb):
        arr = predictor.score_herb_all_adrs(h)
        for a in range(predictor.n_adr):
            scores[(h, a)] = float(arr[a])
    return scores


def collect_oof_scores(summary_path: Path) -> dict[tuple[int, int], float]:
    summary = json.loads(summary_path.read_text())
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    best: dict[tuple[int, int], float] = {}
    for fold_idx, fold in enumerate(summary['fold_results']):
        preds = fold['predictions']
        scores = preds['y_score']
        if 'herb_indices' in preds and 'adr_indices' in preds:
            pairs = zip(preds['herb_indices'], preds['adr_indices'], scores)
        else:
            _, test_data = extractor.load_fold_data(fold_idx)
            pairs = zip(
                test_data['herb_indices'],
                test_data['adr_indices'],
                scores,
            )
        for h, a, s in pairs:
            pair = (int(h), int(a))
            score = float(s)
            if pair not in best or score > best[pair]:
                best[pair] = score
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description='Table 5 Top-15 export (paper §3.5.6)')
    parser.add_argument(
        '--summary',
        type=Path,
        default=MSAT_ROOT / 'results' / 'summary.json',
    )
    parser.add_argument('--top-k', type=int, default=15)
    parser.add_argument(
        '--out-dir',
        type=Path,
        default=MSAT_ROOT / 'results',
    )
    parser.add_argument(
        '--use-predictor',
        action='store_true',
        help='Non-paper: score all herb×adr with best_model_for_prediction.pt',
    )
    parser.add_argument(
        '--checkpoint',
        type=Path,
        default=None,
        help='Checkpoint for --use-predictor. Defaults to saved_models/best_model_for_prediction.pt',
    )
    parser.add_argument(
        '--exclude-faers-only',
        action='store_true',
        help='Non-paper legacy pool: exclude FAERS 25734 edges only',
    )
    parser.add_argument(
        '--tcmda-cache',
        type=Path,
        default=MSAT_ROOT / 'data' / 'tcmda_cache.json',
        help='TCMDA manual verification cache (paper §3.5.6 channel i)',
    )
    args = parser.parse_args()
    if args.checkpoint is not None and not args.use_predictor:
        parser.error('--checkpoint is only valid together with --use-predictor')

    names = EntityNames.load()
    if args.exclude_faers_only:
        excluded = faers_positive_pairs()
        pool_label = 'exclude_faers_only'
    else:
        excluded = graph_positive_pairs()
        pool_label = 'exclude_all_graph_positives'

    if args.use_predictor:
        scores = collect_predictor_scores(args.checkpoint)
        checkpoint = args.checkpoint or (MSAT_ROOT / 'saved_models' / 'best_model_for_prediction.pt')
        source = str(checkpoint)
        scoring_mode = 'predictor'
        checkpoint_manifest = file_manifest(checkpoint)
    else:
        scores = collect_oof_scores(args.summary)
        source = str(args.summary)
        scoring_mode = 'oof_pooled'
        checkpoint_manifest = None

    candidates = [(pair, sc) for pair, sc in scores.items() if pair not in excluded]
    candidates.sort(key=lambda x: x[1], reverse=True)
    top = candidates[: args.top_k]

    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    build_known_herb_adr_map(data)

    rows = []
    for rank, ((h, a), score) in enumerate(top, start=1):
        paths = explain_herb_adr(
            data,
            h,
            a,
            herb_label=names.herb_display(h),
            adr_label=names.adr_display(a),
        )
        rec = names.herbs.get(h)
        mechanistic = any('成分介导' in p or '共享靶点' in p for p in paths)
        herb_aliases = [x for x in [rec.chinese, rec.latin, rec.pinyin] if rec and x]
        adr_pt = names.adr_display(a)
        db_ok, tcmda_ev = tcmda_database_verified(herb_aliases, adr_pt, args.tcmda_cache)
        rows.append(
            {
                'rank': rank,
                'herb_id': h,
                'pinyin': rec.pinyin if rec else '',
                'latin': rec.latin if rec else '',
                'chinese': rec.chinese if rec else '',
                'adr_id': a,
                'adr_pt': adr_pt,
                'score_pct': round(score * 100, 3),
                'database_verified': db_ok,
                'tcmda_evidence': tcmda_ev,
                'mechanistic_support': mechanistic,
                'path_hint': paths[0] if paths else '',
            }
        )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / 'table5_top15.csv'
    json_path = out_dir / 'table5_summary.json'
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    supported = sum(1 for r in rows if r['database_verified'] or r['mechanistic_support'])
    payload = {
        'created_at': datetime.now().isoformat(),
        'protocol': 'paper_3.5.6_global_top15',
        'source_summary': source,
        'scoring_mode': scoring_mode,
        'artifact_status': artifact_status(stale=False),
        'checkpoint': checkpoint_manifest,
        'input_summary': file_manifest(args.summary) if not args.use_predictor else None,
        'candidate_pool': pool_label,
        'database_check': (
            f'TCMDA cache: {args.tcmda_cache} '
            f'({"found" if args.tcmda_cache.is_file() else "missing — register at organchem.csdb.cn"})'
        ),
        'top_k': args.top_k,
        'support_rate': supported / len(rows) if rows else 0.0,
        'supported_count': supported,
        'csv': str(csv_path),
        'rows': rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[SAVED] {csv_path}')
    print(f'[SAVED] {json_path}')
    print(f'[support] {supported}/{len(rows)} = {payload["support_rate"]:.1%} (mechanistic only; TCMDA pending)')


if __name__ == '__main__':
    main()
