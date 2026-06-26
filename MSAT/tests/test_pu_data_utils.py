import torch
from torch_geometric.data import HeteroData

from experiments.pu_data_utils import (
    build_positive_pair_set,
    build_unobserved_pairs,
    count_mechanistic_support,
)


def toy_graph():
    data = HeteroData()
    data["herb"].x = torch.randn(3, 4)
    data["adr"].x = torch.randn(3, 4)
    data["target"].x = torch.randn(4, 4)
    data["compound"].x = torch.randn(2, 4)
    data["herb", "causes", "adr"].edge_index = torch.tensor([[0, 1], [1, 2]])
    data["herb", "causes", "adr"].edge_attr = torch.ones(2, 6)
    data["adr", "rev_causes", "herb"].edge_index = torch.tensor([[1, 2], [0, 1]])
    data["adr", "rev_causes", "herb"].edge_attr = torch.ones(2, 6)
    data["herb", "targets", "target"].edge_index = torch.tensor([[0, 2], [0, 3]])
    data["adr", "causes", "target"].edge_index = torch.tensor([[1, 2], [0, 3]])
    data["herb", "contains", "compound"].edge_index = torch.tensor([[0], [0]])
    data["target", "binds", "compound"].edge_index = torch.tensor([[0], [0]])
    return data


def test_positive_pair_set_uses_forward_cmm_adr_edges():
    pairs = build_positive_pair_set(toy_graph())
    assert pairs == {(0, 1), (1, 2)}


def test_unobserved_pairs_exclude_positives():
    pairs = build_unobserved_pairs(num_herbs=3, num_adrs=3, positive_pairs={(0, 1), (1, 2)})
    assert (0, 1) not in pairs
    assert (1, 2) not in pairs
    assert (2, 2) in pairs
    assert len(pairs) == 7


def test_mechanistic_support_counts_direct_and_compound_target_overlap():
    support = count_mechanistic_support(toy_graph(), herb_id=0, adr_id=1)
    assert support["direct_target_overlap"] == 1
    assert support["compound_target_overlap"] == 1
    assert support["total"] == 2
