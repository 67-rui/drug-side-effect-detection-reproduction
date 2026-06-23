# Final Remote Run Summary - 2026-06-23

This summary records the AutoDL paper-aligned run that completed on 2026-06-23 16:11 CST and was synchronized to local `MSAT/results/` at about 16:50 CST.

## Sync Status

- Remote source: `/root/autodl-tmp/MSAT/results`
- Local destination: `MSAT/results/`
- Synced payload: 103 files, about 328 MB
- Remote status at final check: no training process, GPU idle

## Main Results

| Target | Local file | Status | Key result |
| --- | --- | --- | --- |
| Table 2 MSAT main 10-fold | `summary.json` | reproduced | AUC 0.9792 +/- 0.0018; F1 0.9311; MCC 0.8616 |
| Table 4 MSAT 1:10 | `summary_neg10.json` | close | AUC 0.8710 +/- 0.0051; F1 0.5639; MCC 0.5221 |
| Fig.5a FAERS-only cold-start | `faers_only_coldstart_summary.json` | reproduced | MSAT beats GAT/HGT/Simple-HGN; MSAT AUC 0.9281; unseen CMM 96.47% |
| Fig.6 test imbalance | `fig6_summary.json` | partial mismatch | MSAT wins ratio 10 only; HGT is higher at ratios 2 and 5 |
| Table 5 top predictions | `table5_summary.json` | not reproduced | support 1/15 under `exclude_all_graph_positives` |
| Table 6 mapping | `table6_mapping.csv` | generated, weak | mapping exists but is coarse and downstream of weak Table 5 |
| Zhishi case | `case_zhishi_diarrhoea.json` | mapped, score weak | herb maps to 枳实 / Citrus aurantium L.; score 0.2549; rank 7/5974 |

## Critical Issues

1. The synced 1:10 ML baseline JSON files are invalid until rerun. `baseline_neg10_summary.json` reports LR/RF/XGB AUC approximately 1.0; the code-level leakage source has been fixed, but the old result files still reflect the pre-fix run.

2. Fig.6 is not fully aligned with the paper. In the synced run, HGT has slightly higher AUC than MSAT at negative ratios 2 and 5; MSAT is only first at ratio 10.

3. Table 5/6 should not be presented as reproduced. Current top-15 support is 1/15, far from the paper claim, and the external TCMDA evidence path is not equivalent to the paper's validation.

4. The Zhishi case should be checkpoint-audited before citation. The final synced score is weaker than an earlier local run, and later imbalance experiments may have overwritten `saved_models/best_model_for_prediction.pt`.

## Local Fixes Applied After This Sync

These fixes are in local code, but the result JSON files above still reflect the pre-fix remote run until experiments are rerun.

- ML baseline leakage fix: classical ML pair features now exclude CMM-ADR `edge_attr` by default. Before the fix, fold 0 1:10 diagnostics showed edge-attribute presence separated labels with accuracy 1.0.
- Checkpoint isolation fix: tagged MSAT runs now save to `saved_models/best_model_for_prediction_<tag>.pt`, while the main run keeps `saved_models/best_model_for_prediction.pt`.
- Metadata fix: future MSAT summaries include `test_neg_ratio`; future GNN baseline JSON files include data/model/training config.
- Artifact provenance fix: future Table 5, Table 6, Zhishi case, prediction, and Phase 7 outputs can use explicit checkpoints and record file manifests.
- Stale marking: current final-sync Table 5, Table 6, and Zhishi JSON files are marked stale until regenerated with explicit checkpoint provenance.
- Server rerun helper: `scripts/rerun_after_artifact_fix.sh`.
- Regression tests added for pair-feature leakage and checkpoint paths.

Verification:

- `/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q`: 9 passed.
- `/Users/a67_2024/opt/anaconda3/bin/python -m py_compile inference/artifact_manifest.py scripts/run_table5_validation.py scripts/run_case_zhishi.py scripts/predict.py scripts/run_phase7.py scripts/run_table6_mapping.py`: passed.

## Recommended Next Steps

1. When the server is available, pull latest code and run `scripts/rerun_after_artifact_fix.sh`.
   - This refreshes corrected 1:10 ML baselines and regenerates Table 5, Table 6, and the Zhishi case with provenance.

2. Run `scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json` after every result sync.
   - Do not cite outputs with `stale_artifact`, `missing_provenance`, or `suspicious_ml_auc`.

3. Re-run Fig.6 after checkpoint isolation and metadata fixes are deployed.
   - Compare HGT/MSAT settings, threshold handling, and whether the same train/test split and test-negative sampling are used.

4. Follow `TABLE5_PROTOCOL_DECISION.md` for Table 5.
   - If no faithful TCMDA validation source is available, report Table 5 as a reproduction gap rather than claiming the paper's 13/15.

5. Regenerate `REPRODUCTION_REPORT.md` after corrected remote artifacts are synced back.
