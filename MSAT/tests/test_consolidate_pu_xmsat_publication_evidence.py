from scripts.consolidate_pu_xmsat_publication_evidence import (
    build_publication_evidence_summary,
    write_publication_evidence_artifacts,
)


def _baseline():
    return {
        "overall_metrics": {
            "auc": {"mean": 0.979271},
            "auprc": {"mean": 0.977095},
            "f1": {"mean": 0.931451},
            "mcc": {"mean": 0.862520},
        }
    }


def _run(auc, auprc, f1, mcc):
    return {
        "fold_results": [
            {"test_metrics": {"auc": auc, "auprc": auprc, "f1": f1, "mcc": mcc}},
            {
                "test_metrics": {
                    "auc": auc + 0.0002,
                    "auprc": auprc + 0.0002,
                    "f1": f1 + 0.0002,
                    "mcc": mcc + 0.0002,
                }
            },
        ],
        "mean_metrics": {"auc": auc, "auprc": auprc, "f1": f1, "mcc": mcc},
    }


def test_build_publication_evidence_summary_consolidates_main_and_supporting_evidence():
    summary = build_publication_evidence_summary(
        baseline=_baseline(),
        main_runs=[
            ("hybrid_seed2026", _run(0.9804, 0.9779, 0.9351, 0.8684)),
            ("hybrid_seed1337", _run(0.9803, 0.9780, 0.9348, 0.8683)),
        ],
        ablation_runs=[
            ("random_seed2026", _run(0.9797, 0.9777, 0.9338, 0.8661)),
        ],
        seed_robustness={
            "seed_spread": {
                "auc": {"range": 0.000028},
                "auprc": {"range": 0.000054},
                "f1": {"range": 0.000297},
                "mcc": {"range": 0.000078},
            }
        },
        weight_sensitivity={
            "reference_label": "u0.2_rn0.8",
            "runs": [{"label": "u0.2_rn0.8"}, {"label": "u0.1_rn0.8"}],
        },
    )

    assert summary["experiment"] == "pu_xmsat_publication_evidence_consolidation"
    assert summary["baseline"]["metrics"]["auc"] == 0.979271
    assert summary["main_claim"]["supported_metrics"] == ["auc", "auprc", "f1", "mcc"]
    assert summary["main_runs"][0]["metrics"]["f1"]["delta_vs_baseline"] > 0
    assert summary["ablation"]["run_count"] == 1
    assert summary["seed_robustness"]["max_seed_spread"] == 0.000297
    assert summary["weight_sensitivity"]["run_count"] == 2
    assert "not causal" in summary["claim_boundary"].lower()


def test_write_publication_evidence_artifacts_outputs_markdown_and_json(tmp_path):
    summary = build_publication_evidence_summary(
        baseline=_baseline(),
        main_runs=[("hybrid_seed2026", _run(0.9804, 0.9779, 0.9351, 0.8684))],
        ablation_runs=[],
        seed_robustness={},
        weight_sensitivity={},
    )
    output_json = tmp_path / "summary.json"
    output_md = tmp_path / "summary.md"

    write_publication_evidence_artifacts(summary, output_json, output_md)

    assert "PU-XMSAT Publication Evidence Consolidation" in output_md.read_text()
    assert '"experiment": "pu_xmsat_publication_evidence_consolidation"' in output_json.read_text()
