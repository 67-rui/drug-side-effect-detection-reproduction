from inference.contribution_scoring import rank_score_drops, zero_node_features


def test_rank_score_drops_orders_largest_drop_first():
    ranked = rank_score_drops(
        original_score=0.9,
        masked_scores={"compound:1": 0.2, "target:2": 0.7},
    )
    assert ranked[0]["feature"] == "compound:1"
    assert ranked[0]["score_drop"] == 0.7


def test_zero_node_features_does_not_mutate_original():
    import torch
    from torch_geometric.data import HeteroData

    data = HeteroData()
    data["compound"].x = torch.ones(2, 3)
    masked = zero_node_features(data, "compound", [1])
    assert data["compound"].x[1].sum().item() == 3
    assert masked["compound"].x[1].sum().item() == 0
