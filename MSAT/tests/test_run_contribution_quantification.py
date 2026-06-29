import json

from scripts.run_contribution_quantification import (
    build_case_contribution_payload,
    infer_checkpoint_context,
    sample_random_node_refs,
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


def test_select_mechanistic_cases_can_quantify_all_subgraph_node_refs():
    payload = {
        "rows": [
            {
                "herb_id": 1,
                "adr_id": 2,
                "paths": [
                    {"path": "Herb -> Compound #10 -> Target #20 <- ADR"},
                    {"path": "Herb -> Compound #30 -> Target #40 <- ADR"},
                    {"path": "Herb -> Compound #50 -> Target #60 <- ADR"},
                ],
            }
        ]
    }

    cases = select_mechanistic_cases(payload, max_cases=1, max_features=0)

    assert [ref["feature"] for ref in cases[0]["node_refs"]] == [
        "compound:10",
        "target:20",
        "compound:30",
        "target:40",
        "compound:50",
        "target:60",
    ]
    assert cases[0]["available_node_ref_count"] == 6
    assert cases[0]["quantified_node_ref_count"] == 6
    assert cases[0]["node_refs_truncated"] is False


def test_select_mechanistic_cases_accepts_top_prediction_mechanism_paths():
    payload = {
        "rows": [
            {
                "herb_id": 5,
                "adr_id": 6,
                "top_mechanism_paths": [
                    "Herb -> Compound #77 -> Target #88 <- ADR",
                ],
            }
        ]
    }

    cases = select_mechanistic_cases(payload, max_cases=5)

    assert len(cases) == 1
    assert cases[0]["path_texts"] == ["Herb -> Compound #77 -> Target #88 <- ADR"]
    assert [ref["feature"] for ref in cases[0]["node_refs"]] == [
        "compound:77",
        "target:88",
    ]


def test_select_mechanistic_cases_deduplicates_top_and_explicit_paths():
    payload = {
        "rows": [
            {
                "herb_id": 5,
                "adr_id": 6,
                "top_mechanism_paths": [
                    "Herb -> Compound #77 -> Target #88 <- ADR",
                ],
                "explicit_mechanism_paths": [
                    "Herb -> Compound #77 -> Target #88 <- ADR",
                ],
            }
        ]
    }

    cases = select_mechanistic_cases(payload, max_cases=5)

    assert cases[0]["path_texts"] == ["Herb -> Compound #77 -> Target #88 <- ADR"]


def test_infer_checkpoint_context_keeps_pu_fold_checkpoint_nonfinal():
    context = infer_checkpoint_context(
        "saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt",
        checkpoint_is_final_pu=False,
    )

    assert "PU-XMSAT checkpoint" in context
    assert "not final" in context.lower()


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
    assert payload["node_contributions"][0]["display_name"] == "Compound #10"
    assert payload["node_contributions"][0]["name_source"] == "unmapped_graph_id"
    assert payload["node_contributions"][0]["score_drop"] == 0.4
    assert payload["path_contributions"][0]["feature"] == "path:1"
    assert payload["path_contributions"][0]["score_drop"] == 0.2
    assert payload["mechanism_subgraph"]["nodes"][0]["feature"] == "compound:10"
    assert json.loads(json.dumps(payload))


def test_build_case_contribution_payload_can_include_random_controls():
    case = {
        "herb_id": 1,
        "adr_id": 2,
        "source": "unit",
        "path_texts": ["Herb -> Compound #10 -> Target #20 <- ADR"],
        "node_refs": [
            {"feature": "compound:10", "node_type": "compound", "node_id": 10, "label": "Compound #10"},
        ],
    }

    payload = build_case_contribution_payload(
        case,
        original_score=0.8,
        score_masked=lambda ref: 0.7,
        score_masked_path=lambda path: 0.6,
        random_node_refs=[
            {"feature": "compound:11", "node_type": "compound", "node_id": 11, "label": "Compound #11"},
            {"feature": "target:21", "node_type": "target", "node_id": 21, "label": "Target #21"},
        ],
        random_path_controls=[
            {
                "path_index": 1,
                "path_text": "random same-type path control",
                "features": ["compound:11", "target:21"],
                "feature_refs": [
                    {"feature": "compound:11", "node_type": "compound", "node_id": 11},
                    {"feature": "target:21", "node_type": "target", "node_id": 21},
                ],
            }
        ],
    )

    assert payload["random_controls"]["component"][0]["feature"] == "compound:11"
    assert payload["random_controls"]["target"][0]["feature"] == "target:21"
    assert payload["random_controls"]["pathway"][0]["features"] == ["compound:11", "target:21"]


def test_sample_random_node_refs_uses_same_node_type_and_excludes_case_nodes():
    import torch

    refs = [
        {"feature": "compound:1", "node_type": "compound", "node_id": 1},
        {"feature": "target:2", "node_type": "target", "node_id": 2},
    ]
    sampled = sample_random_node_refs(
        refs,
        {"compound": torch.zeros((4, 2)), "target": torch.zeros((5, 2))},
        seed=3,
        controls_per_type=1,
    )

    assert {row["node_type"] for row in sampled} == {"compound", "target"}
    assert ("compound", 1) not in {(row["node_type"], row["node_id"]) for row in sampled}
    assert ("target", 2) not in {(row["node_type"], row["node_id"]) for row in sampled}


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
