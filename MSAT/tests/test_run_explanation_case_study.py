from scripts.run_explanation_case_study import build_case_row


def test_build_case_row_contains_prediction_paths_and_contributions():
    row = build_case_row(
        herb_id=277,
        adr_id=2931,
        score=0.68,
        paths=[{"template": "herb-compound-target-adr"}],
        contributions=[{"feature": "compound:72344", "score_drop": 0.2}],
    )
    assert row["herb_id"] == 277
    assert row["adr_id"] == 2931
    assert row["prediction_score"] == 0.68
    assert row["path_count"] == 1
    assert row["contribution_count"] == 1
