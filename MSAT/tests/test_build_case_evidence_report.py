import csv
import json

from scripts.build_case_evidence_report import (
    build_case_evidence_rows,
    summarize_case_evidence,
)


def _write_csv(path, rows):
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_build_case_evidence_rows_keeps_unverified_literature_as_review_only(tmp_path):
    table5 = tmp_path / "table5_top15.csv"
    explanations = tmp_path / "explanation_case_studies.json"
    literature = tmp_path / "literature.csv"

    _write_csv(
        table5,
        [
            {
                "rank": "1",
                "herb_id": "237",
                "pinyin": "YE CAO MEI",
                "latin": "Fragaria vesca L.",
                "chinese": "野草莓",
                "adr_id": "3989",
                "adr_pt": "Altered state of consciousness",
                "score_pct": "99.939",
                "database_verified": "False",
                "tcmda_evidence": "",
                "mechanistic_support": "True",
                "path_hint": "成分介导：野草莓 → Compound #1073 → Target #2586 ← Altered state of consciousness",
            }
        ],
    )
    explanations.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "herb_id": 237,
                        "adr_id": 3989,
                        "prediction_score": 0.99939,
                        "paths": [{"path": "成分介导：野草莓 → Compound #1073 → Target #2586"}],
                        "contributions": [{"feature": "compound:1073", "score_drop": 0.12}],
                    }
                ]
            }
        )
    )
    _write_csv(
        literature,
        [
            {
                "herb_id": "237",
                "adr_id": "3989",
                "title": "Candidate title",
                "url": "https://example.test/paper",
                "support_candidate": "True",
                "verified_support": "False",
            }
        ],
    )

    rows = build_case_evidence_rows(table5, explanations, literature, limit=5)

    assert len(rows) == 1
    assert rows[0]["evidence_grade"] == "C"
    assert rows[0]["direct_literature_support"] is False
    assert rows[0]["literature_record_count"] == 1
    assert rows[0]["literature_support_candidate_count"] == 1
    assert rows[0]["manual_review_required"] is True
    assert rows[0]["mechanistic_support"] is True
    assert rows[0]["top_contributions"] == "compound:1073:0.12"


def test_summarize_case_evidence_counts_grades_and_mechanisms():
    summary = summarize_case_evidence(
        [
            {
                "evidence_grade": "C",
                "mechanistic_support": True,
                "direct_literature_support": False,
                "literature_record_count": 3,
                "literature_support_candidate_count": 2,
            },
            {
                "evidence_grade": "D",
                "mechanistic_support": False,
                "direct_literature_support": False,
                "literature_record_count": 0,
                "literature_support_candidate_count": 0,
            },
        ]
    )

    assert summary["row_count"] == 2
    assert summary["grade_counts"] == {"C": 1, "D": 1}
    assert summary["mechanistic_support_count"] == 1
    assert summary["direct_literature_support_count"] == 0
    assert summary["literature_record_row_count"] == 1
    assert summary["literature_review_candidate_count"] == 1
