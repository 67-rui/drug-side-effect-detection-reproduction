import csv
import json
from pathlib import Path

from scripts.build_direction3_targeted_review_queue import (
    build_targeted_review_queue,
    write_queue_artifacts,
)


def _contribution_payload():
    return {
        "experiment": "contribution_quantification",
        "checkpoint_path": "saved_models/local.pt",
        "checkpoint_context": "local predictor checkpoint",
        "claim_boundary": "local sensitivity only",
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "source": "case_a",
                "original_score": 0.8,
                "path_contributions": [
                    {
                        "features": ["compound:1", "target:20"],
                        "path_text": "Herb A -> compound -> target -> ADR",
                        "score_drop": 0.2,
                    }
                ],
                "node_contributions": [
                    {"feature": "target:20", "node_type": "target", "score_drop": 0.15}
                ],
            },
            {
                "herb_id": 2,
                "adr_id": 20,
                "source": "case_b",
                "original_score": 0.7,
                "path_contributions": [
                    {
                        "features": ["compound:2", "target:30"],
                        "path_text": "Herb B -> compound -> target -> ADR",
                        "score_drop": 0.01,
                    }
                ],
                "node_contributions": [
                    {"feature": "target:30", "node_type": "target", "score_drop": 0.0}
                ],
            },
        ],
    }


def _batch_payload():
    return {
        "experiment": "batch_mechanism_interpretability",
        "checkpoint_path": "saved_models/local.pt",
        "checkpoint_context": "local predictor checkpoint",
        "claim_boundary": "local sensitivity only",
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "source": "case_a",
                "original_score": 0.8,
                "pathway_contributions": [
                    {
                        "features": ["compound:1", "target:20"],
                        "path_features": "compound:1;target:20",
                        "path_text": "Herb A -> compound -> target -> ADR",
                        "score_drop": 0.2,
                    }
                ],
                "target_contributions": [
                    {"feature": "target:20", "node_type": "target", "score_drop": 0.15}
                ],
                "component_contributions": [
                    {"feature": "compound:1", "node_type": "compound", "score_drop": 0.1}
                ],
            },
            {
                "herb_id": 2,
                "adr_id": 20,
                "source": "case_b",
                "original_score": 0.9,
                "pathway_contributions": [
                    {
                        "features": ["compound:2", "target:30"],
                        "path_features": "compound:2;target:30",
                        "path_text": "Herb B -> compound -> target -> ADR",
                        "score_drop": 0.0,
                    }
                ],
                "target_contributions": [
                    {"feature": "target:30", "node_type": "target", "score_drop": 0.5}
                ],
                "component_contributions": [
                    {"feature": "compound:2", "node_type": "compound", "score_drop": 0.6}
                ],
            },
        ],
    }


def _case_evidence_payload():
    return {
        "rows": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "herb_latin": "Herb A",
                "adr_pt": "ADR A",
                "evidence_grade": "C",
                "direct_literature_support": False,
                "mechanistic_support": True,
                "literature_record_count": 3,
                "literature_support_candidate_count": 1,
                "verified_literature_count": 0,
            },
            {
                "herb_id": 2,
                "adr_id": 20,
                "herb_latin": "Herb B",
                "adr_pt": "ADR B",
                "evidence_grade": "D",
                "direct_literature_support": False,
                "mechanistic_support": False,
                "literature_record_count": 0,
                "literature_support_candidate_count": 0,
                "verified_literature_count": 0,
            },
        ]
    }


def _manual_review_payload():
    return {
        "rows": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "manual_review_status": "mechanism_relevant_direction_conflicting",
                "updated_grade_recommendation": "C",
                "paper_use": "hypothesis-generating mechanistic discussion only",
                "rationale": "Mechanism relevant, but direct adverse-reaction direction is not confirmed.",
            }
        ]
    }


def test_build_targeted_review_queue_ranks_by_path_sensitivity_and_keeps_grade_boundary():
    queue = build_targeted_review_queue(
        _contribution_payload(),
        _case_evidence_payload(),
        _manual_review_payload(),
    )

    assert queue["summary"]["case_count"] == 2
    assert queue["summary"]["manual_reviewed_count"] == 1
    assert queue["summary"]["ready_strong_evidence_count"] == 0
    assert queue["rows"][0]["herb_id"] == 1
    assert queue["rows"][0]["top_path_features"] == "compound:1;target:20"
    assert queue["rows"][0]["max_path_score_drop"] == 0.2
    assert queue["rows"][0]["evidence_grade"] == "C"
    assert queue["rows"][0]["updated_grade_recommendation"] == "C"
    assert queue["rows"][0]["review_action"] == "preserve_as_mechanism_screening_boundary"
    assert queue["claim_boundary"].startswith("This queue prioritizes")


def test_batch_review_queue_sorts_by_path_then_target_then_component_drop():
    queue = build_targeted_review_queue(
        _batch_payload(),
        _case_evidence_payload(),
        _manual_review_payload(),
    )

    assert [row["herb_id"] for row in queue["rows"]] == [1, 2]
    assert queue["rows"][0]["max_path_score_drop"] == 0.2
    assert queue["rows"][1]["max_target_score_drop"] == 0.5
    assert queue["rows"][1]["max_component_score_drop"] == 0.6
    assert queue["summary"]["ready_strong_evidence_count"] == 0


def test_batch_review_queue_uses_max_node_drop_after_path_drop():
    payload = _batch_payload()
    payload["cases"][0]["pathway_contributions"][0]["score_drop"] = 0.0
    payload["cases"][0]["target_contributions"][0]["score_drop"] = 0.15
    payload["cases"][0]["component_contributions"][0]["score_drop"] = 0.1
    payload["cases"][1]["pathway_contributions"][0]["score_drop"] = 0.0
    payload["cases"][1]["target_contributions"][0]["score_drop"] = 0.05
    payload["cases"][1]["component_contributions"][0]["score_drop"] = 0.6

    queue = build_targeted_review_queue(
        payload,
        _case_evidence_payload(),
        _manual_review_payload(),
    )

    assert [row["herb_id"] for row in queue["rows"]] == [2, 1]
    assert queue["rows"][0]["max_node_score_drop"] == 0.6
    assert queue["rows"][0]["ready_for_strong_evidence_writeup"] is False


def test_automated_direct_support_does_not_make_ready_without_manual_grade():
    evidence = _case_evidence_payload()
    evidence["rows"][0]["evidence_grade"] = "A"
    evidence["rows"][0]["direct_literature_support"] = True
    evidence["rows"][0]["verified_literature_count"] = 1

    queue = build_targeted_review_queue(
        _contribution_payload(),
        evidence,
        {"rows": []},
    )

    assert queue["rows"][0]["evidence_grade"] == "A"
    assert queue["rows"][0]["direct_literature_support"] is True
    assert queue["summary"]["ready_strong_evidence_count"] == 0
    assert queue["rows"][0]["review_action"] == "target_external_evidence_review"


def test_write_queue_artifacts_outputs_json_csv_and_claim_bounded_markdown(tmp_path):
    queue = build_targeted_review_queue(
        _contribution_payload(),
        _case_evidence_payload(),
        _manual_review_payload(),
    )
    output_json = tmp_path / "queue.json"
    output_csv = tmp_path / "queue.csv"
    output_md = tmp_path / "queue.md"

    write_queue_artifacts(queue, output_json, output_csv, output_md)

    assert json.loads(output_json.read_text())["summary"]["case_count"] == 2
    rows = list(csv.DictReader(output_csv.open()))
    assert rows[0]["top_node_feature"] == "target:20"
    rendered = output_md.read_text()
    assert "not external validation" in rendered
    assert "Targeted Review Queue" in rendered
