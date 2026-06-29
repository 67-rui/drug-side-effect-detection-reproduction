# PU-XMSAT Package B/C Final Summary

**Date:** 2026-06-29

## Package C: Final Checkpoint Mechanism Interpretability

- Final top prediction export: `results/pu_xmsat_top_predictions_top5000.json`
- Contribution quantification with random controls: `results/contribution_quantification_top5000_random_controls.json`
- Batch interpretability report: `results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint is final PU-XMSAT: yes
- Candidate source: final PU-XMSAT top-ranking export, top 5000 unobserved CMM-ADR predictions

## Mechanism Coverage

| Top K | Candidates checked | Explicit-path candidates | Coverage rate |
| ---: | ---: | ---: | ---: |
| 50 | 50 | 1 | 0.020000 |
| 100 | 100 | 8 | 0.080000 |
| 500 | 500 | 31 | 0.062000 |
| 1000 | 1000 | 64 | 0.064000 |
| 5000 | 5000 | 391 | 0.078200 |

Mechanism-supported top-K actually selected for perturbation: 20 cases. All 20 selected cases had explicit mechanism paths. The complete top-5000 pool was available locally after synchronization, with `candidate_pool_missing_count=0`.

## Perturbation Sensitivity

- Quantified case count: 20
- Near-zero sensitivity cases: 12
- Negative score_drop cases: 0
- Random perturbation controls available: yes

| Control group | Count | Mean score_drop | Max score_drop |
| --- | ---: | ---: | ---: |
| component | 100 | 0.000000013112 | 0.000000476800 |
| target | 100 | 0.000000010729 | 0.000001072900 |
| pathway | 86 | 0.000000406142 | 0.000029921500 |

Interpretation: the final checkpoint now supports batch-level mechanism triage rather than a two-case demo, but perturbation sensitivity is still small for most cases. This should be written as local model-sensitivity evidence for ranking and mechanism inspection, not as strong causal or external biological validation.

## Package B: Cluster-Held-Out Generalization

- Result JSON: `results/pu_xmsat_cluster_holdout_hybrid_seed2026_10cluster_200e_66015p_valf1.json`
- Markdown summary: `results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`
- Run completed: full 10-cluster/fold run
- Runtime: 871.6329 seconds
- Backend: `full_msat_pu`
- Split mode: `cluster_holdout`
- Cluster feature: `herb_x`
- Sampling strategy: `hybrid`
- Seed: 2026
- Max epochs: 200
- Max pairs: 66015
- Threshold strategy: `val_f1`

## Cluster-Held-Out Mean Metrics

| Metric | Mean |
| --- | ---: |
| AUC | 0.889069 |
| AUPRC | 0.903219 |
| F1 | 0.176976 |
| MCC | 0.191914 |

Interpretation caveats: heldout herb counts range from 1 to 207, and 3 heldout clusters contain fewer than 5 herbs. The low F1/MCC indicates that cluster-held-out evaluation is a much harder new-CMM/herb-cluster stress test, not evidence of equivalent deployment performance under unseen herb groups.

## Cluster-Held-Out Fold Summary

| Fold | Holdout cluster | Heldout herbs | Test positives | AUC | AUPRC | F1 | MCC |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 207 | 14977 | 0.808161 | 0.830212 | 0.098053 | 0.157502 |
| 1 | 1 | 1 | 9 | 0.987654 | 0.988889 | 0.500000 | 0.447214 |
| 2 | 2 | 1 | 5 | 1.000000 | 1.000000 | 0.750000 | 0.654654 |
| 3 | 3 | 1 | 5 | 1.000000 | 1.000000 | 0.000000 | 0.000000 |
| 4 | 4 | 20 | 213 | 0.891490 | 0.911725 | 0.000000 | 0.000000 |
| 5 | 5 | 65 | 107 | 0.882435 | 0.901068 | 0.170940 | 0.221404 |
| 6 | 6 | 33 | 937 | 0.850245 | 0.871114 | 0.041797 | 0.103863 |
| 7 | 7 | 71 | 3294 | 0.862943 | 0.875762 | 0.184920 | 0.227787 |
| 8 | 8 | 112 | 4186 | 0.808398 | 0.830461 | 0.006192 | 0.039436 |
| 9 | 9 | 140 | 3329 | 0.799364 | 0.822962 | 0.017862 | 0.067277 |

## Leakage Controls

- Heldout herbs are excluded from PU training positives, reliable negatives, and unlabeled arrays through `allowed_train_herbs`.
- Validation/test positive CMM-ADR edges are removed from the message-passing graph for evaluation.
- Mechanism edges are retained because the protocol tests structural generalization to held-out herb/CMM clusters, not blind removal of all biological annotations.

## Claim Boundary

Package B supports a structure-generalization or new-CMM/herb-cluster generalization statement under the PU-XMSAT protocol. Package C supports checkpoint-aware, batch-level, evidence-linked mechanism triage. Neither package supports SHAP claims, causal effects, clinical validation, causal transportability, or automatic Grade A/B evidence upgrading. Negative score_drop must not be interpreted as a protective mechanism.
