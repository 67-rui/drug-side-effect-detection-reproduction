import pytest

from scripts.compare_pu_xmsat_to_baseline import build_comparison, csv_rows


def _payload(rows):
    return {
        "fold_results": [
            {"fold": idx, "test_metrics": metrics}
            for idx, metrics in enumerate(rows)
        ]
    }


def test_build_comparison_reports_paired_fold_statistics():
    baseline = _payload([
        {"auc": 0.80},
        {"auc": 0.70},
        {"auc": 0.90},
    ])
    pu = _payload([
        {"auc": 0.90},
        {"auc": 0.69},
        {"auc": 0.91},
    ])

    comparison = build_comparison(baseline, pu, metrics=("auc",))
    row = comparison["metrics"][0]

    assert comparison["fold_count"] == 3
    assert row["metric"] == "auc"
    assert row["baseline_mean"] == pytest.approx(0.80)
    assert row["pu_mean"] == pytest.approx(0.8333333333)
    assert row["mean_delta"] == pytest.approx(0.0333333333)
    assert row["pu_wins"] == 2
    assert row["pu_losses"] == 1
    assert row["ties"] == 0
    assert row["paired_ttest_p"] is not None
    assert 0.0 <= row["paired_ttest_p"] <= 1.0


def test_build_comparison_keeps_comparison_labels():
    baseline = _payload([
        {"auc": 0.80},
        {"auc": 0.82},
        {"auc": 0.81},
    ])
    pu = _payload([
        {"auc": 0.81},
        {"auc": 0.81},
        {"auc": 0.83},
    ])

    comparison = build_comparison(
        baseline,
        pu,
        metrics=("auc",),
        baseline_label="random seed=2026",
        pu_label="hybrid seed=2026",
    )

    assert comparison["baseline_label"] == "random seed=2026"
    assert comparison["pu_label"] == "hybrid seed=2026"
    assert "hybrid seed=2026" in comparison["interpretation"]
    assert "random seed=2026" in comparison["interpretation"]


def test_csv_rows_include_report_ready_columns():
    comparison = {
        "metrics": [
            {
                "metric": "auc",
                "baseline_mean": 0.97927,
                "pu_mean": 0.97962,
                "mean_delta": 0.00035,
                "pu_wins": 7,
                "pu_losses": 3,
                "ties": 0,
                "paired_ttest_p": 0.324195,
            }
        ]
    }

    rows = csv_rows(comparison)

    assert rows == [
        {
            "metric": "auc",
            "baseline_mean": "0.979270",
            "pu_mean": "0.979620",
            "mean_delta": "+0.000350",
            "pu_wins": "7",
            "pu_losses": "3",
            "ties": "0",
            "paired_ttest_p": "0.324195",
        }
    ]
