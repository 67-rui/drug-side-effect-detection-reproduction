import json

from scripts.apply_entity_name_overrides import apply_overrides


def test_apply_overrides_merges_compound_and_target_records_without_touching_existing_names(tmp_path):
    base = {
        "meta": {"method": "base mapping"},
        "herbs": {"1": {"primary": "Herb One", "source": "unit"}},
        "adrs": {"2": {"primary": "ADR Two", "source": "unit"}},
    }
    overrides = {
        "meta": {"curator": "unit-test"},
        "compounds": {
            "761": {
                "primary": "Candidate compound",
                "source": "manual_literature_review",
                "confidence": 0.91,
            }
        },
        "targets": {
            "15721": {
                "primary": "Candidate target",
                "source": "hgnc_biobert_alignment",
                "confidence": 0.72,
            }
        },
    }

    merged = apply_overrides(base, overrides)

    assert merged["herbs"] == base["herbs"]
    assert merged["adrs"] == base["adrs"]
    assert merged["compounds"]["761"]["primary"] == "Candidate compound"
    assert merged["targets"]["15721"]["source"] == "hgnc_biobert_alignment"
    assert merged["meta"]["compound_target_overrides"]["curator"] == "unit-test"
    assert merged["meta"]["compound_target_overrides"]["compound_count"] == 1
    assert merged["meta"]["compound_target_overrides"]["target_count"] == 1


def test_apply_overrides_rejects_records_without_primary_name():
    base = {"meta": {}, "herbs": {}, "adrs": {}}
    overrides = {"targets": {"1": {"source": "bad"}}}

    try:
        apply_overrides(base, overrides)
    except ValueError as exc:
        assert "primary" in str(exc)
    else:
        raise AssertionError("expected invalid override to raise ValueError")
