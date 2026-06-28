import json

from scripts.run_contribution_quantification import (
    build_case_contribution_payload,
    select_mechanistic_cases,
    write_outputs,
)


def test_select_mechanistic_cases_keeps_rows_with_explicit_node_refs():
    payload = {
        "rows": [
            {
                "herb_id": 1,
                "adr_id": 2,
                "paths": [{"path": "Herb -> Compound #10 -> Target #20 <- ADR"}],
            },
            {
                "herb_id": 3,
                "adr_id": 4,
                "paths": [{"path": "No explicit short path"}],
            },
        ]
    }

    cases = select_mechanistic_cases(payload, max_cases=5)

    assert len(cases) == 1
    assert cases[0]["node_refs"][0]["feature"] == "compound:10"


def test_build_case_contribution_payload_contains_ranked_rows():
    case = {
        "herb_id": 1,
        "adr_id": 2,
        "source": "unit",
        "path_texts": [
            "Herb -> Compound #10 -> Target #20 <- ADR",
            "Herb -> Compound #30 -> Target #40 <- ADR",
        ],
        "node_refs": [
            {"feature": "compound:10", "node_type": "compound", "node_id": 10, "label": "Compound #10"},
            {"feature": "target:20", "node_type": "target", "node_id": 20, "label": "Target #20"},
        ],
    }

    payload = build_case_contribution_payload(
        case,
        original_score=0.8,
        score_masked=lambda ref: {"compound:10": 0.4, "target:20": 0.7}[ref["feature"]],
        score_masked_path=lambda path: {1: 0.6, 2: 0.75}[path["path_index"]],
    )

    assert payload["herb_id"] == 1
    assert payload["adr_id"] == 2
    assert payload["original_score"] == 0.8
    assert payload["node_contributions"][0]["feature"] == "compound:10"
    assert payload["node_contributions"][0]["score_drop"] == 0.4
    assert payload["path_contributions"][0]["feature"] == "path:1"
    assert payload["path_contributions"][0]["score_drop"] == 0.2
    assert payload["mechanism_subgraph"]["nodes"][0]["feature"] == "compound:10"
    assert json.loads(json.dumps(payload))


def test_write_outputs_records_checkpoint_metadata(tmp_path):
    payload = {
        "created_at": "2026-06-28T00:00:00",
        "checkpoint_path": "saved_models/best_model_for_prediction.pt",
        "checkpoint_context": "not final PU attribution",
        "claim_boundary": "local perturbation sensitivity only",
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 2,
                "source": "unit",
                "original_score": 0.8,
                "mechanism_subgraph": {
                    "nodes": [],
                    "edges": [],
                    "paths": [],
                },
                "node_contributions": [
                    {
                        "feature": "compound:10",
                        "node_type": "compound",
                        "node_id": 10,
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
                        "masked_score": 0.5,
                        "score_drop": 0.3,
                    }
                ],
            }
        ],
    }

    output_json = tmp_path / "contribution.json"
    output_csv = tmp_path / "contribution.csv"
    output_md = tmp_path / "contribution.md"

    write_outputs(payload, output_json, output_csv, output_md)

    text = output_md.read_text()
    assert "Checkpoint: `saved_models/best_model_for_prediction.pt`" in text
    assert "not final PU attribution" in text
    assert "local perturbation sensitivity only" in text
    assert "Negative score drops mean the score increased after masking" in text
    assert "Node Contributions" in text
    assert "Path Contributions" in text
