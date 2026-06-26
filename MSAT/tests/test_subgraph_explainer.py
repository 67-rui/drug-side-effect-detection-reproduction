import torch
from torch_geometric.data import HeteroData

from inference.subgraph_explainer import extract_path_templates


def toy_graph():
    data = HeteroData()
    data["herb"].x = torch.randn(1, 4)
    data["compound"].x = torch.randn(1, 4)
    data["target"].x = torch.randn(1, 4)
    data["adr"].x = torch.randn(1, 4)
    data["herb", "contains", "compound"].edge_index = torch.tensor([[0], [0]])
    data["target", "binds", "compound"].edge_index = torch.tensor([[0], [0]])
    data["adr", "causes", "target"].edge_index = torch.tensor([[0], [0]])
    return data


def test_extract_path_templates_finds_compound_target_adr_path():
    paths = extract_path_templates(toy_graph(), herb_id=0, adr_id=0)
    assert paths == [
        {
            "template": "herb-compound-target-adr",
            "herb_id": 0,
            "compound_id": 0,
            "target_id": 0,
            "adr_id": 0,
        }
    ]
