# PU-XMSAT Interpretability Gap Audit

**Date:** 2026-06-29

## Summary

- Current final explanation checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`.
- Equals final full-positive hybrid PU-XMSAT checkpoint: yes for the regenerated top-prediction, contribution, batch, aggregate, and Direction 3 artifacts.
- Formal checkpoint export status: completed on the remote GPU server with 10 folds and 10 metadata sidecars; structured training output is `results/pu_xmsat_final_hybrid_seed2026_checkpoint_export.json`.
- Current final explanation candidates: final PU-XMSAT top-5000 unobserved CMM-ADR predictions from `results/pu_xmsat_top_predictions_top5000.json`.
- Mechanism path coverage in the synchronized final top-5000 export: 1/50, 8/100, 31/500, 64/1000, and 391/5000 candidates have parseable explicit mechanism paths.
- Current synchronized batch artifact selected and perturbation-quantified 20 mechanism-supported cases from the complete top-5000 candidate pool (`candidate_pool_missing_count=0`, `candidate_pool_is_complete=true`).
- Random perturbation controls are available in `results/contribution_quantification_top5000_random_controls.json` and summarized in `results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`.
- Legacy local checkpoint context: older fallback reports used `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`; those legacy numbers should no longer be used as the primary manuscript interpretation result.

## Checkpoint Saving Capability

The `full_msat_pu` backend already saves best fold states when `save_checkpoints=True`. This pass exposed checkpoint export through `MSAT/experiments/run_pu_msat_experiment.py` with:

- `--save-checkpoints`
- `--checkpoint-dir`
- `--checkpoint-prefix`

When no prefix is supplied, the formal prefix includes backend, sampling strategy, seed, pair budget, threshold strategy, unlabeled weight, and reliable-negative weight. The backend appends the fold index in the filename, so a formal export can avoid overwriting the reproduced MSAT baseline checkpoint.

Expected next formal prefix for the selected formal setting:

`pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold{fold}.pt`

Each checkpoint should have a metadata sidecar:

`pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold{fold}.metadata.json`

## Paper Wording If No Final PU Checkpoint Is Used

This section now applies only to legacy fallback artifacts. The regenerated artifacts are final-checkpoint-aware. If older fallback numbers are mentioned historically, they should be described as local predictor checkpoint sensitivity and not mixed with the formal PU-XMSAT attribution.

Safe wording for the current final-checkpoint artifacts:

> Mechanism interpretation was regenerated from the formal full-positive hybrid PU-XMSAT checkpoint and the complete top-5000 final prediction export. Explicit-path coverage was sparse but measured systematically: 391/5000 top-ranked candidates had parseable mechanism paths, and 20 mechanism-supported candidates were subjected to compound-, target-, and path-level perturbation scoring with random controls. The analysis is best interpreted as checkpoint-aware batch-level mechanism triage rather than SHAP attribution, causal effect estimation, external validation, or broad mechanistic confirmation.

## Next Checkpoint To Use

For final PU-XMSAT attribution, export the full-positive hybrid checkpoint with:

- backend: `full_msat_pu`
- strategy: `hybrid`
- seed: `2026` for the next formal export, unless the manuscript team selects a different seed or requires both seed 2026 and seed 1337 exports
- fold: explicit fold index in the filename
- pair budget: `66015`
- threshold strategy: `val_f1`
- PU weights: `unlabeled_weight=0.2`, `reliable_negative_weight=0.8`

This export has now been completed for seed 2026. The next checkpoint-level extensions, if needed, are:

- rerun top prediction/interpretability from additional folds or an ensemble scoring policy;
- optionally improve compound/target display-name mapping for currently unmapped graph ids;
- consider explicit-path-prioritized ranking as an additional triage analysis while preserving final checkpoint context;
- run a more balanced or repeated-seed cluster-held-out generalization follow-up if the manuscript needs stronger new-cluster evidence beyond the completed 10-cluster stress test.

## Current Claim Boundary

The synchronized final-checkpoint batch report selected 20 parseable explicit-path candidates from the complete top-5000 final PU-XMSAT prediction pool and perturbation-quantified all 20 cases. Sensitivity remains limited: 12/20 cases are near-zero sensitivity and 0/20 have negative score_drop at the case level. The analysis supports checkpoint-aware component/target/pathway triage with random-control context, not SHAP attribution, causal interpretation, clinical validation, or external evidence upgrading. Perturbation magnitude must not upgrade evidence grades; Grade C remains a literature/manual-review status, and Grade A/B requires manually verified direct external evidence.
