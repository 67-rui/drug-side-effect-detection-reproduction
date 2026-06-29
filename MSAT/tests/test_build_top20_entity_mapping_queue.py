import csv
import json

from scripts.build_top20_entity_mapping_queue import build_mapping_queue, write_outputs


def test_build_mapping_queue_collects_unique_compounds_targets_and_case_links():
    batch_payload = {
        "cases": [
            {
                "herb_id": 1,
                "adr_id": 10,
                "path_contributions": [
                    {
                        "features": ["compound:11", "target:21"],
                        "path_text": "Herb -> Compound #11 -> Target #21 <- ADR",
                        "score_drop": 0.3,
                    }
                ],
                "node_contributions": [
                    {"feature": "compound:11", "node_type": "compound", "node_id": 11, "score_drop": 0.1},
                    {"feature": "target:21", "node_type": "target", "node_id": 21, "score_drop": 0.2},
                ],
            },
            {
                "herb_id": 2,
                "adr_id": 20,
                "path_contributions": [
                    {
                        "features": ["compound:11", "target:30"],
                        "path_text": "Herb -> Compound #11 -> Target #30 <- ADR",
                        "score_drop": 0.05,
                    }
                ],
                "node_contributions": [
                    {"feature": "compound:11", "node_type": "compound", "node_id": 11, "score_drop": 0.4},
                    {"feature": "target:30", "node_type": "target", "node_id": 30, "score_drop": 0.0},
                ],
            },
        ]
    }
    names_payload = {
        "compounds": {"11": {"primary": "Mapped compound", "source": "unit"}},
        "targets": {},
    }

    queue = build_mapping_queue(batch_payload, names_payload)

    assert queue["summary"]["compound_count"] == 1
    assert queue["summary"]["target_count"] == 2
    assert queue["summary"]["unmapped_count"] == 2
    compound = next(row for row in queue["rows"] if row["feature"] == "compound:11")
    assert compound["feature"] == "compound:11"
    assert compound["current_display_name"] == "Mapped compound"
    assert compound["case_count"] == 2
    assert compound["max_score_drop"] == 0.4
    assert "herb 1 -> ADR 10" in compound["case_links"]


def test_write_outputs_creates_json_csv_and_markdown(tmp_path):
    queue = {
        "summary": {"compound_count": 1, "target_count": 0, "mapped_count": 0, "unmapped_count": 1},
        "rows": [
            {
                "feature": "compound:11",
                "node_type": "compound",
                "node_id": 11,
                "current_display_name": "Compound #11",
                "name_source": "unmapped_graph_id",
                "case_count": 1,
                "occurrence_count": 1,
                "max_score_drop": 0.1,
                "mean_score_drop": 0.1,
                "case_links": "herb 1 -> ADR 10",
                "top_path_text": "Herb -> Compound #11 -> ADR",
                "mapping_status": "needs_mapping",
            }
        ],
    }

    out_json = tmp_path / "queue.json"
    out_csv = tmp_path / "queue.csv"
    out_md = tmp_path / "queue.md"
    write_outputs(queue, out_json, out_csv, out_md)

    assert json.loads(out_json.read_text())["summary"]["unmapped_count"] == 1
    rows = list(csv.DictReader(out_csv.open()))
    assert rows[0]["feature"] == "compound:11"
    assert "Top-20 Entity Mapping Queue" in out_md.read_text()
