# PU-XMSAT Interpretability Gap Audit

**Date:** 2026-06-29

## Summary

- Current explanation checkpoint: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Current explanation checkpoint SHA256: `26d65adad1ffe275b938aa89326c113e4bb70b5770f35df5e40ce7a145484e19`
- Equals final full-positive hybrid PU-XMSAT checkpoint: no.
- Reason: current full-positive hybrid PU-XMSAT result exports record `checkpoint_path: null`; no formal final PU predictor checkpoint is present under `MSAT/saved_models/`.
- Current explanation candidates: transitional mechanism-supported artifacts, not final PU-XMSAT top-ranking export.

## Checkpoint Saving Capability

The `full_msat_pu` backend already saves best fold states when `save_checkpoints=True`. This pass exposed checkpoint export through `MSAT/experiments/run_pu_msat_experiment.py` with:

- `--save-checkpoints`
- `--checkpoint-dir`
- `--checkpoint-prefix`

When no prefix is supplied, the formal prefix includes backend, sampling strategy, seed, pair budget, threshold strategy, unlabeled weight, and reliable-negative weight. The backend appends the fold index in the filename, so a formal export can avoid overwriting the reproduced MSAT baseline checkpoint.

Expected next formal prefix for the strongest current setting:

`full_msat_pu_strategy-hybrid_seed-1337_pairs-66015_threshold-val_f1_uw-0p2_rnw-0p8_best_model_fold{fold}.pt`

## Paper Wording If No Final PU Checkpoint Is Used

The manuscript should state that the current mechanism analysis is a checkpoint-aware fallback: it uses the local predictor checkpoint and existing perturbation rows for mechanism-supported candidates. It should not be described as final full-positive hybrid PU-XMSAT attribution.

Safe wording:

> Mechanism interpretation was run as a local perturbation-sensitivity workflow using the available predictor checkpoint and transitional mechanism-supported candidate artifacts. Because an explicit final full-positive hybrid PU-XMSAT predictor checkpoint was not exported for this analysis, the attribution is used for mechanism triage and evidence screening rather than final PU-XMSAT checkpoint attribution.

## Next Checkpoint To Use

For final PU-XMSAT attribution, export the full-positive hybrid checkpoint with:

- backend: `full_msat_pu`
- strategy: `hybrid`
- seed: `1337` or the manuscript-selected seed
- fold: explicit fold index in the filename
- pair budget: `66015`
- threshold strategy: `val_f1`
- PU weights: `unlabeled_weight=0.2`, `reliable_negative_weight=0.8`

Then rerun batch mechanism interpretability with `--checkpoint` and `--checkpoint-is-final-pu` only after confirming the exported checkpoint can be loaded for prediction.

## Current Claim Boundary

The current batch report selected 2 parseable explicit-path candidates from transitional artifacts and perturbation-quantified both cases using already-computed contribution rows. It supports component/target/pathway triage, not SHAP attribution, causal interpretation, clinical validation, or external evidence upgrading. Grade C remains a screening grade, not strong external evidence.
