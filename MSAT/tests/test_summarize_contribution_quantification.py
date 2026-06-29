import csv
import json

from scripts.summarize_contribution_quantification import (
    load_contribution_payload,
    summarize_contributions,
    write_summary_artifacts,
)


def _contribution_payload():
    return {
        "experiment": "contribution_quantification",
        "checkpoint_path": "saved_models/best_model_for_prediction.pt",
        "checkpoint_context": "local predictor checkpoint sensitivity only",
        "claim_boundary": "local perturbation sensitivity only",
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 2,
                "source": "case_a",
                "node_contributions": [
                    {
                        "feature": "target:20",
                        "node_type": "target",
                        "node_id": 20,
                        "masked_score": 0.6,
                        "score_drop": 0.2,
                    },
                    {
                        "feature": "compound:10",
                        "node_type": "compound",
                        "node_id": 10,
                        "masked_score": 0.7,
                        "score_drop": 0.1,
                    },
                    {
                        "feature": "target:30",
                        "node_type": "target",
                        "node_id": 30,
                        "masked_score": 0.9,
                        "score_drop": -0.1,
                    },
                ],
                "path_contributions": [
                    {
                        "feature": "path:1",
                        "path_index": 1,
                        "path_text": "Herb -> Compound #10 -> Target #20 <- ADR",
                        "features": ["compound:10", "target:20"],
                        "masked_score": 0.5,
                        "score_drop": 0.3,
                    },
                    {
                        "feature": "path:2",
                        "path_index": 2,
                        "path_text": "Herb -> Compound #99 -> Target #30 <- ADR",
                        "features": ["compound:99", "target:30"],
                        "masked_score": 0.9,
                        "score_drop": -0.1,
                    },
                ],
            },
            {
                "herb_id": 3,
                "adr_id": 4,
                "source": "case_b",
                "node_contributions": [
                    {
                        "feature": "target:20",
                        "node_type": "target",
                        "node_id": 20,
                        "masked_score": 0.4,
                        "score_drop": 0.4,
                    }
                ],
                "path_contributions": [
                    {
                        "feature": "path:1",
                        "path_index": 1,
                        "path_text": "Herb -> Compound #10 -> Target #20 <- ADR",
                        "features": ["compound:10", "target:20"],
                        "masked_score": 0.6,
                        "score_drop": 0.1,
                    }
                ],
            },
        ],
    }


def test_summarize_contributions_aggregates_repeated_nodes_and_paths():
    summary = summarize_contributions(_contribution_payload(), top_k=5)

    assert summary["case_count"] == 2
    assert summary["positive_node_count"] == 3
    assert summary["positive_path_count"] == 2
    assert summary["top_nodes"][0]["feature"] == "target:20"
    assert summary["top_nodes"][0]["case_count"] == 2
    assert summary["top_nodes"][0]["occurrence_count"] == 2
    assert summary["top_nodes"][0]["mean_score_drop"] == 0.3
    assert summary["top_nodes"][0]["positive_drop_count"] == 2
    assert summary["top_paths"][0]["path_features"] == "compound:10;target:20"
    assert summary["top_paths"][0]["case_count"] == 2
    assert summary["top_paths"][0]["occurrence_count"] == 2
    assert summary["top_paths"][0]["negative_drop_count"] == 0


def test_summary_artifacts_preserve_claim_boundaries(tmp_path):
    input_json = tmp_path / "contribution.json"
    output_json = tmp_path / "aggregate.json"
    output_csv = tmp_path / "aggregate.csv"
    output_md = tmp_path / "aggregate.md"
    input_json.write_text(json.dumps(_contribution_payload()))

    payload = load_contribution_payload(input_json)
    summary = summarize_contributions(payload, top_k=3)
    write_summary_artifacts(summary, output_json, output_csv, output_md)

    assert json.loads(output_json.read_text())["checkpoint_context"] == "local predictor checkpoint sensitivity only"

    rows = list(csv.DictReader(output_csv.open()))
    assert rows[0]["aggregate_type"] == "path"
    assert rows[0]["path_features"] == "compound:10;target:20"

    markdown = output_md.read_text()
    assert "These are perturbation sensitivity aggregates, not causal or SHAP attributions." in markdown
    assert "local predictor checkpoint sensitivity only" in markdown
    assert "Top Path Aggregates" in markdown
