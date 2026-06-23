# MSAT Project Memory

Last inspected: 2026-06-23 16:50 CST
Latest external progress note: `resource_副本/MSAT_SESSION_PROGRESS_2026-06-23.md` (2026-06-23 11:45 CST)

## Purpose

This project reproduces the paper:

- Shi et al. (2026), "MSAT: a FAERS-informed heterogeneous graph neural network for pharmacovigilance prediction of Chinese materia medica-associated adverse drug reactions", Frontiers in Pharmacology 17:1774128.
- Local paper PDF: `resource_副本/fphar-17-1774128.pdf`.
- Local upstream code copy: `resource_副本/MSAT-main/`.
- Working implementation: `MSAT/`.

The reproduction goal is not just to run the upstream code, but to match the paper's experimental protocol and reported findings, using the paper, official split file, Zenodo graph data, and the local expanded scripts.

## Repository Shape

- `MSAT/model.py`: MSAT model implementation.
  - Multi-relation attention over heterogeneous graph node types.
  - ESA-style gated edge encoder for 6-dim CMM-ADR evidence features.
  - HSP-style propagation / bottleneck transform.
  - HCI-style late fusion prediction head: MLP + bilinear + DistMult.
- `MSAT/train.py`: 10-fold MSAT training/evaluation.
  - Uses official `10fold_cv_split.pkl`.
  - Removes held-out test positive CMM-ADR edges from graph in both directions.
  - Saves fold models and summary metrics.
- `MSAT/experiments/feature_extractor.py`: graph and split loader.
  - Loads `experiments_data_clean_final/complete_hetero_graph.pt`.
  - Supports 1:1, 1:10, and test-only imbalance negative sampling.
- `MSAT/baselines/`: ML/GNN baseline support.
- `MSAT/inference/`: cold-start, entity mapping, predictor, TCM mapping, graph path utilities.
- `MSAT/scripts/`: experiment runners for the paper tables/figures.
- `MSAT/results/`: current effective outputs and living reports.
- `MSAT/results/archive_pre_paper_align_2026-06-22/`: historical outputs before paper-protocol realignment; do not cite as final unless explicitly comparing history.
- `docs/superpowers/plans/`: phase plans, especially Phase 8 and Phase 9 gap-closure notes.

The workspace is now a git repository and has been pushed to GitHub:

- Remote: `git@github.com:67-rui/drug-side-effect-detection-reproduction.git`
- Public URL: `https://github.com/67-rui/drug-side-effect-detection-reproduction`
- Initial pushed commit: `ee5e617 Initial reproduction project snapshot`

## Paper Protocol Anchors

The paper uses:

- 27,062 CMM-ADR associations.
- Stratified 10-fold cross-validation.
- Approximate 81:9:10 train/validation/test split within each fold.
- Test positive CMM-ADR edges removed from the graph during training/evaluation to avoid topology leakage.
- Balanced 1:1 negative sampling for primary Table 2/3 evaluation.
- End-to-end 1:10 sampling for Table 4.
- Test imbalance sweep for Fig.6.
- FAERS-only training and literature hold-out evaluation for Fig.5a cold-start.
- Top-15 high-confidence unlabeled predictions for Table 5.
- TCM functional system mapping for Table 6.
- Case study: Zhishi / Citrus aurantium L. -> diarrhoea, with nobiletin (CID 72344) and ABCG2/BCRP path narrative.

## Data State

Important local files:

- `MSAT/data/10fold_cv_split.pkl`: official GitHub split.
- `experiments_data_clean_final/complete_hetero_graph.pt`: Zenodo graph data, required by tests/training.
- `MSAT/data/paper_table5_reference.json`: paper Table 5 reference evidence.
- `MSAT/data/paper_table6_reference.json`: paper Table 6 mapping reference.
- `MSAT/data/cctcm_herb_index.json` and `MSAT/data/entity_names.json`: entity display/mapping support.
- `MSAT/data/tcmda_cache.json`: local manual/seeded TCMDA-style evidence cache.

Graph scale recorded in the report:

- herb/CMM nodes: 651, 768-d features.
- compound nodes: 1,498, 768-d features.
- target nodes: 21,393, 768-d features.
- ADR nodes: 5,974, 768-d features.
- supervised CMM-ADR edges: 27,062, 6-d evidence features.

## Current Progress Snapshot

The full paper-aligned AutoDL resume completed on 2026-06-23 16:11 CST. Remote `results/` was synchronized back to local `MSAT/results/` at about 2026-06-23 16:50 CST.

Remote/local sync facts:

- Remote path: `/root/autodl-tmp/MSAT/results`.
- Local path: `MSAT/results/`.
- Synced result payload: 103 files, about 328 MB.
- Remote training processes had stopped and GPU was idle at the final check.

Final local snapshot after the remote sync:

Strongly reproduced / effectively complete:

- Table 2 MSAT main experiment: `summary.json` AUC 0.9792 +/- 0.0018, F1 0.9311, MCC 0.8616. This matches the paper's main MSAT AUC level.
- Table 3 w/o ablations: Full is best; w/o HCI has lowest AUC among w/o variants.
- Table 4 MSAT 1:10: `summary_neg10.json` AUC 0.8710 +/- 0.0051, F1 0.5639, MCC 0.5221, close to the paper's reported 1:10 MSAT level.
- Fig.5b degree stratification: tail/head trend aligns with paper.
- Fig.5a paper-aligned FAERS-only cold-start: `faers_only_coldstart_summary.json` shows MSAT beats GAT, HGT, and Simple-HGN on Precision, MCC, and AUC, with unseen herb rate 164/170 = 96.47%.
- Entity mapping sanity for paper seeds: recorded as 16/16 mapped.

Partially reproduced / still problematic:

- Table 3 Only variants: all below Full, but Only HCI is not the lowest as in the paper.
- Table 4 all-model ranking: GNN baselines are plausible and below MSAT, but ML baselines are invalid right now. LR/RF/XGB produce AUC approximately 1.0 under 1:10, which is a severe anomaly and likely indicates target-edge evidence leakage or pair-feature construction leakage. Do not cite ML baseline rows until fixed.
- Fig.6 imbalance sweep: MSAT is best only at test negative ratio 10. HGT is slightly higher than MSAT at ratios 2 and 5, so the current Fig.6 result does not fully match the paper trend.
- Table 5 Top-15: unresolved. Current files and report have version drift:
  - Current root `table5_summary.json` is `paper_3.5.6_global_top15` / `exclude_all_graph_positives` with support 1/15.
  - `archive_pre_paper_align_2026-06-22/table5_paper_compare.json` has paper-herb Top-1 support 12/15 but ADR text matches paper 0/15.
  - External database validation is incomplete because TCMDA has no public API in this workflow.
- Table 6 TCM mapping: columns are generated, but mapping is still coarse and often defaults to `Qi-Blood-Fluid`; fine-grained paper mappings are not fully reproduced.
- Zhishi case study:
  - Current `case_zhishi_diarrhoea.json` still maps herb_id 277 and label includes 枳实 / Citrus aurantium L., with nobiletin CID 72344 paths.
  - The final synced score is weaker than the earlier local run: score 0.2549, rank 7/5974. This may be caused by later Fig.6/test-negative runs overwriting `saved_models/best_model_for_prediction.pt`; verify checkpoint provenance before citing the case score.

See `MSAT/results/FINAL_REMOTE_RUN_SUMMARY_2026-06-23.md` for the concise final synced result table and next actions.

## Fixes Started After Final Sync

These code fixes were made locally after synchronizing the remote result files. The old JSON metrics in `MSAT/results/` have not yet been regenerated after these fixes.

- ML baseline leakage fixed in code:
  - `baselines.common.pair_features()` now excludes CMM-ADR edge evidence by default.
  - `baselines.ml_models.run_ml_cv()` records `include_cmm_adr_edge_attr: false` in future ML baseline outputs.
  - Diagnostic before the fix showed fold 0 1:10 `has_edge_attr == label` accuracy was 1.0 for both train and test, explaining LR/RF/XGB AUC near 1.0.
- Prediction checkpoint overwrite fixed in code:
  - Main run still writes `saved_models/best_model_for_prediction.pt`.
  - Tagged runs now write `saved_models/best_model_for_prediction_<tag>.pt`.
  - Future Fig.6, ablation, and other tagged runs should no longer overwrite the main predictor checkpoint used by Table 5 and the Zhishi case.
- Future MSAT/GNN summaries now include clearer protocol metadata:
  - MSAT summaries include `test_neg_ratio`.
  - GNN baseline summaries include data/model/training config fields.
- Regression tests added:
  - `tests/test_baseline_leakage.py`
  - `tests/test_checkpoint_paths.py`

Verification after these code changes:

- `/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q`: 7 passed.
- `/Users/a67_2024/opt/anaconda3/bin/python -m py_compile baselines/common.py baselines/ml_models.py baselines/gnn_models.py train.py scripts/run_imbalance_sweep.py`: passed.
- A local one-fold LR numerical rerun was attempted but interrupted after more than 2.5 minutes on CPU; rerun corrected ML baselines on the GPU server instead.

## Current Reports To Trust

Use these together; none is fully sufficient alone:

- `resource_副本/MSAT_SESSION_PROGRESS_2026-06-23.md`: latest Cursor/remote-run progress note; authoritative for current AutoDL running state.
- `MSAT/results/REPRODUCTION_REPORT.md`: broad narrative and paper table overview.
- `MSAT/results/VERIFICATION_FINDINGS.md`: better for latest gap analysis around Fig.5a, Table 5, and Table 4.
- `MSAT/results/PAPER_CODE_AUDIT.md`: protocol/code alignment audit.
- `MSAT/results/faers_only_coldstart_summary.json`: authoritative current Fig.5a FAERS-only result.
- `MSAT/results/case_zhishi_diarrhoea.json`: authoritative current Zhishi case output.
- `MSAT/results/table5_summary.json`, `table5_top15.csv`, `table6_mapping.csv`: current root outputs, but verify protocol and timestamps before citing.

## Known Version Drift

There is a mismatch between some report prose and current root result files:

- `REPRODUCTION_REPORT.md` still contains older statements about the Zhishi case and Table 5 support. Current final synced files are authoritative until the report is regenerated.
- Current `case_zhishi_diarrhoea.json` says score 0.2549/rank 7 and label includes 枳实.
- Current root `table5_summary.json` records 1/15 support under `exclude_all_graph_positives`.
- `table6_mapping.csv` appears generated from a different Table 5 input than current `table5_top15.csv`.

Before publishing any final claim, regenerate Table 5 -> Table 6 in one controlled run and update the report.

## Verification

Attempted local tests:

- `python3 -m pytest MSAT/tests -q`: failed because default Python has no pytest.
- Bundled Codex Python also has no pytest.

No code-level pytest result is available from this inspection. Existing result files indicate prior GPU/server runs succeeded.

## Recommended Next Steps

1. Push the leakage/checkpoint fixes to the server and rerun corrected ML baselines.
   - Priority command target: 1:10 `lr`, `rf`, `xgb`, then regenerate `baseline_neg10_summary.json`.
   - Do not cite old `baseline_lr_neg10.json`, `baseline_rf_neg10.json`, or `baseline_xgb_neg10.json`.
2. Restore or regenerate a clean main-run predictor checkpoint.
   - Re-run the main Table 2 MSAT training or copy the intended main checkpoint to `saved_models/best_model_for_prediction.pt`.
   - Then regenerate Table 5 and the Zhishi case.
3. Normalize Table 5 protocol and rerun Table 5 -> Table 6 in one pass.
   - Decide whether the final paper-aligned claim uses exclude-all-positives, FAERS-only exclusion, predictor mode, or paper-herb diagnostic mode.
   - Write the chosen protocol explicitly into result filenames or metadata.
4. Re-run Fig.6 only after the checkpoint and metadata fixes are deployed.
   - Current Fig.6 mismatch may be a real model/protocol result, but the regenerated summaries will be easier to audit.
5. Improve Table 5 evidence validation.
   - TCMDA has no public API path here; use explicit manual cache entries or approved external evidence sources only.
   - Avoid claiming paper's 13/15 unless the same evidence definition is implemented.
6. Fix Table 6 mapping.
   - Prefer `paper_table6_reference.json` for paper-comparison rows.
   - Expand PT/SOC rules for Stomach, Kidney, Liver, etc.
7. Finish Zhishi readability.
   - Map target IDs in the nobiletin paths to ABCG2/BCRP where supported.
   - Ensure report text is updated to current rank/score.
8. Reconcile report drift.
   - Update `REPRODUCTION_REPORT.md` sections 10.7, 10.8, 12, and 13 after remote results are pulled back.
