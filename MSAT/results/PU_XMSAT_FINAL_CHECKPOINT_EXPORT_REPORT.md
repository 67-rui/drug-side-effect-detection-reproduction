# PU-XMSAT Final Checkpoint Export Report

**Date:** 2026-06-29

## Status

- Final full-positive hybrid PU-XMSAT checkpoint export: **completed on the remote GPU server**.
- Training command: formal `full_msat_pu` backend, `hybrid` sampling, seed `2026`, 10 folds, 200 max epochs, 66,015 pair budget, `val_f1` threshold strategy, `unlabeled_weight=0.2`, `reliable_negative_weight=0.8`.
- Output JSON synced locally: `results/pu_xmsat_final_hybrid_seed2026_checkpoint_export.json`.
- Pipeline manifest synced locally: `results/final_pu_xmsat_pipeline_manifest.json`.
- Baseline checkpoint safety: no MSAT baseline checkpoint was overwritten. Formal PU checkpoints were written under the separate remote directory `saved_models/pu_xmsat_formal/`.

## Training Result Summary

- Fold count: 10.
- Checkpoint count: 10 `.pt` checkpoints plus 10 metadata sidecars.
- Mean AUC: 0.980281.
- Mean AUPRC: 0.977907.
- Mean F1: 0.934326.
- Mean MCC: 0.867061.
- Mean final loss: 0.100011.

## Code Readiness

The `full_msat_pu` backend now supports safe best-validation checkpoint export when `--save-checkpoints` is supplied.

Checkpoint filenames use a formal non-baseline prefix:

`pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold{fold}.pt`

Metadata sidecars are written next to each checkpoint:

`pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold{fold}.metadata.json`

The metadata records backend, sampling strategy, seed, fold, pair budget, threshold strategy, PU sample weights, best validation epoch/AUC, checkpoint path, metadata path, and protocol version.

## Executed Full Pipeline Command

The formal run was executed through:

```bash
PYTHONPATH=. python scripts/run_final_pu_xmsat_interpretability_pipeline.py \
  --python /root/miniconda3/bin/python \
  --manifest results/final_pu_xmsat_pipeline_manifest.json
```

The pipeline refuses nonfinal fold/epoch/pair/top-K settings by default. It runs training first, then regenerates top predictions, contribution quantification, batch interpretability, aggregate summary, mechanism explanation layer, and Direction 3 evidence queue.

## Equivalent Training Command

Run this from `MSAT/` after the project and data are available on the server:

```bash
PYTHONPATH=. python experiments/run_pu_msat_experiment.py \
  --backend full_msat_pu \
  --sampling-strategy hybrid \
  --seed 2026 \
  --max-folds 10 \
  --max-epochs 200 \
  --max-pairs 66015 \
  --threshold-strategy val_f1 \
  --unlabeled-weight 0.2 \
  --reliable-negative-weight 0.8 \
  --candidate-cache results/pu_candidate_scores.random50k.jsonl \
  --save-checkpoints \
  --checkpoint-dir saved_models/pu_xmsat_formal \
  --checkpoint-prefix pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8 \
  --output results/pu_xmsat_final_hybrid_seed2026_checkpoint_export.json
```

This is the training step executed by the pipeline.

## Post-Training Interpretation Outputs

- Top prediction export: `results/pu_xmsat_top_predictions.json/.csv` and `results/PU_XMSAT_TOP_PREDICTIONS_EXPORT.md`.
- Contribution quantification: `results/contribution_quantification.json/.csv` and `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`.
- Batch mechanism interpretability: `results/batch_mechanism_interpretability.json/.csv` and `results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY.md`.
- Aggregate summary: `results/contribution_aggregate_summary.json/.csv` and `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`.
- Direction 3 review queue: `results/direction3_targeted_review_queue.json/.csv` and `results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md`.

Top-50 PU prediction export selected 50 unobserved CMM-ADR candidates from the formal checkpoint, but only 1 of the top-50 had parseable explicit mechanism paths. Therefore, the final-checkpoint-aware mechanism quantification covers 1 case, not 20 or 50 cases.

## Claim Boundary

The explanation layer is now checkpoint-aware and uses the formal PU-XMSAT checkpoint, but the top-50 mechanism-path coverage is sparse. Manuscript wording can claim a final-checkpoint-aware top-ranking mechanism screen, but it cannot claim broad systematic mechanism coverage across 20-50 cases. The only quantified final-checkpoint case shows near-zero perturbation sensitivity and remains Grade C / boundary-only evidence, not strong external validation.
