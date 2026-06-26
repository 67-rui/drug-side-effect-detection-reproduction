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
        "mean_metrics": {
            "auc": 0.71,
            "auprc": 0.62,
            "f1": 0.55,
            "mcc": 0.40,
        },
    }

    report = build_report(baseline, pu, {"rows": []})

    assert "Backend: full_msat_pu" in report
    assert "PU-XMSAT | 0.7100 | 0.6200" in report
