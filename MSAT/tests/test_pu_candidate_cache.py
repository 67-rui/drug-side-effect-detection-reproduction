from scripts.build_pu_candidate_cache import row_from_candidate
from experiments.reliable_negative_sampling import CandidateScore


def test_row_from_candidate_is_json_serializable():
    row = row_from_candidate(
        CandidateScore(
            herb_id=1,
            adr_id=2,
            reliability_score=0.75,
            baseline_score=0.10,
            structural_support=0,
            similar_positive_support=0,
            adr_frequency=3,
            reason_flags=("low_model_score",),
        )
    )
    assert row["herb_id"] == 1
    assert row["adr_id"] == 2
    assert row["reason_flags"] == ["low_model_score"]
