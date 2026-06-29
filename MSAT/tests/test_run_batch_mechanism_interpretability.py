import csv
import json

from scripts.run_batch_mechanism_interpretability import (
    build_batch_payload_from_contributions,
    compute_topk_mechanism_coverage,
    select_top_mechanism_candidates,
    write_batch_artifacts,
)


def _case_evidence_payload():
    return {
        "rows": [
            {
                "rank": 1,
                "source": "table5_top15",
                "herb_id": 1,
                "adr_id": 10,
                "prediction_score": 0.99,
                "top_mechanism_paths": [
                    "Herb A -> Compound #11 -> Target #21 <- ADR A",
                ],
            },
            {
                "rank": 2,
                "source": "table5_top15",
                "herb_id": 2,
                "adr_id": 20,
                "prediction_score": 0.98,
                "top_mechanism_paths": [],
            },
            {
                "rank": 3,
                "source": "case_zhishi_diarrhoea",
                "herb_id": 3,
                "adr_id": 30,
                "prediction_score": 0.88,
                "top_mechanism_paths": [
                    "Herb B -> Compound #12 -> Target #22 <- ADR B",
                ],
            },
        ]
    }


def _contribution_payload():
    return {
        "experiment": "contribution_quantification",
        "checkpoint_path": "saved_models/best_model_for_prediction.pt",
        "checkpoint_context": "local predictor checkpoint",
        "claim_boundary": "local perturbation sensitivity only",
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "source": "table5_top15",
                "original_score": 0.99,
                "paths": ["Herb A -> Compound #11 -> Target #21 <- ADR A"],
                "mechanism_subgraph": {"nodes": [{"feature": "compound:11"}, {"feature": "target:21"}], "edges": [], "paths": []},
                "node_contributions": [
                    {"feature": "compound:11", "node_type": "compound", "node_id": 11, "score_drop": 0.1, "masked_score": 0.89},
                    {"feature": "target:21", "node_type": "target", "node_id": 21, "score_drop": 0.2, "masked_score": 0.79},
                ],
                "path_contributions": [
                    {"feature": "path:1", "features": ["compound:11", "target:21"], "path_text": "Herb A -> Compound #11 -> Target #21 <- ADR A", "score_drop": 0.3, "masked_score": 0.69}
                ],
            },
            {
                "herb_id": 3,
                "adr_id": 30,
                "source": "case_zhishi_diarrhoea",
                "original_score": 0.88,
                "paths": ["Herb B -> Compound #12 -> Target #22 <- ADR B"],
                "mechanism_subgraph": {"nodes": [{"feature": "compound:12"}, {"feature": "target:22"}], "edges": [], "paths": []},
                "node_contributions": [
                    {"feature": "compound:12", "node_type": "compound", "node_id": 12, "score_drop": -0.05, "masked_score": 0.93},
                    {"feature": "target:22", "node_type": "target", "node_id": 22, "score_drop": 0.0, "masked_score": 0.88},
                ],
                "path_contributions": [
                    {"feature": "path:1", "features": ["compound:12", "target:22"], "path_text": "Herb B -> Compound #12 -> Target #22 <- ADR B", "score_drop": 0.00001, "masked_score": 0.87999}
                ],
            },
        ],
    }


def test_select_top_mechanism_candidates_uses_transitional_sources_and_explicit_paths():
    selected, metadata = select_top_mechanism_candidates(
        final_predictions_payload={},
        case_evidence_payload=_case_evidence_payload(),
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=20,
    )

    assert metadata["candidate_source"] == "transitional_mechanism_supported_artifacts"
    assert metadata["is_final_pu_top_ranking_export"] is False
    assert metadata["requested_top_k"] == 20
    assert metadata["selected_count"] == 2
    assert metadata["explicit_path_candidate_count"] == 2
    assert [(row["herb_id"], row["adr_id"]) for row in selected] == [(1, 10), (3, 30)]


def test_select_top_mechanism_candidates_keeps_nonfinal_top_prediction_boundary():
    final_predictions = {
        "checkpoint_context": {
            "is_final_10fold_export": False,
            "scope_limitations": "fold-scoped pilot export; not final 10-fold export",
        },
        "rows": [
            {
                "rank": 1,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 9,
                "adr_id": 90,
                "prediction_score": 0.97,
                "top_mechanism_paths": [
                    "Herb C -> Compound #13 -> Target #23 <- ADR C",
                ],
            }
        ],
    }

    selected, metadata = select_top_mechanism_candidates(
        final_predictions_payload=final_predictions,
        case_evidence_payload=_case_evidence_payload(),
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=20,
    )

    assert [(row["herb_id"], row["adr_id"]) for row in selected] == [(9, 90)]
    assert metadata["candidate_source"] == "pu_xmsat_top_predictions_nonfinal_export"
    assert metadata["is_final_pu_top_ranking_export"] is False
    assert "not final" in metadata["candidate_source_note"].lower()


def test_select_top_mechanism_candidates_tracks_final_top_prediction_path_coverage():
    final_predictions = {
        "checkpoint_context": {"is_final_10fold_export": True},
        "rows": [
            {
                "rank": 1,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 9,
                "adr_id": 90,
                "prediction_score": 0.99,
                "top_mechanism_paths": [],
            },
            {
                "rank": 2,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 8,
                "adr_id": 80,
                "prediction_score": 0.98,
                "top_mechanism_paths": [
                    "Herb C -> Compound #13 -> Target #23 <- ADR C",
                ],
            },
        ],
    }

    selected, metadata = select_top_mechanism_candidates(
        final_predictions_payload=final_predictions,
        case_evidence_payload={},
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=20,
    )

    assert [(row["herb_id"], row["adr_id"]) for row in selected] == [(8, 80)]
    assert metadata["candidate_source"] == "final_pu_xmsat_top_predictions"
    assert metadata["top_prediction_candidate_count"] == 2
    assert metadata["explicit_path_candidate_count"] == 1
    assert metadata["coverage_missing_candidate_count"] == 1
    assert metadata["coverage_missing_candidates"][0]["coverage_status"] == "missing_explicit_mechanism_path"


def test_topk_coverage_counts_explicit_paths_across_multiple_cutoffs():
    final_predictions = {
        "rows": [
            {
                "rank": 1,
                "herb_id": 1,
                "adr_id": 10,
                "prediction_score": 0.99,
                "top_mechanism_paths": [],
            },
            {
                "rank": 2,
                "herb_id": 2,
                "adr_id": 20,
                "prediction_score": 0.98,
                "top_mechanism_paths": "Herb -> Compound #12 -> Target #22 <- ADR",
            },
            {
                "rank": 3,
                "herb_id": 3,
                "adr_id": 30,
                "prediction_score": 0.97,
                "top_mechanism_paths": "知识图谱中未发现该 CMM–ADR 对的显式短路径",
            },
        ]
    }

    coverage = compute_topk_mechanism_coverage(final_predictions, cutoffs=(1, 2, 3, 5))

    assert coverage == [
        {"top_k": 1, "candidate_count": 1, "explicit_path_candidate_count": 0, "coverage_rate": 0.0},
        {"top_k": 2, "candidate_count": 2, "explicit_path_candidate_count": 1, "coverage_rate": 0.5},
        {"top_k": 3, "candidate_count": 3, "explicit_path_candidate_count": 1, "coverage_rate": 1 / 3},
        {"top_k": 5, "candidate_count": 3, "explicit_path_candidate_count": 1, "coverage_rate": 1 / 3},
    ]


def test_select_top_mechanism_candidates_can_search_wider_pool_than_requested_top_k():
    final_predictions = {
        "checkpoint_context": {"is_final_10fold_export": True},
        "rows": [
            {
                "rank": 1,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 1,
                "adr_id": 10,
                "prediction_score": 0.99,
                "top_mechanism_paths": [],
            },
            {
                "rank": 2,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 2,
                "adr_id": 20,
                "prediction_score": 0.98,
                "top_mechanism_paths": [],
            },
            {
                "rank": 3,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 3,
                "adr_id": 30,
                "prediction_score": 0.97,
                "top_mechanism_paths": "Herb -> Compound #31 -> Target #41 <- ADR",
            },
        ],
    }

    selected, metadata = select_top_mechanism_candidates(
        final_predictions_payload=final_predictions,
        case_evidence_payload={},
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=1,
        candidate_pool_top_k=3,
        coverage_cutoffs=(1, 3),
    )

    assert [(row["herb_id"], row["adr_id"]) for row in selected] == [(3, 30)]
    assert metadata["requested_top_k"] == 1
    assert metadata["candidate_pool_top_k"] == 3
    assert metadata["top_prediction_available_count"] == 3
    assert metadata["candidate_pool_missing_count"] == 0
    assert metadata["candidate_pool_is_complete"] is True
    assert metadata["mechanism_coverage_by_topk"][0]["explicit_path_candidate_count"] == 0
    assert metadata["mechanism_coverage_by_topk"][1]["explicit_path_candidate_count"] == 1


def test_select_top_mechanism_candidates_marks_incomplete_candidate_pool():
    final_predictions = {
        "checkpoint_context": {"is_final_10fold_export": True},
        "rows": [
            {
                "rank": 1,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 1,
                "adr_id": 10,
                "prediction_score": 0.99,
                "top_mechanism_paths": "Herb -> Compound #31 -> Target #41 <- ADR",
            },
            {
                "rank": 2,
                "source": "pu_xmsat_global_unobserved_pairs",
                "herb_id": 2,
                "adr_id": 20,
                "prediction_score": 0.98,
                "top_mechanism_paths": [],
            },
        ],
    }

    _, metadata = select_top_mechanism_candidates(
        final_predictions_payload=final_predictions,
        case_evidence_payload={},
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=1,
        candidate_pool_top_k=5000,
        coverage_cutoffs=(50, 5000),
    )

    assert metadata["candidate_pool_top_k"] == 5000
    assert metadata["top_prediction_available_count"] == 2
    assert metadata["candidate_pool_missing_count"] == 4998
    assert metadata["candidate_pool_is_complete"] is False
    assert metadata["mechanism_coverage_by_topk"][0]["candidate_count"] == 2


def test_select_top_mechanism_candidates_excludes_unparseable_placeholder_paths():
    payload = {
        "rows": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "prediction_score": 0.99,
                "top_mechanism_paths": "知识图谱中未发现该 CMM–ADR 对的显式短路径",
            },
            {
                "herb_id": 2,
                "adr_id": 20,
                "prediction_score": 0.98,
                "top_mechanism_paths": "Herb -> Compound #12 -> Target #22 <- ADR",
            },
        ]
    }

    selected, metadata = select_top_mechanism_candidates(
        final_predictions_payload={},
        case_evidence_payload=payload,
        table5_payload={},
        explanation_payload={},
        structured_mechanism_payload={},
        top_k=20,
    )

    assert metadata["selected_count"] == 1
    assert [(row["herb_id"], row["adr_id"]) for row in selected] == [(2, 20)]


def test_build_batch_payload_from_existing_contributions_marks_context_and_drop_classes():
    candidates, metadata = select_top_mechanism_candidates(
        {},
        _case_evidence_payload(),
        {},
        {},
        {},
        top_k=20,
    )
    payload = build_batch_payload_from_contributions(
        candidates=candidates,
        candidate_metadata=metadata,
        contribution_payload=_contribution_payload(),
        checkpoint_path="saved_models/best_model_for_prediction.pt",
        checkpoint_is_final_pu=False,
    )

    assert payload["experiment"] == "batch_mechanism_interpretability"
    assert payload["candidate_source"] == "transitional_mechanism_supported_artifacts"
    assert payload["checkpoint_is_final_pu_xmsat"] is False
    assert payload["summary"]["quantified_case_count"] == 2
    assert payload["summary"]["coverage_missing_candidate_count"] == 0
    assert payload["summary"]["cases_with_explicit_mechanism_paths"] == 2
    assert payload["summary"]["near_zero_sensitivity_case_count"] == 1
    assert payload["summary"]["negative_score_drop_case_count"] == 1
    assert payload["component_contributions"][0]["feature"] == "compound:11"
    assert payload["component_contributions"][0]["display_name"] == "Compound #11"
    assert payload["component_contributions"][0]["name_source"] == "unmapped_graph_id"
    assert payload["target_contributions"][0]["feature"] == "target:21"
    assert payload["target_contributions"][0]["display_name"] == "Target #21"
    assert payload["pathway_contributions"][0]["path_features"] == "compound:11;target:21"
    assert payload["pathway_contributions"][0]["path_display_features"] == "Compound #11;Target #21"
    assert payload["cases"][1]["sensitivity_class"] == "near_zero"
    assert payload["cases"][1]["has_negative_score_drop"] is True


def test_build_batch_payload_includes_random_control_summary_when_available():
    candidates, metadata = select_top_mechanism_candidates(
        {},
        _case_evidence_payload(),
        {},
        {},
        {},
        top_k=20,
    )
    contribution = _contribution_payload()
    contribution["random_controls"] = {
        "component": [{"score_drop": 0.01}, {"score_drop": 0.02}],
        "target": [{"score_drop": 0.03}],
        "pathway": [{"score_drop": 0.04}, {"score_drop": 0.06}],
    }

    payload = build_batch_payload_from_contributions(
        candidates,
        metadata,
        contribution,
        checkpoint_path="saved_models/best_model_for_prediction.pt",
        checkpoint_is_final_pu=False,
    )

    assert payload["random_control_summary"]["component"]["count"] == 2
    assert payload["random_control_summary"]["component"]["mean_score_drop"] == 0.015
    assert payload["random_control_summary"]["pathway"]["mean_score_drop"] == 0.05
    assert payload["summary"]["has_random_perturbation_controls"] is True


def test_write_batch_artifacts_outputs_json_csv_and_bounded_markdown(tmp_path):
    candidates, metadata = select_top_mechanism_candidates(
        {},
        _case_evidence_payload(),
        {},
        {},
        {},
        top_k=20,
    )
    payload = build_batch_payload_from_contributions(
        candidates,
        metadata,
        _contribution_payload(),
        checkpoint_path="saved_models/best_model_for_prediction.pt",
        checkpoint_is_final_pu=False,
    )
    output_json = tmp_path / "batch.json"
    output_csv = tmp_path / "batch.csv"
    output_md = tmp_path / "batch.md"

    write_batch_artifacts(payload, output_json, output_csv, output_md)

    assert json.loads(output_json.read_text())["summary"]["quantified_case_count"] == 2
    rows = list(csv.DictReader(output_csv.open()))
    assert rows[0]["contribution_group"] == "pathway"
    rendered = output_md.read_text()
    assert "not final PU-XMSAT top-ranking export" in rendered
    assert "not causal" in rendered
