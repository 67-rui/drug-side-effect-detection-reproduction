import pytest

from scripts.summarize_pu_xmsat_weight_sensitivity import summarize_weight_runs


def _baseline():
    return {
        "overall_metrics": {
            "auc": {"mean": 0.90},
            "auprc": {"mean": 0.80},
            "f1": {"mean": 0.70},
            "mcc": {"mean": 0.60},
        }
    }


def _run(first_auc, second_auc):
    return {
        "fold_results": [
            {"test_metrics": {"auc": first_auc, "auprc": 0.82, "f1": 0.72, "mcc": 0.62}},
            {"test_metrics": {"auc": second_auc, "auprc": 0.84, "f1": 0.74, "mcc": 0.64}},
        ]
    }


def test_summarize_weight_runs_reports_baseline_and_reference_deltas():
    summary = summarize_weight_runs(
        baseline=_baseline(),
        reference_label="u0.2 rn0.8",
        runs=[
            ("u0.1 rn0.8", 0.1, 0.8, _run(0.91, 0.93)),
            ("u0.2 rn0.8", 0.2, 0.8, _run(0.92, 0.94)),
            ("u0.4 rn0.8", 0.4, 0.8, _run(0.94, 0.96)),
        ],
        metrics=("auc", "auprc", "f1", "mcc"),
    )

    assert summary["reference_label"] == "u0.2 rn0.8"
    assert summary["run_count"] == 3
    assert summary["fold_count"] == 2
    low, default, high = summary["runs"]
    assert low["unlabeled_weight"] == pytest.approx(0.1)
    assert default["metrics"]["auc"]["mean"] == pytest.approx(0.93)
    assert low["metrics"]["auc"]["delta_vs_baseline"] == pytest.approx(0.02)
    assert low["metrics"]["auc"]["delta_vs_reference"] == pytest.approx(-0.01)
    assert high["metrics"]["auc"]["delta_vs_reference"] == pytest.approx(0.02)
