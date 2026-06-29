import csv
import json

from scripts.build_mechanism_explanation_layer import (
    build_mechanism_explanation_layer,
    write_mechanism_explanation_outputs,
)


def _payload():
    return {
        "experiment": "contribution_quantification",
        "checkpoint_path": "saved_models/best_model_for_prediction.pt",
        "checkpoint_context": "local predictor checkpoint sensitivity only",
        "claim_boundary": "local perturbation sensitivity only",
        "cases": [
            {
                "herb_id": 277,
                "adr_id": 2931,
                "source": "case_zhishi_diarrhoea",
                "original_score": 0.8,
                "mechanism_subgraph": {
                    "nodes": [
                        {"feature": "compound:523", "node_type": "compound", "node_id": 523},
                        {"feature": "target:3223", "node_type": "target", "node_id": 3223},
                        {"feature": "target:8101", "node_type": "target", "node_id": 8101},
                    ],
                    "edges": [
                        {"source": "compound:523", "target": "target:3223", "path_indices": [1]},
                        {"source": "compound:523", "target": "target:8101", "path_indices": [2]},
                    ],
                    "paths": [
                        {
                            "path_index": 1,
                            "path_text": "Herb -> Compound #523 -> Target #3223 <- ADR",
                            "features": ["compound:523", "target:3223"],
                        },
                        {
                            "path_index": 2,
                            "path_text": "Herb -> Compound #523 -> Target #8101 <- ADR",
                            "features": ["compound:523", "target:8101"],
                        },
                    ],
                },
                "node_contributions": [
                    {
                        "feature": "compound:523",
                        "node_type": "compound",
                        "node_id": 523,
                        "masked_score": 0.7,
                        "score_drop": 0.00001,
                    },
                    {
                        "feature": "target:3223",
                        "node_type": "target",
                        "node_id": 3223,
                        "masked_score": 0.5,
                        "score_drop": 0.3,
                    },
                    {
                        "feature": "target:8101",
                        "node_type": "target",
                        "node_id": 8101,
                        "masked_score": 0.82,
                        "score_drop": -0.02,
                    },
                ],
                "path_contributions": [
                    {
                        "feature": "path:1",
                        "path_index": 1,
                        "path_text": "Herb -> Compound #523 -> Target #3223 <- ADR",
                        "features": ["compound:523", "target:3223"],
                        "masked_score": 0.45,
                        "score_drop": 0.35,
                    },
                    {
                        "feature": "path:2",
                        "path_index": 2,
                        "path_text": "Herb -> Compound #523 -> Target #8101 <- ADR",
                        "features": ["compound:523", "target:8101"],
                        "masked_score": 0.83,
                        "score_drop": -0.03,
                    },
                ],
            }
        ],
    }


def test_build_mechanism_explanation_layer_splits_component_target_and_pathway_contributions():
    layer = build_mechanism_explanation_layer(_payload(), top_k=5)

    assert layer["completion"]["case_count"] == 1
    assert layer["completion"]["all_subgraph_nodes_quantified"] is True
    assert layer["case_summaries"][0]["compound_node_count"] == 1
    assert layer["case_summaries"][0]["target_node_count"] == 2
    assert layer["case_summaries"][0]["node_quantification_coverage"] == "3/3"
    assert layer["component_contributions"][0]["feature"] == "compound:523"
    assert layer["component_contributions"][0]["display_name"] == "Compound #523"
    assert layer["component_contributions"][0]["name_source"] == "unmapped_graph_id"
    assert layer["target_contributions"][0]["feature"] == "target:3223"
    assert layer["target_contributions"][0]["display_name"] == "Target #3223"
    assert layer["pathway_contributions"][0]["path_features"] == "compound:523;target:3223"
    assert layer["pathway_contributions"][0]["path_display_features"] == "Compound #523;Target #3223"
    assert layer["completion"]["positive_component_count"] == 0
    assert layer["completion"]["near_zero_component_count"] == 1
    assert layer["completion"]["positive_target_count"] == 1
    assert layer["completion"]["positive_pathway_count"] == 1
    assert layer["component_contributions"][0]["near_zero_drop_count"] == 1
    assert layer["component_contributions"][0]["positive_drop_count"] == 0


def test_write_mechanism_explanation_outputs_contains_chinese_handoff_tables(tmp_path):
    layer = build_mechanism_explanation_layer(_payload(), top_k=5)
    output_json = tmp_path / "layer.json"
    output_csv = tmp_path / "layer.csv"
    output_md = tmp_path / "layer.md"

    write_mechanism_explanation_outputs(layer, output_json, output_csv, output_md)

    assert json.loads(output_json.read_text())["experiment"] == "mechanism_explanation_layer"
    rows = list(csv.DictReader(output_csv.open()))
    assert {row["contribution_group"] for row in rows} == {"component", "target", "pathway"}
    assert rows[0]["display_name"] or rows[0]["path_display_features"]

    markdown = output_md.read_text()
    assert "关键机制子图" in markdown
    assert "成分贡献" in markdown
    assert "靶点贡献" in markdown
    assert "机制路径贡献" in markdown
    assert "不是因果效应、不是 SHAP 值、不是外部临床验证" in markdown
    assert "当前两个机制案例" not in markdown
    assert "Near-zero" in markdown
    assert "Compound #523" in markdown
    assert "Target #3223" in markdown
