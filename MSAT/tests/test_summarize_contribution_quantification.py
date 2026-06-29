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
    assert summary["near_zero_node_count"] == 0
    assert summary["negative_node_count"] == 1
    assert summary["negative_path_count"] == 1
    assert summary["top_nodes"][0]["feature"] == "target:20"
    assert summary["top_nodes"][0]["case_count"] == 2
    assert summary["top_nodes"][0]["occurrence_count"] == 2
    assert summary["top_nodes"][0]["mean_score_drop"] == 0.3
    assert summary["top_nodes"][0]["positive_drop_count"] == 2
    assert summary["top_paths"][0]["path_features"] == "compound:10;target:20"
    assert summary["top_paths"][0]["case_count"] == 2
    assert summary["top_paths"][0]["occurrence_count"] == 2
    assert summary["top_paths"][0]["negative_drop_count"] == 0
    assert len(summary["all_nodes"]) == 3
    assert len(summary["all_paths"]) == 2


def test_summarize_contributions_keeps_all_aggregates_when_top_k_is_small():
    summary = summarize_contributions(_contribution_payload(), top_k=1)

    assert len(summary["top_nodes"]) == 1
    assert len(summary["top_paths"]) == 1
    assert len(summary["all_nodes"]) == 3
    assert len(summary["all_paths"]) == 2


def test_summarize_batch_payload_splits_component_target_pathway_groups():
    batch_payload = {
        "experiment": "batch_mechanism_interpretability",
        "checkpoint_path": "saved_models/local.pt",
        "checkpoint_context": "fallback contribution rows",
        "candidate_source": "transitional_mechanism_supported_artifacts",
        "candidate_source_note": "not final PU-XMSAT top-ranking export",
        "summary": {
            "requested_top_k": 20,
            "top_prediction_candidate_count": 20,
            "coverage_missing_candidate_count": 19,
            "quantified_case_count": 1,
        },
        "cases": [
            {
                "case_index": 1,
                "herb_id": 1,
                "adr_id": 2,
                "source": "case_a",
                "component_contributions": [
                    {"feature": "compound:10", "node_type": "compound", "node_id": 10, "score_drop": 0.1}
                ],
                "target_contributions": [
                    {"feature": "target:20", "node_type": "target", "node_id": 20, "score_drop": 0.2}
                ],
                "pathway_contributions": [
                    {"path_features": "compound:10;target:20", "features": ["compound:10", "target:20"], "score_drop": -0.1}
                ],
            }
        ],
    }

    summary = summarize_contributions(batch_payload, top_k=3)

    assert summary["source_experiment"] == "batch_mechanism_interpretability"
    assert summary["candidate_source"] == "transitional_mechanism_supported_artifacts"
    assert summary["top_prediction_candidate_count"] == 20
    assert summary["coverage_missing_candidate_count"] == 19
    assert summary["top_components"][0]["feature"] == "compound:10"
    assert summary["top_targets"][0]["feature"] == "target:20"
    assert summary["top_pathways"][0]["path_features"] == "compound:10;target:20"
    assert summary["negative_pathway_count"] == 1


def test_summarize_batch_payload_preserves_display_names_and_sources():
    batch_payload = {
        "experiment": "batch_mechanism_interpretability",
        "cases": [
            {
                "case_index": 1,
                "herb_id": 1,
                "adr_id": 2,
                "source": "case_a",
                "component_contributions": [
                    {
                        "feature": "compound:10",
                        "display_name": "Naringin",
                        "name_source": "unit",
                        "node_type": "compound",
                        "node_id": 10,
                        "score_drop": 0.1,
                    }
                ],
                "target_contributions": [
                    {
                        "feature": "target:20",
                        "display_name": "ABCB1",
                        "name_source": "unit",
                        "node_type": "target",
                        "node_id": 20,
                        "score_drop": 0.2,
                    }
                ],
                "pathway_contributions": [
                    {
                        "path_features": "compound:10;target:20",
                        "path_display_features": "Naringin;ABCB1",
                        "features": ["compound:10", "target:20"],
                        "score_drop": 0.3,
                    }
                ],
            }
        ],
    }

    summary = summarize_contributions(batch_payload, top_k=3)

    assert summary["top_components"][0]["display_name"] == "Naringin"
    assert summary["top_components"][0]["name_source"] == "unit"
    assert summary["top_targets"][0]["display_name"] == "ABCB1"
    assert summary["top_pathways"][0]["path_display_features"] == "Naringin;ABCB1"


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
