from scripts.summarize_cluster_holdout_generalization import summarize_cluster_holdout_run


def test_summarize_cluster_holdout_run_reports_metrics_and_protocol():
    payload = {
        "split_mode": "cluster_holdout",
        "fold_results": [
            {
                "cluster_protocol": {
                    "holdout_cluster": 0,
                    "heldout_herb_count": 5,
                    "test_positive_count": 12,
                    "hidden_eval_positive_pair_count": 12,
                },
                "pu_pair_counts": {"excluded_herb_count": 5},
                "test_metrics": {"auc": 0.7, "auprc": 0.6, "f1": 0.5, "mcc": 0.4},
            },
            {
                "cluster_protocol": {
                    "holdout_cluster": 1,
                    "heldout_herb_count": 6,
                    "test_positive_count": 10,
                    "hidden_eval_positive_pair_count": 10,
                },
                "pu_pair_counts": {"excluded_herb_count": 6},
                "test_metrics": {"auc": 0.8, "auprc": 0.7, "f1": 0.6, "mcc": 0.5},
            },
        ],
    }

    summary = summarize_cluster_holdout_run(payload)

    assert summary["experiment"] == "pu_xmsat_cluster_holdout_generalization"
    assert summary["fold_count"] == 2
    assert summary["mean_metrics"]["auc"] == 0.75
    assert summary["folds"][0]["holdout_cluster"] == 0
    assert summary["folds"][0]["excluded_herb_count"] == 5
    assert summary["leakage_controls"]["heldout_herbs_filtered_from_pu_training"] is True
    assert summary["cluster_balance"]["min_heldout_herb_count"] == 5
    assert summary["cluster_balance"]["max_heldout_herb_count"] == 6
    assert summary["cluster_balance"]["tiny_holdout_cluster_count"] == 0
    assert "not external clinical validation" in summary["claim_boundary"]


def test_summarize_cluster_holdout_run_flags_tiny_holdout_clusters():
    payload = {
        "split_mode": "cluster_holdout",
        "fold_results": [
            {
                "cluster_protocol": {
                    "holdout_cluster": 0,
                    "heldout_herb_count": 1,
                    "test_positive_count": 5,
                    "hidden_eval_positive_pair_count": 5,
                },
                "pu_pair_counts": {"excluded_herb_count": 1},
                "test_metrics": {"auc": 1.0, "auprc": 1.0, "f1": 0.0, "mcc": 0.0},
            },
            {
                "cluster_protocol": {
                    "holdout_cluster": 1,
                    "heldout_herb_count": 50,
                    "test_positive_count": 100,
                    "hidden_eval_positive_pair_count": 100,
                },
                "pu_pair_counts": {"excluded_herb_count": 50},
                "test_metrics": {"auc": 0.8, "auprc": 0.7, "f1": 0.2, "mcc": 0.1},
            },
        ],
    }

    summary = summarize_cluster_holdout_run(payload)

    assert summary["cluster_balance"]["tiny_holdout_cluster_count"] == 1
    assert summary["cluster_balance"]["tiny_holdout_cluster_threshold"] == 5
    assert "tiny heldout clusters" in summary["interpretation_caveats"][0]


def test_summarize_cluster_holdout_run_reports_non_tiny_robust_metrics():
    payload = {
        "split_mode": "cluster_holdout",
        "fold_results": [
            {
                "cluster_protocol": {
                    "holdout_cluster": 0,
                    "heldout_herb_count": 1,
                    "test_positive_count": 2,
                    "hidden_eval_positive_pair_count": 2,
                },
                "pu_pair_counts": {"excluded_herb_count": 1},
                "test_metrics": {"auc": 0.1, "auprc": 0.2, "f1": 0.0, "mcc": 0.0},
            },
            {
                "cluster_protocol": {
                    "holdout_cluster": 1,
                    "heldout_herb_count": 10,
                    "test_positive_count": 5,
                    "hidden_eval_positive_pair_count": 5,
                },
                "pu_pair_counts": {"excluded_herb_count": 10},
                "test_metrics": {"auc": 0.7, "auprc": 0.6, "f1": 0.3, "mcc": 0.2},
            },
            {
                "cluster_protocol": {
                    "holdout_cluster": 2,
                    "heldout_herb_count": 20,
                    "test_positive_count": 15,
                    "hidden_eval_positive_pair_count": 15,
                },
                "pu_pair_counts": {"excluded_herb_count": 20},
                "test_metrics": {"auc": 0.9, "auprc": 0.8, "f1": 0.5, "mcc": 0.4},
            },
        ],
    }

    summary = summarize_cluster_holdout_run(payload)

    robust = summary["non_tiny_robust_summary"]
    assert robust["included_fold_count"] == 2
    assert robust["excluded_tiny_fold_count"] == 1
    assert robust["mean_metrics"]["auc"] == 0.8
    assert round(robust["std_metrics"]["auc"], 6) == 0.1
    assert robust["weighted_by_test_positive_metrics"]["auc"] == 0.85
    assert robust["included_folds"] == [1, 2]
