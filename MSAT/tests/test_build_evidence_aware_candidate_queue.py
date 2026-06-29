import csv
import json

from scripts.build_evidence_aware_candidate_queue import (
    build_evidence_aware_queue,
    write_outputs,
)


def _row(
    rank,
    herb_id,
    adr_id,
    herb_latin,
    adr_pt,
    score=0.99,
    paths=None,
):
    paths = paths if paths is not None else [
        f"{herb_latin} -> Compound #1 -> Target #2 <- {adr_pt}"
    ]
    return {
        "rank": rank,
        "herb_id": herb_id,
        "adr_id": adr_id,
        "herb_latin": herb_latin,
        "herb_name": herb_latin,
        "adr_pt": adr_pt,
        "prediction_score": score,
        "has_explicit_mechanism_path": bool(paths),
        "explicit_mechanism_path_count": len(paths),
        "explicit_mechanism_paths": paths,
    }


def test_build_queue_filters_explicit_paths_and_scores_evidence_retrievability():
    top_predictions = {
        "experiment": "top_predictions",
        "checkpoint_path": "saved_models/formal.pt",
        "checkpoint_context": {"is_final_10fold_export": True},
        "rows": [
            _row(1, 10, 100, "Rare herb", "Spina bifida", 0.999),
            _row(2, 20, 200, "Polypodium glycyrrhiza", "Watery diarrhoea", 0.998),
            _row(3, 30, 300, "No path herb", "Jaundice", 0.997, paths=[]),
        ],
    }
    batch = {
        "cases": [
            {
                "herb_id": 20,
                "adr_id": 200,
                "max_positive_score_drop": 0.0012,
                "sensitivity_class": "positive",
            }
        ]
    }

    queue = build_evidence_aware_queue(top_predictions, batch, top_k=10)

    assert queue["summary"]["explicit_path_candidate_count"] == 2
    assert queue["summary"]["queued_count"] == 2
    assert queue["rows"][0]["herb_latin"] == "Polypodium glycyrrhiza"
    assert queue["rows"][0]["prior_perturbation_score_drop"] == 0.0012
    assert queue["rows"][0]["evidence_retrievability_score"] > queue["rows"][1][
        "evidence_retrievability_score"
    ]
    assert "Polypodium glycyrrhiza" in queue["rows"][0]["pubmed_exact_query"]
    assert queue["claim_boundary"].startswith("This queue reranks")


def test_build_queue_applies_max_per_herb_diversity_before_backfill():
    rows = []
    for index in range(1, 7):
        rows.append(_row(index, 1, 100 + index, "Repeated herb", "Jaundice", 0.999 - index / 1000))
    rows.append(_row(20, 2, 220, "Polypodium glycyrrhiza", "Watery diarrhoea", 0.95))
    rows.append(_row(21, 3, 230, "Crocus sativus", "Sedation", 0.94))
    top_predictions = {"rows": rows}

    queue = build_evidence_aware_queue(top_predictions, {}, top_k=4, max_per_herb=2)

    selected_herbs = [row["herb_latin"] for row in queue["rows"]]
    assert selected_herbs.count("Repeated herb") == 2
    assert len(set(selected_herbs)) == 3
    assert queue["summary"]["diversity_max_per_herb"] == 2


def test_write_outputs_creates_json_csv_and_markdown(tmp_path):
    top_predictions = {
        "rows": [
            _row(1, 10, 100, "Polypodium glycyrrhiza", "Watery diarrhoea", 0.998),
        ]
    }
    queue = build_evidence_aware_queue(top_predictions, {}, top_k=1)
    out_json = tmp_path / "queue.json"
    out_csv = tmp_path / "queue.csv"
    out_md = tmp_path / "queue.md"

    write_outputs(queue, out_json, out_csv, out_md)

    assert json.loads(out_json.read_text())["summary"]["queued_count"] == 1
    rows = list(csv.DictReader(out_csv.open()))
    assert rows[0]["herb_latin"] == "Polypodium glycyrrhiza"
    assert rows[0]["latin"] == "Polypodium glycyrrhiza"
    rendered = out_md.read_text()
    assert "Evidence-Aware Mechanism Candidate Queue" in rendered
    assert "not external validation" in rendered
