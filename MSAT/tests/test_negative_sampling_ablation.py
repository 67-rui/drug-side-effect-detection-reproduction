from experiments.run_negative_sampling_ablation import summarize_strategy_counts


def test_summarize_strategy_counts_counts_pair_types():
    rows = [
        {"strategy": "random", "pair_type": "negative"},
        {"strategy": "hybrid", "pair_type": "reliable_negative"},
        {"strategy": "hybrid", "pair_type": "reliable_negative"},
    ]
    summary = summarize_strategy_counts(rows)
    assert summary["random"]["negative"] == 1
    assert summary["hybrid"]["reliable_negative"] == 2
