"""GNN baselines: GCN, GAT, R-GCN, HGT, HetGNN, Simple-HGN."""

from __future__ import annotations

import copy
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch_geometric.data import HeteroData
from torch_geometric.nn import GATConv, GraphConv, HGTConv, HeteroConv, Linear, SAGEConv

from baselines.common import FoldSplit, compute_metrics

GNN_HIDDEN = 128
GNN_LAYERS = 2
GNN_DROPOUT = 0.2
GNN_LR = 1e-3
GNN_WEIGHT_DECAY = 1e-5
GNN_MAX_EPOCHS = 200
GNN_PATIENCE = 30
GNN_BATCH_SIZE = 4096


class LinkScorer(nn.Module):
    def __init__(self, hidden: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(hidden * 2, hidden),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden, 1),
        )

    def forward(self, h_emb, a_emb, h_idx, a_idx):
        pair = torch.cat([h_emb[h_idx], a_emb[a_idx]], dim=-1)
        return torch.sigmoid(self.mlp(pair).squeeze(-1))


class HeteroEncoder(nn.Module):
    """Unified heterogeneous encoder using HeteroConv."""

    def __init__(self, metadata, in_channels_dict, hidden: int, layers: int, conv_cls, conv_kwargs=None):
        super().__init__()
        conv_kwargs = conv_kwargs or {}
        self.layers = nn.ModuleList()
        ch_in = dict(in_channels_dict)
        for _ in range(layers):
            conv = HeteroConv(
                {
                    et: conv_cls(ch_in[et[0]], hidden, **conv_kwargs)
                    for et in metadata[1]
                },
                aggr='sum',
            )
            self.layers.append(conv)
            ch_in = {nt: hidden for nt in metadata[0]}
        self.dropout = GNN_DROPOUT

    def forward(self, x_dict, edge_index_dict):
        for i, conv in enumerate(self.layers):
            x_dict = conv(x_dict, edge_index_dict)
            if i < len(self.layers) - 1:
                x_dict = {k: F.relu(v) for k, v in x_dict.items()}
                x_dict = {k: F.dropout(v, p=self.dropout, training=self.training) for k, v in x_dict.items()}
        return x_dict


class HGTLinkModel(nn.Module):
    def __init__(self, metadata, in_channels_dict, hidden: int, layers: int, heads: int = 4):
        super().__init__()
        self.lin = nn.ModuleDict({nt: Linear(in_channels_dict[nt], hidden) for nt in metadata[0]})
        self.layers = nn.ModuleList([HGTConv(hidden, hidden, metadata, heads) for _ in range(layers)])
        self.scorer = LinkScorer(hidden)

    def forward(self, x_dict, edge_index_dict, h_idx, a_idx):
        x_dict = {k: self.lin[k](v).relu_() for k, v in x_dict.items()}
        for conv in self.layers:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {k: v.relu() for k, v in x_dict.items()}
        return self.scorer(x_dict['herb'], x_dict['adr'], h_idx, a_idx)


class HeteroLinkModel(nn.Module):
    def __init__(self, encoder: nn.Module):
        super().__init__()
        self.encoder = encoder
        self.scorer = LinkScorer(GNN_HIDDEN)

    def forward(self, x_dict, edge_index_dict, h_idx, a_idx):
        x_dict = self.encoder(x_dict, edge_index_dict)
        return self.scorer(x_dict['herb'], x_dict['adr'], h_idx, a_idx)


def build_model(model_name: str, data: HeteroData, device: torch.device) -> nn.Module:
    metadata = data.metadata()
    in_channels = {nt: data[nt].x.size(1) for nt in data.node_types}

    if model_name == 'gcn':
        enc = HeteroEncoder(metadata, in_channels, GNN_HIDDEN, GNN_LAYERS, GraphConv)
        return HeteroLinkModel(enc).to(device)
    if model_name == 'gat':
        enc = HeteroEncoder(
            metadata, in_channels, GNN_HIDDEN, GNN_LAYERS, GATConv,
            conv_kwargs={'heads': 4, 'concat': False, 'add_self_loops': False},
        )
        return HeteroLinkModel(enc).to(device)
    if model_name == 'rgcn':
        enc = HeteroEncoder(metadata, in_channels, GNN_HIDDEN, GNN_LAYERS, SAGEConv)
        return HeteroLinkModel(enc).to(device)
    if model_name == 'hetnn':
        enc = HeteroEncoder(metadata, in_channels, GNN_HIDDEN, GNN_LAYERS, SAGEConv)
        return HeteroLinkModel(enc).to(device)
    if model_name == 'simple_hgn':
        enc = HeteroEncoder(
            metadata, in_channels, GNN_HIDDEN, GNN_LAYERS, GATConv,
            conv_kwargs={'heads': 2, 'concat': False, 'add_self_loops': False},
        )
        return HeteroLinkModel(enc).to(device)
    if model_name == 'hgt':
        return HGTLinkModel(metadata, in_channels, GNN_HIDDEN, GNN_LAYERS).to(device)
    raise ValueError(f'Unknown GNN model: {model_name}')


def _batch_forward(model, data, h_idx, a_idx, device):
    h = torch.as_tensor(h_idx, device=device, dtype=torch.long)
    a = torch.as_tensor(a_idx, device=device, dtype=torch.long)
    x_dict = {k: data[k].x for k in data.node_types}
    edge_index_dict = {k: data[k].edge_index for k in data.edge_types}
    return model(x_dict, edge_index_dict, h, a)


def _eval_scores(model, data, h, a, y, device) -> np.ndarray:
    model.eval()
    scores = []
    n = len(y)
    with torch.no_grad():
        for start in range(0, n, GNN_BATCH_SIZE):
            end = min(start + GNN_BATCH_SIZE, n)
            out = _batch_forward(model, data, h[start:end], a[start:end], device)
            scores.append(out.cpu().numpy())
    return np.concatenate(scores)


def train_eval_gnn(model_name: str, fold: FoldSplit, device: torch.device) -> Dict[str, float]:
    data = fold.data.clone().to(device)
    model = build_model(model_name, fold.data, device)
    optimizer = AdamW(model.parameters(), lr=GNN_LR, weight_decay=GNN_WEIGHT_DECAY)

    best_auc = -1.0
    best_state = None
    patience = 0

    train_h, train_a, train_y = fold.train_h, fold.train_a, fold.train_y
    val_h, val_a, val_y = fold.val_h, fold.val_a, fold.val_y

    for epoch in range(GNN_MAX_EPOCHS):
        model.train()
        perm = np.random.permutation(len(train_y))
        for start in range(0, len(train_y), GNN_BATCH_SIZE):
            idx = perm[start:start + GNN_BATCH_SIZE]
            optimizer.zero_grad()
            out = _batch_forward(model, data, train_h[idx], train_a[idx], device)
            loss = F.binary_cross_entropy(
                out, torch.as_tensor(train_y[idx], device=device, dtype=torch.float32)
            )
            loss.backward()
            optimizer.step()

        val_scores = _eval_scores(model, data, val_h, val_a, val_y, device)
        val_auc = compute_metrics(val_y, val_scores)['auc']
        if val_auc > best_auc:
            best_auc = val_auc
            best_state = copy.deepcopy(model.state_dict())
            patience = 0
        else:
            patience += 1
            if patience >= GNN_PATIENCE:
                break

    if best_state:
        model.load_state_dict(best_state)

    test_scores = _eval_scores(model, data, fold.test_h, fold.test_a, fold.test_y, device)
    metrics = compute_metrics(fold.test_y, test_scores)
    metrics['predictions'] = {
        'y_true': fold.test_y.tolist(),
        'y_score': test_scores.tolist(),
        'herb_indices': fold.test_h.tolist(),
        'adr_indices': fold.test_a.tolist(),
    }
    return metrics


def run_gnn_cv(model_name: str, n_folds: int = 10, device=None) -> Dict:
    from baselines.common import aggregate_fold_metrics, prepare_fold
    from config import DataConfig, TrainingConfig

    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    fold_metrics: List[Dict[str, float]] = []
    for fold_idx in range(n_folds):
        print(f'  [{model_name}] fold {fold_idx + 1}/{n_folds} (device={device})')
        fold = prepare_fold(fold_idx)
        metrics = train_eval_gnn(model_name, fold, device)
        fold_metrics.append(metrics)
        print(f"    AUC={metrics['auc']:.4f} F1={metrics['f1']:.4f}")

    return {
        'model': model_name,
        'data_config': {
            'n_folds': n_folds,
            'neg_ratio': DataConfig.NEG_RATIO,
            'test_neg_ratio': getattr(DataConfig, 'TEST_NEG_RATIO', DataConfig.NEG_RATIO),
            'random_seed': DataConfig.RANDOM_SEED,
        },
        'model_config': {
            'hidden': GNN_HIDDEN,
            'layers': GNN_LAYERS,
            'dropout': GNN_DROPOUT,
        },
        'training_config': {
            'learning_rate': GNN_LR,
            'weight_decay': GNN_WEIGHT_DECAY,
            'max_epochs': GNN_MAX_EPOCHS,
            'patience': GNN_PATIENCE,
            'batch_size': GNN_BATCH_SIZE,
            'use_optimal_threshold': TrainingConfig.USE_OPTIMAL_THRESHOLD,
        },
        'fold_metrics': fold_metrics,
        'overall_metrics': aggregate_fold_metrics(fold_metrics),
    }
