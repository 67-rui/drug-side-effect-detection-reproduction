"""MSAT CMM–ADR link prediction for deployment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import torch
from torch_geometric.data import HeteroData

from config import DataConfig, ModelConfig
from experiments.feature_extractor import FeatureExtractor
from inference.entity_mapping import EntityNames, DEFAULT_MAPPING_PATH
from inference.graph_utils import build_known_herb_adr_map, explain_herb_adr, herb_known_adr_counts
from model import MSATTCMFSFinal


@dataclass
class PairScore:
    herb_id: int
    adr_id: int
    score: float
    known_edge: bool
    rank: int | None = None


class MSATPredictor:
    """Load MSAT on the full Zenodo graph and score CMM–ADR pairs."""

    DEFAULT_CHECKPOINT = Path(__file__).resolve().parents[1] / 'saved_models' / 'best_model_for_prediction.pt'

    def __init__(
        self,
        checkpoint: str | Path | None = None,
        device: str | None = None,
        entity_names_path: str | Path | None = None,
    ):
        self.checkpoint = Path(checkpoint or self.DEFAULT_CHECKPOINT)
        if not self.checkpoint.is_file():
            raise FileNotFoundError(
                f'未找到模型权重: {self.checkpoint}\n'
                '请先完成 MSAT 训练并生成 saved_models/best_model_for_prediction.pt'
            )

        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)

        extractor = FeatureExtractor(data_dir=str(DataConfig.DATA_DIR))
        self.data: HeteroData = extractor.get_graph_data()
        self.n_herb = self.data['herb'].x.size(0)
        self.n_adr = self.data['adr'].x.size(0)

        self.node_degrees = self._compute_degrees()
        self.known_map = build_known_herb_adr_map(self.data)
        self.herb_adr_counts = herb_known_adr_counts(self.data)
        self.names = EntityNames.load(entity_names_path or DEFAULT_MAPPING_PATH)

        self.model = self._build_model()
        state = torch.load(self.checkpoint, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state)
        self.model.eval()

        self._x_dict = {k: v.to(self.device) for k, v in self.data.x_dict.items()}
        self._edge_index_dict = {k: v.to(self.device) for k, v in self.data.edge_index_dict.items()}
        self._edge_attr_dict = {
            k: (v.to(self.device) if v is not None else None)
            for k, v in self.data.edge_attr_dict.items()
        }

    def _compute_degrees(self) -> dict[str, torch.Tensor]:
        degrees: dict[str, torch.Tensor] = {}
        for ntype in self.data.node_types:
            degree = torch.zeros(self.data[ntype].x.size(0))
            for edge_type, edge_index in self.data.edge_index_dict.items():
                if edge_type[2] == ntype:
                    degree += torch.bincount(edge_index[1], minlength=self.data[ntype].x.size(0)).float()
            degrees[ntype] = degree
        return degrees

    def _build_model(self) -> MSATTCMFSFinal:
        model = MSATTCMFSFinal(
            node_types=list(self.data.node_types),
            edge_types=list(self.data.edge_types),
            in_channels_dict={nt: self.data[nt].x.size(1) for nt in self.data.node_types},
            hidden_channels=ModelConfig.HIDDEN_CHANNELS,
            out_channels=ModelConfig.OUT_CHANNELS,
            num_layers=ModelConfig.NUM_LAYERS,
            num_heads=ModelConfig.NUM_HEADS,
            dropout=ModelConfig.DROPOUT,
            edge_attr_dim=ModelConfig.EDGE_ATTR_DIM,
            node_degrees_dict=self.node_degrees,
            use_gated_edge_encoder=ModelConfig.USE_GATED_EDGE_ENCODER,
            use_bottleneck_transform=ModelConfig.USE_BOTTLENECK_TRANSFORM,
            use_late_fusion=ModelConfig.USE_LATE_FUSION,
        )
        return model.to(self.device)

    def herb_label(self, herb_id: int) -> str:
        return self.names.herb_display(herb_id)

    def adr_label(self, adr_id: int) -> str:
        return self.names.adr_display(adr_id)

    def list_herb_options(self) -> list[tuple[int, str]]:
        return [
            (i, self.names.herb_short(i, self.herb_adr_counts[i]))
            for i in range(self.n_herb)
        ]

    def list_adr_options(self) -> list[tuple[int, str]]:
        return [(i, self.adr_label(i)) for i in range(self.n_adr)]

    @torch.no_grad()
    def score_pairs(self, herb_ids: np.ndarray, adr_ids: np.ndarray) -> np.ndarray:
        h = torch.as_tensor(herb_ids, dtype=torch.long, device=self.device)
        a = torch.as_tensor(adr_ids, dtype=torch.long, device=self.device)
        out = self.model(
            self._x_dict,
            self._edge_index_dict,
            self._edge_attr_dict,
            h,
            a,
        )
        return torch.nan_to_num(out, nan=0.5).detach().cpu().numpy().reshape(-1)

    @torch.no_grad()
    def score_herb_all_adrs(self, herb_id: int, batch_size: int = 2048) -> np.ndarray:
        if not 0 <= herb_id < self.n_herb:
            raise ValueError(f'herb_id 须在 [0, {self.n_herb})，收到 {herb_id}')

        scores = np.empty(self.n_adr, dtype=np.float64)
        adr_all = np.arange(self.n_adr, dtype=np.int64)
        herb_col = np.full(self.n_adr, herb_id, dtype=np.int64)

        for start in range(0, self.n_adr, batch_size):
            end = min(start + batch_size, self.n_adr)
            scores[start:end] = self.score_pairs(herb_col[start:end], adr_all[start:end])
        return scores

    def predict_herb(self, herb_id: int, top_k: int = 15, threshold: float = 0.5) -> dict:
        scores = self.score_herb_all_adrs(herb_id)
        order = np.argsort(scores)[::-1]
        known = self.known_map.get(herb_id, set())

        top_rows: list[dict] = []
        for rank, adr_id in enumerate(order[:top_k], start=1):
            top_rows.append(
                {
                    'rank': rank,
                    'adr_id': int(adr_id),
                    'adr': self.adr_label(int(adr_id)),
                    'score': float(scores[adr_id]),
                    'known_edge': int(adr_id) in known,
                    'above_threshold': float(scores[adr_id]) >= threshold,
                }
            )

        return {
            'herb_id': herb_id,
            'herb': self.herb_label(herb_id),
            'known_adr_count': len(known),
            'herb_degree': int(self.node_degrees['herb'][herb_id].item()),
            'top_adr': top_rows,
            'all_scores': {self.adr_label(i): float(scores[i]) for i in order[:100]},
            'threshold': threshold,
        }

    def predict_pair(self, herb_id: int, adr_id: int) -> dict:
        if not 0 <= herb_id < self.n_herb:
            raise ValueError(f'无效 herb_id: {herb_id}')
        if not 0 <= adr_id < self.n_adr:
            raise ValueError(f'无效 adr_id: {adr_id}')

        score = float(self.score_pairs(np.array([herb_id]), np.array([adr_id]))[0])
        all_scores = self.score_herb_all_adrs(herb_id)
        rank = int((all_scores > score).sum()) + 1
        known = adr_id in self.known_map.get(herb_id, set())

        return {
            'herb_id': herb_id,
            'adr_id': adr_id,
            'herb': self.herb_label(herb_id),
            'adr': self.adr_label(adr_id),
            'score': score,
            'rank': rank,
            'rank_total': self.n_adr,
            'known_edge': known,
            'paths': explain_herb_adr(
                self.data,
                herb_id,
                adr_id,
                herb_label=self.herb_label(herb_id),
                adr_label=self.adr_label(adr_id),
            ),
        }

    def predict_formula(
        self,
        herb_ids: list[int],
        mode: Literal['max', 'mean'] = 'max',
        top_k: int = 15,
        threshold: float = 0.5,
    ) -> dict:
        valid = [h for h in herb_ids if 0 <= h < self.n_herb]
        missing = [h for h in herb_ids if h not in valid]
        if not valid:
            return {'found': False, 'error': '无有效 CMM 节点 ID'}

        per_herb_scores = [self.score_herb_all_adrs(h) for h in valid]
        stacked = np.stack(per_herb_scores, axis=0)
        if mode == 'max':
            agg = stacked.max(axis=0)
        else:
            agg = stacked.mean(axis=0)

        order = np.argsort(agg)[::-1]
        top_rows = []
        for rank, adr_id in enumerate(order[:top_k], start=1):
            top_rows.append(
                {
                    'rank': rank,
                    'adr_id': int(adr_id),
                    'adr': self.adr_label(int(adr_id)),
                    'score': float(agg[adr_id]),
                    'above_threshold': float(agg[adr_id]) >= threshold,
                }
            )

        return {
            'found': True,
            'herb_ids': valid,
            'herbs': [self.herb_label(h) for h in valid],
            'missing_herb_ids': missing,
            'aggregation': mode,
            'top_adr': top_rows,
            'per_herb': [
                {'herb_id': h, 'herb': self.herb_label(h), 'top_score': float(s.max())}
                for h, s in zip(valid, per_herb_scores)
            ],
            'threshold': threshold,
        }
