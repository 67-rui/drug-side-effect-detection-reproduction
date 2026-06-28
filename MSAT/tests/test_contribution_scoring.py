from inference.contribution_scoring import (
    build_key_mechanism_subgraph,
    extract_node_refs_from_path,
    extract_node_refs_from_paths,
    rank_score_drops,
    score_node_perturbations,
    score_path_perturbations,
    zero_node_features,
    zero_x_dict_feature_refs,
    zero_x_dict_node_features,
)


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


def test_extract_node_refs_from_paths_dedupes_compounds_and_targets_in_order():
    refs = extract_node_refs_from_paths(
        [
            "Herb -> Compound #1073 -> Target #2586 <- ADR",
            "Herb -> Compound #1073 -> Target #999 <- ADR",
            "Herb -> nobiletin (CID 72344) -> Target #2586 -> ADR",
        ]
    )

    assert refs == [
        {
            "feature": "compound:1073",
            "node_type": "compound",
            "node_id": 1073,
            "label": "Compound #1073",
        },
        {
            "feature": "target:2586",
            "node_type": "target",
            "node_id": 2586,
            "label": "Target #2586",
        },
        {
            "feature": "target:999",
            "node_type": "target",
            "node_id": 999,
            "label": "Target #999",
        },
    ]


def test_extract_node_refs_from_path_preserves_one_path_sequence():
    refs = extract_node_refs_from_path("Herb -> Compound #10 -> Target #20 -> Target #30 <- ADR")

    assert [ref["feature"] for ref in refs] == ["compound:10", "target:20", "target:30"]


def test_build_key_mechanism_subgraph_dedupes_nodes_and_edges():
    subgraph = build_key_mechanism_subgraph(
        [
            "Herb -> Compound #10 -> Target #20 <- ADR",
            "Herb -> Compound #10 -> Target #21 <- ADR",
        ]
    )

    assert [node["feature"] for node in subgraph["nodes"]] == [
        "compound:10",
        "target:20",
        "target:21",
    ]
    assert subgraph["edges"] == [
        {"source": "compound:10", "target": "target:20", "path_indices": [1]},
        {"source": "compound:10", "target": "target:21", "path_indices": [2]},
    ]
    assert subgraph["paths"][0]["features"] == ["compound:10", "target:20"]


def test_zero_x_dict_node_features_only_clones_selected_node_type():
    import torch

    x_dict = {
        "compound": torch.ones(2, 3),
        "target": torch.ones(2, 3) * 2,
    }
    masked = zero_x_dict_node_features(x_dict, "compound", 1)

    assert x_dict["compound"][1].sum().item() == 3
    assert masked["compound"][1].sum().item() == 0
    assert masked["target"] is x_dict["target"]


def test_zero_x_dict_feature_refs_clones_each_selected_type_once():
    import torch

    x_dict = {
        "compound": torch.ones(3, 2),
        "target": torch.ones(3, 2) * 2,
        "adr": torch.ones(3, 2) * 3,
    }
    refs = [
        {"feature": "compound:1", "node_type": "compound", "node_id": 1},
        {"feature": "target:0", "node_type": "target", "node_id": 0},
        {"feature": "target:2", "node_type": "target", "node_id": 2},
    ]

    masked = zero_x_dict_feature_refs(x_dict, refs)

    assert x_dict["compound"][1].sum().item() == 2
    assert x_dict["target"][0].sum().item() == 4
    assert masked["compound"][1].sum().item() == 0
    assert masked["target"][0].sum().item() == 0
    assert masked["target"][2].sum().item() == 0
    assert masked["adr"] is x_dict["adr"]


def test_score_node_perturbations_sorts_score_drops():
    refs = [
        {"feature": "compound:1", "node_type": "compound", "node_id": 1, "label": "Compound #1"},
        {"feature": "target:2", "node_type": "target", "node_id": 2, "label": "Target #2"},
    ]

    rows = score_node_perturbations(
        original_score=0.9,
        node_refs=refs,
        score_masked=lambda ref: {"compound:1": 0.2, "target:2": 0.7}[ref["feature"]],
    )

    assert rows[0]["feature"] == "compound:1"
    assert rows[0]["score_drop"] == 0.7
    assert rows[0]["node_type"] == "compound"
    assert rows[1]["feature"] == "target:2"


def test_score_path_perturbations_sorts_whole_path_drops():
    paths = [
        {
            "path_index": 1,
            "path_text": "A",
            "features": ["compound:1", "target:2"],
            "feature_refs": [
                {"feature": "compound:1", "node_type": "compound", "node_id": 1},
                {"feature": "target:2", "node_type": "target", "node_id": 2},
            ],
        },
        {
            "path_index": 2,
            "path_text": "B",
            "features": ["compound:3", "target:4"],
            "feature_refs": [
                {"feature": "compound:3", "node_type": "compound", "node_id": 3},
                {"feature": "target:4", "node_type": "target", "node_id": 4},
            ],
        },
    ]

    rows = score_path_perturbations(
        original_score=0.9,
        paths=paths,
        score_masked_path=lambda path: {1: 0.8, 2: 0.3}[path["path_index"]],
    )

    assert rows[0]["feature"] == "path:2"
    assert rows[0]["features"] == ["compound:3", "target:4"]
    assert rows[0]["score_drop"] == 0.6
