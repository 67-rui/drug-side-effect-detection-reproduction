import json

from inference.entity_mapping import EntityNames


def test_entity_names_loads_optional_compound_and_target_records(tmp_path):
    mapping = {
        "meta": {"loaded": True},
        "herbs": {},
        "adrs": {},
        "compounds": {
            "10": {"primary": "Naringin", "source": "unit"},
        },
        "targets": {
            "20": {"primary": "ABCB1", "source": "unit"},
        },
    }
    path = tmp_path / "entity_names.json"
    path.write_text(json.dumps(mapping), encoding="utf-8")

    names = EntityNames.load(path)

    assert names.compound_display(10) == "Naringin"
    assert names.compound_source(10) == "unit"
    assert names.target_display(20) == "ABCB1"
    assert names.target_source(20) == "unit"
    assert names.compound_display(999) == "Compound #999"
    assert names.compound_source(999) == "unmapped_graph_id"
    assert names.target_display(888) == "Target #888"
    assert names.target_source(888) == "unmapped_graph_id"
