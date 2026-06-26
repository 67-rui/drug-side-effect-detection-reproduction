from scripts.build_pu_candidate_cache import _bounded_unobserved_pairs, row_from_candidate
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


def test_bounded_unobserved_pairs_random_selection_avoids_prefix_bias():
    pairs = _bounded_unobserved_pairs(
        num_herbs=5,
        num_adrs=10,
        positive_pairs=set(),
        max_candidates=10,
        seed=7,
        selection="random",
    )

    assert len(pairs) == 10
    assert len({herb_id for herb_id, _ in pairs}) > 1
    assert pairs != [(0, adr_id) for adr_id in range(10)]
    assert pairs == _bounded_unobserved_pairs(
        num_herbs=5,
        num_adrs=10,
        positive_pairs=set(),
        max_candidates=10,
        seed=7,
        selection="random",
    )


def test_bounded_unobserved_pairs_prefix_selection_keeps_legacy_order():
    pairs = _bounded_unobserved_pairs(
        num_herbs=5,
        num_adrs=10,
        positive_pairs=set(),
        max_candidates=10,
        seed=7,
        selection="prefix",
    )

    assert pairs == [(0, adr_id) for adr_id in range(10)]
