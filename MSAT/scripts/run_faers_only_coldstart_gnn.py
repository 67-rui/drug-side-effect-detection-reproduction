#!/usr/bin/env python3
"""Paper §3.5.4: GNN baselines trained FAERS-only, evaluated on literature hold-out."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.common import FoldSplit
from baselines.gnn_models import train_eval_gnn
from inference.coldstart import literature_pairs
from scripts.run_faers_only_coldstart_train import (
    eval_literature_coldstart,
    faers_only_graph,
    faers_positive_array,
    sample_pairs,
)
from config import DataConfig, TrainingConfig
from experiments.feature_extractor import FeatureExtractor


GNN_MODELS = ['gat', 'hgt', 'simple_hgn']
DISPLAY = {'gat': 'GAT', 'hgt': 'HGT', 'simple_hgn': 'Simple-HGN'}


def prepare_faers_only_fold() -> tuple[FoldSplit, set[tuple[int, int]], set[int]]:
    lit_pairs = literature_pairs()
    faers_pos = faers_positive_array()
    extractor = FeatureExtractor(data_dir=DataConfig.DATA_DIR)
    graph = extractor.get_graph_data()
    num_adr = graph['adr'].x.size(0)
    all_pos_set = set(map(tuple, graph['herb', 'causes', 'adr'].edge_index.t().tolist()))

    rng = np.random.RandomState(TrainingConfig.RANDOM_STATE)
    perm = rng.permutation(len(faers_pos))
    n_val = max(1, int(len(faers_pos) * (1 - TrainingConfig.TRAIN_VAL_SPLIT)))
    val_pos = faers_pos[perm[:n_val]]
    train_pos = faers_pos[perm[n_val:]]

    train_data = sample_pairs(train_pos, num_adr, all_pos_set, seed=42, neg_ratio=1)
    val_data = sample_pairs(val_pos, num_adr, all_pos_set, seed=43, neg_ratio=1)
    lit_pos = np.array(sorted(lit_pairs), dtype=np.int64)
    test_data = sample_pairs(lit_pos, num_adr, all_pos_set, seed=44, neg_ratio=1)

    data = faers_only_graph(lit_pairs)
    pos_ei = data['herb', 'causes', 'adr'].edge_index
    herb_train_degree = np.bincount(
        pos_ei[0].numpy(), minlength=data['herb'].x.size(0)
    ).astype(np.float32)

    fold = FoldSplit(
        fold_idx=0,
        data=data,
        train_h=train_data['herb_indices'],
        train_a=train_data['adr_indices'],
        train_y=train_data['labels'],
        val_h=val_data['herb_indices'],
        val_a=val_data['adr_indices'],
        val_y=val_data['labels'],
        test_h=test_data['herb_indices'],
        test_a=test_data['adr_indices'],
        test_y=test_data['labels'],
        herb_x=data['herb'].x.numpy(),
        adr_x=data['adr'].x.numpy(),
        herb_train_degree=herb_train_degree,
    )
    faers_herbs = set(faers_pos[:, 0].tolist())
    return fold, lit_pairs, faers_herbs


def run_model(model_name: str, fold: FoldSplit, lit_pairs: set, faers_herbs: set, device) -> dict:
    print(f'=== {DISPLAY[model_name]} (FAERS-only) ===')
    metrics = train_eval_gnn(model_name, fold, device)
    preds = metrics.pop('predictions')
    y_true = np.asarray(preds['y_true'])
    y_score = np.asarray(preds['y_score'])
    coldstart = eval_literature_coldstart(
        y_true,
        y_score,
        np.asarray(preds['herb_indices']),
        np.asarray(preds['adr_indices']),
        lit_pairs,
        faers_herbs,
    )
    row = {
        'model': DISPLAY[model_name],
        'model_key': model_name,
        'protocol': 'paper_3.5.4_faers_train_literature_eval',
        'test_metrics_full': {k: metrics[k] for k in ('precision', 'recall', 'f1', 'auc', 'mcc')},
        'fig5a_literature_holdout': coldstart,
    }
    cs = coldstart
    if cs.get('status') == 'ok':
        print(
            f"  Fig.5a: P={cs['precision']:.4f} MCC={cs['mcc']:.4f} "
            f"AUC={cs['auc']:.4f} unseen={cs['unseen_herb_rate']:.1%}"
        )
    return row


def merge_summary(out_path: Path, msat_path: Path, gnn_rows: list[dict]) -> dict:
    msat = json.loads(msat_path.read_text()) if msat_path.is_file() else {}
    msat_row = {
        'model': 'MSAT',
        'model_key': 'msat',
        'protocol': msat.get('protocol', 'paper_3.5.4_faers_train_literature_eval'),
        'test_metrics_full': msat.get('test_metrics_full', {}),
        'fig5a_literature_holdout': msat.get('fig5a_literature_holdout', {}),
        'train_seconds': msat.get('train_seconds'),
    }
    models = [msat_row] + gnn_rows

    def metric(model_row: dict, key: str) -> float:
        cs = model_row.get('fig5a_literature_holdout', {})
        return float(cs.get(key, float('nan')))

    ranking = {}
    for key in ('precision', 'mcc', 'auc'):
        ranked = sorted(models, key=lambda r: metric(r, key), reverse=True)
        ranking[key] = [r['model'] for r in ranked]
        ranking[f'{key}_winner'] = ranked[0]['model']

    msat_wins = sum(
        1 for key in ('precision', 'mcc', 'auc')
        if ranking[f'{key}_winner'] == 'MSAT'
    )

    payload = {
        'created_at': datetime.now().isoformat(),
        'protocol': 'paper_3.5.4_faers_train_literature_eval',
        'unseen_cmm_target': 0.965,
        'models': models,
        'ranking': ranking,
        'msat_beats_all_gnn': msat_wins == 3 and len(gnn_rows) >= 3,
        'paper_claim_msat_best': msat_wins == 3,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='FAERS-only GNN cold-start (Fig.5a)')
    parser.add_argument('--models', nargs='+', default=GNN_MODELS)
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'faers_only_coldstart_gnn.json',
    )
    parser.add_argument(
        '--summary',
        type=Path,
        default=MSAT_ROOT / 'results' / 'faers_only_coldstart_summary.json',
    )
    parser.add_argument(
        '--msat',
        type=Path,
        default=MSAT_ROOT / 'results' / 'faers_only_coldstart_train.json',
    )
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')
    fold, lit_pairs, faers_herbs = prepare_faers_only_fold()

    rows = []
    for name in args.models:
        rows.append(run_model(name, fold, lit_pairs, faers_herbs, device))

    args.out.write_text(json.dumps({'models': rows}, indent=2), encoding='utf-8')
    print(f'[SAVED] {args.out}')

    payload = merge_summary(args.summary, args.msat, rows)
    print(f'[SAVED] {args.summary}')
    print(f"Ranking P/MCC/AUC: {payload['ranking']['precision_winner']} / "
          f"{payload['ranking']['mcc_winner']} / {payload['ranking']['auc_winner']}")
    print(f"MSAT beats all GNN (3/3): {payload['msat_beats_all_gnn']}")


if __name__ == '__main__':
    main()
