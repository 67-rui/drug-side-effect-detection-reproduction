from scripts.summarize_pu_xmsat_results import build_report


def test_report_includes_full_backend_metrics_when_available():
    baseline = {
        "overall_metrics": {
            "auc": {"mean": 0.97},
            "auprc": {"mean": 0.96},
        }
    }
    pu = {
        "status": "completed",
        "training_executed": True,
        "training_backend": "full_msat_pu",
        "threshold_strategy": "val_f1",
        "mean_metrics": {
            "auc": 0.71,
            "auprc": 0.62,
            "f1": 0.55,
            "mcc": 0.40,
        },
        "fold_results": [
            {
                "fold": 0,
                "optimal_threshold": 0.73,
                "val_f1_at_threshold": 0.66,
            },
        ],
    }

    report = build_report(baseline, pu, {"rows": []})

    assert "Backend: full_msat_pu" in report
    assert "Threshold strategy: val_f1" in report
    assert "Fold 0 | 0.7300 | 0.6600" in report
    assert "PU-XMSAT | 0.7100 | 0.6200" in report
