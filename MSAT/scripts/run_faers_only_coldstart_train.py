#!/usr/bin/env python3
"""Paper §3.5.4: train MSAT on FAERS-only edges, evaluate on literature hold-out (Fig.5a)."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import matthews_corrcoef, precision_score, roc_auc_score
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.common import remove_cmm_adr_pairs
from config import DataConfig, ModelConfig, TrainingConfig
from experiments.feature_extractor import FeatureExtractor
from inference.coldstart import literature_holdout_mask, literature_pairs
from model import MSATTCMFSFinal
from scripts.run_faers_literature_coldstart import literature_unseen_stats
from train import evaluate, find_optimal_threshold, train_one_epoch


def faers_positive_array() -> np.ndarray:
    data = torch.load(DataConfig.GRAPH_PATH, map_location='cpu', weights_only=False)
    ei = data['herb', 'causes', 'adr'].edge_index
    ea = data['herb', 'causes', 'adr'].edge_attr
    faers_mask = ea[:, 2].numpy() > 0.5
    return np.stack([ei[0].numpy()[faers_mask], ei[1].numpy()[faers_mask]], axis=1)


def sample_pairs(
    pos_pairs: np.ndarray,
    num_adr: int,
    positive_set: set[tuple[int, int]],
    seed: int,
    neg_ratio: int = 1,
) -> dict[str, np.ndarray]:
    rng = np.random.RandomState(seed)
    herb_indices, adr_indices, labels = [], [], []
    for h, a in pos_pairs:
        h, a = int(h), int(a)
        herb_indices.append(h)
        adr_indices.append(a)
        labels.append(1)
        neg_count, attempts = 0, 0
        while neg_count < neg_ratio and attempts < num_adr * 20:
            attempts += 1
            a_neg = int(rng.randint(0, num_adr))
            if (h, a_neg) in positive_set:
                continue
            herb_indices.append(h)
            adr_indices.append(a_neg)
            labels.append(0)
            neg_count += 1
    return {
        'herb_indices': np.asarray(herb_indices, dtype=np.int64),
        'adr_indices': np.asarray(adr_indices, dtype=np.int64),
        'labels': np.asarray(labels, dtype=np.float32),
    }


def faers_only_graph(lit_pairs: set[tuple[int, int]]):
    extractor = FeatureExtractor(data_dir=DataConfig.DATA_DIR)
    data = extractor.get_graph_data().clone()
    return remove_cmm_adr_pairs(data, lit_pairs)


def build_node_degrees(data) -> dict:
    node_degrees_dict = {}
    for ntype in data.node_types:
        degree = torch.zeros(data[ntype].x.size(0))
        for edge_type, edge_index in data.edge_index_dict.items():
            if edge_type[2] == ntype:
                degree += torch.bincount(edge_index[1], minlength=data[ntype].x.size(0)).float()
        node_degrees_dict[ntype] = degree
    return node_degrees_dict


def build_model(data, node_degrees_dict, device):
    return MSATTCMFSFinal(
        node_types=list(data.node_types),
        edge_types=list(data.edge_types),
        in_channels_dict={ntype: data[ntype].x.size(1) for ntype in data.node_types},
        hidden_channels=ModelConfig.HIDDEN_CHANNELS,
        out_channels=ModelConfig.OUT_CHANNELS,
        num_layers=ModelConfig.NUM_LAYERS,
        num_heads=ModelConfig.NUM_HEADS,
        dropout=ModelConfig.DROPOUT,
        edge_attr_dim=ModelConfig.EDGE_ATTR_DIM,
        node_degrees_dict=node_degrees_dict,
        use_gated_edge_encoder=ModelConfig.USE_GATED_EDGE_ENCODER,
        use_bottleneck_transform=ModelConfig.USE_BOTTLENECK_TRANSFORM,
        use_late_fusion=ModelConfig.USE_LATE_FUSION,
    ).to(device)


def eval_literature_coldstart(
    y_true: np.ndarray,
    y_score: np.ndarray,
    test_h: np.ndarray,
    test_a: np.ndarray,
    lit_pairs: set[tuple[int, int]],
    faers_herbs: set[int],
) -> dict:
    mask = literature_holdout_mask(y_true, test_h, test_a, lit_pairs)
    y_t, y_s = y_true[mask], y_score[mask]
    if len(y_t) < 10 or len(np.unique(y_t)) < 2:
        return {'status': 'insufficient_samples', 'n': int(len(y_t))}

    y_pred = (y_s >= 0.5).astype(int)
    lit_pos_idx = np.where((y_t == 1))[0]
    unseen_herbs = {
        int(test_h[mask][i])
        for i in lit_pos_idx
        if int(test_h[mask][i]) not in faers_herbs
    }
    lit_herbs = {int(test_h[mask][i]) for i in lit_pos_idx}
    return {
        'status': 'ok',
        'n': int(len(y_t)),
        'n_pos': int((y_t == 1).sum()),
        'n_neg': int((y_t == 0).sum()),
        'precision': float(precision_score(y_t, y_pred, zero_division=0)),
        'mcc': float(matthews_corrcoef(y_t, y_pred)),
        'auc': float(roc_auc_score(y_t, y_s)),
        'unseen_herb_rate': float(len(unseen_herbs) / len(lit_herbs)) if lit_herbs else 0.0,
        'unique_lit_herbs': len(lit_herbs),
        'unique_unseen_herbs': len(unseen_herbs),
    }


def train_faers_only(device: torch.device, max_epochs: int | None = None) -> dict:
    lit_pairs = literature_pairs()
    faers_pos = faers_positive_array()
    extractor = FeatureExtractor(data_dir=DataConfig.DATA_DIR)
    num_adr = extractor.get_graph_data()['adr'].x.size(0)
    all_pos_set = set(map(tuple, extractor.get_graph_data()['herb', 'causes', 'adr'].edge_index.t().tolist()))

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
    node_degrees_dict = build_node_degrees(data)
    data = data.to(device)

    train_edges = torch.from_numpy(
        np.stack([train_data['herb_indices'], train_data['adr_indices']])
    ).long()
    train_labels = torch.from_numpy(train_data['labels'])
    val_h, val_a, val_y = val_data['herb_indices'], val_data['adr_indices'], val_data['labels']

    model = build_model(data, node_degrees_dict, device)
    optimizer = AdamW(
        model.parameters(),
        lr=TrainingConfig.LEARNING_RATE,
        weight_decay=TrainingConfig.WEIGHT_DECAY,
    )
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode=TrainingConfig.SCHEDULER_MODE,
        factor=TrainingConfig.SCHEDULER_FACTOR,
        patience=TrainingConfig.SCHEDULER_PATIENCE,
    )

    epochs = max_epochs or TrainingConfig.NUM_EPOCHS
    best_val_auc, best_state, patience = 0.0, None, 0
    t0 = time.time()
    for epoch in range(epochs):
        loss = train_one_epoch(model, data, optimizer, train_edges, train_labels, device)
        if np.isnan(loss):
            break
        val_metrics, _ = evaluate(model, data, val_h, val_a, val_y, device)
        scheduler.step(val_metrics['auc'])
        if val_metrics['auc'] > best_val_auc:
            best_val_auc = val_metrics['auc']
            best_state = copy.deepcopy(model.state_dict())
            patience = 0
        else:
            patience += 1
            if patience >= TrainingConfig.PATIENCE:
                break
        if (epoch + 1) % 100 == 0:
            print(f'  epoch {epoch + 1}: loss={loss:.4f} val_auc={val_metrics["auc"]:.4f}')

    if best_state:
        model.load_state_dict(best_state)

    _, val_probs = evaluate(model, data, val_h, val_a, val_y, device)
    threshold, _ = find_optimal_threshold(val_probs, val_y)
    test_metrics, test_probs = evaluate(
        model,
        data,
        test_data['herb_indices'],
        test_data['adr_indices'],
        test_data['labels'],
        device,
        threshold=threshold,
    )

    faers_herbs = set(faers_pos[:, 0].tolist())
    coldstart = eval_literature_coldstart(
        test_data['labels'],
        test_probs,
        test_data['herb_indices'],
        test_data['adr_indices'],
        lit_pairs,
        faers_herbs,
    )

    out_dir = MSAT_ROOT / 'saved_models'
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt = out_dir / 'faers_only_coldstart.pt'
    torch.save(best_state or model.state_dict(), ckpt)

    return {
        'created_at': datetime.now().isoformat(),
        'protocol': 'paper_3.5.4_faers_train_literature_eval',
        'train_faers_pos': int(len(faers_pos)),
        'train_samples': int(len(train_data['labels'])),
        'val_samples': int(len(val_data['labels'])),
        'test_literature_pos': int(len(lit_pos)),
        'test_samples': int(len(test_data['labels'])),
        'best_val_auc': float(best_val_auc),
        'optimal_threshold': float(threshold),
        'test_metrics_full': test_metrics,
        'fig5a_literature_holdout': coldstart,
        'unseen_cmm_stats': literature_unseen_stats(),
        'train_seconds': time.time() - t0,
        'checkpoint': str(ckpt),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='FAERS-only MSAT training for Fig.5a')
    parser.add_argument('--max-epochs', type=int, default=None)
    parser.add_argument(
        '--out',
        type=Path,
        default=MSAT_ROOT / 'results' / 'faers_only_coldstart_train.json',
    )
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')
    payload = train_faers_only(device, max_epochs=args.max_epochs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f'[SAVED] {args.out}')
    cs = payload['fig5a_literature_holdout']
    if cs.get('status') == 'ok':
        print(
            f"Fig.5a: P={cs['precision']:.4f} MCC={cs['mcc']:.4f} "
            f"AUC={cs['auc']:.4f} unseen={cs['unseen_herb_rate']:.1%}"
        )


if __name__ == '__main__':
    main()
