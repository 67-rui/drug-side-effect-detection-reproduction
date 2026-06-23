import numpy as np
import torch
from torch_geometric.data import HeteroData

import train
from baselines import common


def _toy_cmm_adr_graph():
    data = HeteroData()
    data['herb'].x = torch.zeros((3, 1), dtype=torch.float32)
    data['adr'].x = torch.zeros((3, 1), dtype=torch.float32)

    data['herb', 'causes', 'adr'].edge_index = torch.tensor(
        [[0, 1, 2], [0, 1, 2]], dtype=torch.long
    )
    data['herb', 'causes', 'adr'].edge_attr = torch.arange(
        18, dtype=torch.float32
    ).reshape(3, 6)
    data['adr', 'rev_causes', 'herb'].edge_index = torch.tensor(
        [[0, 1, 2], [0, 1, 2]], dtype=torch.long
    )
    data['adr', 'rev_causes', 'herb'].edge_attr = torch.arange(
        18, dtype=torch.float32
    ).reshape(3, 6)
    return data


def _forward_pairs(data):
    edge_index = data['herb', 'causes', 'adr'].edge_index
    return set(zip(edge_index[0].tolist(), edge_index[1].tolist()))


def _reverse_pairs_as_forward(data):
    edge_index = data['adr', 'rev_causes', 'herb'].edge_index
    return set(zip(edge_index[1].tolist(), edge_index[0].tolist()))


def test_train_protocol_removes_validation_and_test_positive_edges():
    hidden_pairs = train._evaluation_positive_pair_set(
        val_h=np.array([1, 0]),
        val_a=np.array([1, 2]),
        val_y=np.array([1, 0], dtype=np.float32),
        test_h=np.array([2, 0]),
        test_a=np.array([2, 1]),
        test_y=np.array([1, 0], dtype=np.float32),
    )

    clean = train._remove_cmm_adr_pairs(_toy_cmm_adr_graph(), hidden_pairs)

    assert _forward_pairs(clean) == {(0, 0)}
    assert _reverse_pairs_as_forward(clean) == {(0, 0)}
    assert clean['herb', 'causes', 'adr'].edge_attr.shape == (1, 6)
    assert clean['adr', 'rev_causes', 'herb'].edge_attr.shape == (1, 6)


def test_baseline_protocol_removes_validation_and_test_positive_edges():
    hidden_pairs = common.evaluation_positive_pair_set(
        val_h=np.array([1, 0]),
        val_a=np.array([1, 2]),
        val_y=np.array([1, 0], dtype=np.float32),
        test_h=np.array([2, 0]),
        test_a=np.array([2, 1]),
        test_y=np.array([1, 0], dtype=np.float32),
    )

    clean = common.remove_cmm_adr_pairs(_toy_cmm_adr_graph(), hidden_pairs)

    assert _forward_pairs(clean) == {(0, 0)}
    assert _reverse_pairs_as_forward(clean) == {(0, 0)}
