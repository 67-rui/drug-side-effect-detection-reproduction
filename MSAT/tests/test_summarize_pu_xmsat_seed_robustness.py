import pytest

from scripts.summarize_pu_xmsat_seed_robustness import _parse_run_arg, summarize_runs


def _baseline():
    return {
        "overall_metrics": {
            "auc": {"mean": 0.90},
            "auprc": {"mean": 0.80},
            "f1": {"mean": 0.70},
            "mcc": {"mean": 0.60},
        }
    }


def _run(values):
    return {
        "fold_results": [
            {"test_metrics": metrics}
            for metrics in values
        ]
    }


def test_summarize_runs_reports_per_seed_metrics_and_spread():
    run_a = _run([
        {"auc": 0.91, "auprc": 0.82, "f1": 0.72, "mcc": 0.61},
        {"auc": 0.93, "auprc": 0.84, "f1": 0.74, "mcc": 0.63},
    ])
    run_b = _run([
        {"auc": 0.92, "auprc": 0.83, "f1": 0.73, "mcc": 0.62},
        {"auc": 0.94, "auprc": 0.85, "f1": 0.75, "mcc": 0.64},
    ])

    summary = summarize_runs(
        baseline=_baseline(),
        runs=[("hybrid seed=2026", run_a), ("hybrid seed=1337", run_b)],
        metrics=("auc", "auprc", "f1", "mcc"),
    )

    assert summary["baseline_label"] == "reproduced MSAT baseline"
    assert summary["run_count"] == 2
    assert summary["fold_count"] == 2
    assert summary["runs"][0]["label"] == "hybrid seed=2026"
    assert summary["runs"][0]["metrics"]["auc"]["mean"] == pytest.approx(0.92)
    assert summary["runs"][0]["metrics"]["auc"]["delta_vs_baseline"] == pytest.approx(0.02)
    assert summary["runs"][1]["metrics"]["mcc"]["mean"] == pytest.approx(0.63)
    assert summary["seed_spread"]["auc"]["min"] == pytest.approx(0.92)
    assert summary["seed_spread"]["auc"]["max"] == pytest.approx(0.93)
    assert summary["seed_spread"]["auc"]["range"] == pytest.approx(0.01)


def test_parse_run_arg_allows_equals_in_label():
    label, path = _parse_run_arg("hybrid seed=2026=results/run.json")

    assert label == "hybrid seed=2026"
    assert str(path) == "results/run.json"
