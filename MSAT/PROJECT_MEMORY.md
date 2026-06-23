# MSAT Project Memory

Last inspected: 2026-06-23
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

The repository root is not a git repo, and `MSAT/` is not a git repo either in this workspace.

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

The local `MSAT/results/` root currently contains outputs timestamped up to 2026-06-22 23:46, but Cursor's latest session note reports a newer AutoDL run that has not been fully pulled back locally. Treat `resource_副本/MSAT_SESSION_PROGRESS_2026-06-23.md` as the current progress source until the remote artifacts are synchronized.

Remote AutoDL state from the Cursor note:

- Full paper-aligned retrain started 2026-06-22 22:12 via `scripts/server_paper_retrain.sh`.
- User paused the remote run at 2026-06-23 00:58; `scripts/server_paper_retrain_resume.sh` was uploaded.
- Resume started 2026-06-23 10:34.
- At 2026-06-23 11:45, the resume was still running at `run_baselines.py --neg-ratio 10 --model hgt`, fold 5/10.
- Remote path: `/root/autodl-tmp/MSAT`.
- Resume log: `results/phase8_logs/paper_retrain_resume.log`.

New paper-aligned remote results already reported by Cursor:

- New-protocol Table 2 MSAT 10-fold: `summary.json` AUC about 0.9792.
- New-protocol Table 4 MSAT 1:10: `summary_neg10.json` AUC about 0.871.
- Table 2 ML and GNN baselines are complete on remote.
- Table 3 ablation is complete on remote.
- Table 4 1:10 baselines are partially complete: lr/rf/xgb/gcn/gat/rgcn done; hgt running; hetnn and simple_hgn pending as of 11:45.
- Fig.6 sweep and Phase 9 are still pending after the 1:10 baseline queue.
- Fig.5a FAERS-only result should be kept; Phase 9 will skip FAERS-only because `faers_only_coldstart_summary.json` is already valid.

Local snapshot before/around the remote sync:

Strongly reproduced / effectively complete:

- Table 2 MSAT main experiment: previous local archive AUC about 0.9797 +/- 0.0014; newer remote paper-aligned rerun reported AUC about 0.9792, matching paper about 0.979.
- Table 3 w/o ablations: Full is best; w/o HCI has lowest AUC among w/o variants.
- Table 4 MSAT 1:10: previous local archive AUC about 0.8717 +/- 0.0042; newer remote paper-aligned rerun reported AUC about 0.871, close to paper about 0.875 +/- 0.005.
- Fig.6 imbalance sweep: MSAT highest under tested ratios.
- Fig.5b degree stratification: tail/head trend aligns with paper.
- Fig.5a paper-aligned FAERS-only cold-start: `faers_only_coldstart_summary.json` shows MSAT beats GAT, HGT, and Simple-HGN on Precision, MCC, and AUC, with unseen herb rate 164/170 = 96.47%.
- Entity mapping sanity for paper seeds: recorded as 16/16 mapped.

Partially reproduced / still problematic:

- Table 3 Only variants: all below Full, but Only HCI is not the lowest as in the paper.
- Table 4 all-model ranking: do not finalize until remote resume completes hgt/hetnn/simple_hgn and aggregates all 1:10 baselines. Previous local archive had XGB AUC 0.8768 slightly higher than MSAT 0.8717, but that was before the current remote resume finished.
- Table 5 Top-15: unresolved. Current files and report have version drift:
  - Report section 10.7 mentions OOF + FAERS-only support 7/15 and paper-herb Top-1 support 12/15.
  - Current root `table5_summary.json` is `exclude_all_graph_positives` with support 1/15.
  - `archive_pre_paper_align_2026-06-22/table5_paper_compare.json` has paper-herb Top-1 support 12/15 but ADR text matches paper 0/15.
  - External database validation is incomplete because TCMDA has no public API in this workflow.
- Table 6 TCM mapping: columns are generated, but mapping is still coarse and often defaults to `Qi-Blood-Fluid`; fine-grained paper mappings are not fully reproduced.
- Zhishi case study:
  - Current `case_zhishi_diarrhoea.json` is much improved: herb_id 277, label includes 枳实 / Citrus aurantium L., score 0.9628, rank 1, and nobiletin CID 72344 appears.
  - Target names are still mostly numeric IDs; ABCG2/BCRP is recorded in `paper_targets` but not fully resolved in every displayed path.

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

- `REPRODUCTION_REPORT.md` still contains older statements that the Zhishi case had score 0.430/rank 4/display-name issues, but current `case_zhishi_diarrhoea.json` says score 0.9628/rank 1 and label includes 枳实.
- Report Table 5 prose mentions 7/15 support under OOF + FAERS-only, but current root `table5_summary.json` records 1/15 under `exclude_all_graph_positives`.
- `table6_mapping.csv` appears generated from a different Table 5 input than current `table5_top15.csv`.

Before publishing any final claim, regenerate Table 5 -> Table 6 in one controlled run and update the report.

## Verification

Attempted local tests:

- `python3 -m pytest MSAT/tests -q`: failed because default Python has no pytest.
- Bundled Codex Python also has no pytest.

No code-level pytest result is available from this inspection. Existing result files indicate prior GPU/server runs succeeded.

## Recommended Next Steps

1. Wait for / check remote resume completion.
   - Do not restart `server_paper_retrain.sh`; use `server_paper_retrain_resume.sh` only if stopped.
   - Expected remaining order from Cursor note: hgt -> hetnn -> simple_hgn -> Fig.6 -> Phase 9.
2. Pull back/synchronize new remote artifacts.
   - Especially new `summary.json`, all `baseline_*.json`, `baseline_summary.json`, `baseline_neg10_summary.json`, `fig6_summary.json`, Phase 9 outputs, and remote logs.
3. Normalize Table 5 protocol and rerun Table 5 -> Table 6 in one pass if Phase 9 outputs still show drift.
   - Decide whether the final paper-aligned claim uses exclude-all-positives, FAERS-only exclusion, predictor mode, or paper-herb diagnostic mode.
   - Write the chosen protocol explicitly into result filenames or metadata.
4. Improve Table 5 evidence validation.
   - TCMDA has no public API path here; use explicit manual cache entries or approved external evidence sources only.
   - Avoid claiming paper's 13/15 unless the same evidence definition is implemented.
5. Fix Table 6 mapping.
   - Prefer `paper_table6_reference.json` for paper-comparison rows.
   - Expand PT/SOC rules for Stomach, Kidney, Liver, etc.
6. Finish Zhishi readability.
   - Map target IDs in the nobiletin paths to ABCG2/BCRP where supported.
   - Ensure report text is updated to current rank/score.
7. Reconcile report drift.
   - Update `REPRODUCTION_REPORT.md` sections 10.7, 10.8, 12, and 13 after remote results are pulled back.
8. Install/test environment if code changes continue.
   - Need pytest and project dependencies; current local Python lacks pytest.
