from experiments.reliable_negative_sampling import (
    CandidateScore,
    normalize_scores,
    score_reliable_negative_candidates,
    select_reliable_negatives,
)


def test_normalize_scores_handles_constant_values():
    assert normalize_scores([3.0, 3.0, 3.0]) == [0.0, 0.0, 0.0]


def test_reliable_negative_score_prefers_low_baseline_and_low_support():
    rows = score_reliable_negative_candidates(
        unobserved_pairs=[(0, 0), (0, 1), (1, 0)],
        baseline_scores={(0, 0): 0.90, (0, 1): 0.10, (1, 0): 0.20},
        structural_support={(0, 0): 5, (0, 1): 0, (1, 0): 1},
        similar_positive_support={(0, 0): 2, (0, 1): 0, (1, 0): 0},
        adr_frequency={0: 20, 1: 1},
    )
    best = max(rows, key=lambda row: row.reliability_score)
    assert best.herb_id == 0
    assert best.adr_id == 1
    assert "low_model_score" in best.reason_flags
    assert "low_structural_support" in best.reason_flags


def test_select_reliable_negatives_is_deterministic_for_ties():
    candidates = [
        CandidateScore(herb_id=2, adr_id=1, reliability_score=0.8),
        CandidateScore(herb_id=0, adr_id=1, reliability_score=0.8),
        CandidateScore(herb_id=1, adr_id=1, reliability_score=0.9),
    ]
    selected = select_reliable_negatives(candidates, count=2, seed=42)
    assert [(x.herb_id, x.adr_id) for x in selected] == [(1, 1), (0, 1)]
