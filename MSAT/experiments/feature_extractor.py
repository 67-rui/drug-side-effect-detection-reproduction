"""Load MSAT heterogeneous graph and official 10-fold CV splits."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
from torch_geometric.data import HeteroData


class FeatureExtractor:
    """Load Zenodo graph and official fold splits from 10fold_cv_split.pkl."""

    POS_EDGE_TYPE = ('herb', 'causes', 'adr')
    REV_EDGE_TYPE = ('adr', 'rev_causes', 'herb')

    def __init__(
        self,
        data_dir: str | Path,
        fold_split_path: str | Path | None = None,
        n_folds: int = 10,
        neg_ratio: int = 1,
        test_neg_ratio: int | None = None,
        random_seed: int = 42,
    ):
        self.data_dir = Path(data_dir)
        self.n_folds = n_folds
        self.neg_ratio = neg_ratio
        self.test_neg_ratio = test_neg_ratio if test_neg_ratio is not None else neg_ratio
        self.random_seed = random_seed
        self.fold_split_path = (
            Path(fold_split_path)
            if fold_split_path is not None
            else Path(__file__).resolve().parents[1] / 'data' / '10fold_cv_split.pkl'
        )

        self.graph_path = self.data_dir / 'complete_hetero_graph.pt'
        self.folds_dir = self.data_dir / 'folds'
        self.folds_dir.mkdir(parents=True, exist_ok=True)

        self._graph: HeteroData | None = None
        self._positive_pairs: np.ndarray | None = None
        self._positive_set: set[tuple[int, int]] | None = None
        self._fold_splits: list[dict] | None = None

    def get_graph_data(self) -> HeteroData:
        if self._graph is None:
            if not self.graph_path.exists():
                raise FileNotFoundError(
                    f"Graph not found: {self.graph_path}\n"
                    f"Run: python3 MSAT/scripts/download_data.py"
                )
            self._graph = torch.load(self.graph_path, map_location='cpu', weights_only=False)
            self._validate_graph(self._graph)
        return self._graph

    def _validate_graph(self, data: HeteroData) -> None:
        required_nodes = {'herb', 'compound', 'target', 'adr'}
        missing = required_nodes - set(data.node_types)
        if missing:
            raise ValueError(f"Graph missing node types: {missing}")

        pos_ei = data[self.POS_EDGE_TYPE].edge_index
        pos_attr = data[self.POS_EDGE_TYPE].edge_attr
        if pos_attr is None or pos_attr.shape[1] != 6:
            raise ValueError(
                f"Expected 6-dim edge_attr on {self.POS_EDGE_TYPE}, "
                f"got {None if pos_attr is None else pos_attr.shape}"
            )

        self._positive_pairs = np.stack(
            [pos_ei[0].numpy(), pos_ei[1].numpy()], axis=1
        ).astype(np.int64)
        self._positive_set = {
            (int(h), int(a)) for h, a in self._positive_pairs
        }

    def _load_fold_splits(self) -> list[dict]:
        if self._fold_splits is None:
            if not self.fold_split_path.exists():
                raise FileNotFoundError(
                    f"Fold split file not found: {self.fold_split_path}\n"
                    f"Download from: https://github.com/BowenShiGDPU/MSAT/raw/main/data/10fold_cv_split.pkl"
                )
            with open(self.fold_split_path, 'rb') as f:
                self._fold_splits = pickle.load(f)
            if len(self._fold_splits) != self.n_folds:
                raise ValueError(
                    f"Expected {self.n_folds} folds in {self.fold_split_path}, "
                    f"got {len(self._fold_splits)}"
                )
        return self._fold_splits

    def _fold_cache_path(self, fold_idx: int, split: str, neg_ratio: int | None = None) -> Path:
        ratio = self.neg_ratio if neg_ratio is None else neg_ratio
        return self.folds_dir / f'fold{fold_idx}_{split}_neg{ratio}.npz'

    def _sample_from_pos_pairs(
        self,
        pos_pairs: np.ndarray,
        num_adr: int,
        fold_idx: int,
        split_name: str,
        neg_ratio: int | None = None,
    ) -> Dict[str, np.ndarray]:
        ratio = self.neg_ratio if neg_ratio is None else neg_ratio
        split_code = 0 if split_name == 'dev' else 1
        rng = np.random.RandomState(self.random_seed + fold_idx * 1000 + split_code)

        herb_indices = []
        adr_indices = []
        labels = []

        for h, a in pos_pairs:
            h, a = int(h), int(a)
            herb_indices.append(h)
            adr_indices.append(a)
            labels.append(1)

            neg_count = 0
            attempts = 0
            max_attempts = num_adr * 20
            while neg_count < ratio and attempts < max_attempts:
                attempts += 1
                a_neg = int(rng.randint(0, num_adr))
                if (h, a_neg) in self._positive_set:
                    continue
                herb_indices.append(h)
                adr_indices.append(a_neg)
                labels.append(0)
                neg_count += 1

        return {
            'herb_indices': np.array(herb_indices, dtype=np.int64),
            'adr_indices': np.array(adr_indices, dtype=np.int64),
            'labels': np.array(labels, dtype=np.float32),
        }

    def _resample_fold_split(self, fold_idx: int) -> Tuple[dict, dict]:
        dev_cache = self._fold_cache_path(fold_idx, 'dev')
        test_cache = self._fold_cache_path(fold_idx, 'test')

        if dev_cache.exists() and test_cache.exists():
            return dict(np.load(dev_cache)), dict(np.load(test_cache))

        fold = self._load_fold_splits()[fold_idx]
        train_idx = fold['train_idx']
        test_idx = fold['test_idx']
        herb = fold['herb_indices']
        adr = fold['adr_indices']
        labels = fold['labels']

        train_pos_mask = labels[train_idx] == 1
        test_pos_mask = labels[test_idx] == 1
        dev_pos = np.stack(
            [herb[train_idx][train_pos_mask], adr[train_idx][train_pos_mask]], axis=1
        )
        test_pos = np.stack(
            [herb[test_idx][test_pos_mask], adr[test_idx][test_pos_mask]], axis=1
        )

        num_adr = self.get_graph_data()['adr'].x.size(0)
        dev_data = self._sample_from_pos_pairs(
            dev_pos, num_adr, fold_idx, 'dev', neg_ratio=self.neg_ratio
        )
        test_data = self._sample_from_pos_pairs(
            test_pos, num_adr, fold_idx, 'test', neg_ratio=self.test_neg_ratio
        )

        np.savez(dev_cache, **dev_data)
        np.savez(test_cache, **test_data)
        return dev_data, test_data

    def _resample_test_only(self, fold_idx: int) -> dict:
        test_cache = self._fold_cache_path(fold_idx, 'test', neg_ratio=self.test_neg_ratio)
        if test_cache.exists():
            return dict(np.load(test_cache))

        fold = self._load_fold_splits()[fold_idx]
        test_idx = fold['test_idx']
        herb = fold['herb_indices']
        adr = fold['adr_indices']
        labels = fold['labels']
        test_pos_mask = labels[test_idx] == 1
        test_pos = np.stack(
            [herb[test_idx][test_pos_mask], adr[test_idx][test_pos_mask]], axis=1
        )
        num_adr = self.get_graph_data()['adr'].x.size(0)
        test_data = self._sample_from_pos_pairs(
            test_pos, num_adr, fold_idx, 'test', neg_ratio=self.test_neg_ratio
        )
        np.savez(test_cache, **test_data)
        return test_data

    def load_fold_data(self, fold_idx: int) -> Tuple[dict, dict]:
        if self._positive_pairs is None:
            self.get_graph_data()

        if fold_idx < 0 or fold_idx >= self.n_folds:
            raise ValueError(f"fold_idx must be in [0, {self.n_folds}), got {fold_idx}")

        if self.neg_ratio != 1:
            return self._resample_fold_split(fold_idx)

        if self.test_neg_ratio != 1:
            fold = self._load_fold_splits()[fold_idx]
            train_idx = fold['train_idx']
            test_idx = fold['test_idx']
            herb = fold['herb_indices']
            adr = fold['adr_indices']
            labels = fold['labels']
            dev_data = {
                'herb_indices': np.asarray(herb[train_idx], dtype=np.int64),
                'adr_indices': np.asarray(adr[train_idx], dtype=np.int64),
                'labels': np.asarray(labels[train_idx], dtype=np.float32),
            }
            test_data = self._resample_test_only(fold_idx)
            return dev_data, test_data

        fold = self._load_fold_splits()[fold_idx]
        train_idx = fold['train_idx']
        test_idx = fold['test_idx']
        herb = fold['herb_indices']
        adr = fold['adr_indices']
        labels = fold['labels']

        dev_data = {
            'herb_indices': np.asarray(herb[train_idx], dtype=np.int64),
            'adr_indices': np.asarray(adr[train_idx], dtype=np.int64),
            'labels': np.asarray(labels[train_idx], dtype=np.float32),
        }
        test_data = {
            'herb_indices': np.asarray(herb[test_idx], dtype=np.int64),
            'adr_indices': np.asarray(adr[test_idx], dtype=np.int64),
            'labels': np.asarray(labels[test_idx], dtype=np.float32),
        }
        return dev_data, test_data
