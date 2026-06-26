# PU-XMSAT Full MSAT Pilot Report

**Date:** 2026-06-26  
**Server:** AutoDL RTX 5090 32GB  
**Backend:** `full_msat_pu`  
**Fold:** 0  
**Sampling strategy:** hybrid, low_score, random  
**Weights:** positive `1.0`, reliable negative `0.8`, unlabeled `0.2`  
**Protocol guardrail:** baseline verifier passed before each run.

## Pilot Results

| Run | PU pairs | Epochs | Best epoch | Best val AUC | Test AUC | Test AUPRC | Test F1 | Test MCC | Final loss | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fold0_50e_384p` | 384 | 50 | 50 | 0.8536 | 0.8497 | 0.8402 | 0.6605 | 0.1234 | 0.0000647 | 27.7s |
| `fold0_100e_768p` | 768 | 100 | 100 | 0.8693 | 0.8643 | 0.8511 | 0.6543 | 0.0441 | 0.0000259 | 52.3s |
| `fold0_200e_1536p` | 1536 | 200 | 200 | 0.8878 | 0.8855 | 0.8745 | 0.6551 | 0.0607 | 0.0000184 | 101.9s |

## Threshold-Calibrated Strategy Comparison

After the fixed-threshold pilots, the PU runner was extended with explicit validation-threshold calibration. The following fold0 comparison uses the same budget for all strategies: 200 epochs, 1,536 PU pairs, reliable negative weight 0.8, unlabeled weight 0.2, and threshold selection by validation F1.

| Sampling strategy | Test AUC | Test AUPRC | Test F1 | Test MCC | Selected threshold | Val F1 at threshold | Best epoch | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 0.8832 | 0.8706 | 0.6585 | 0.1037 | 0.9900 | 0.6710 | 197 | 99.7s |
| low_score | 0.8313 | 0.8079 | 0.7532 | 0.4665 | 0.9900 | 0.7610 | 7 | 52.9s |
| random | 0.9167 | 0.9175 | 0.6627 | 0.1417 | 0.9900 | 0.6748 | 200 | 101.1s |

## Interpretation

The full MSAT PU backend is now operational on GPU. AUC and AUPRC improve as epochs and PU pair count increase, and the best validation AUC occurs at the final epoch for all three runs. This suggests the pilot has not yet reached a clear plateau.

Threshold-dependent metrics need care. Recall is nearly 1.0 at the fixed `0.5` threshold, while precision and MCC remain weak. Validation-threshold calibration improves interpretability of F1/MCC, but all three calibrated runs selected the upper grid boundary (`0.99`), which indicates that probability calibration is still poor and thresholded metrics should be reported as secondary.

The negative-sampling comparison is not yet conclusive. `random` gives the strongest ranking metrics on fold0, while `low_score` gives much stronger thresholded F1/MCC but weaker AUC/AUPRC and reaches its best validation AUC very early. This suggests that `low_score` may produce easier negatives, whereas `random` may better preserve ranking difficulty under the current pilot budget. `hybrid` did not dominate this fold0 comparison and needs either revised scoring weights or multi-fold evidence before being used as the default claim.

## Recommendation

Do not start a full formal 10-fold claim yet. First run a bounded multi-fold pilot for at least `random` and `low_score` under the same budget, because fold0 currently points to different winners depending on whether the paper prioritizes ranking metrics or thresholded classification metrics. If the pattern is stable across folds, the next paper-facing experiment should report PU-XMSAT with AUC/AUPRC as primary metrics and F1/MCC as threshold-calibrated secondary metrics.

## Raw Artifacts

The raw JSON summaries are available locally and on the server but are ignored by git to avoid result-artifact pollution:

- `results/pu_training_summary_fold0_50e_384p.json`
- `results/pu_training_summary_fold0_100e_768p.json`
- `results/pu_training_summary_fold0_200e_1536p.json`
- `results/pu_training_summary_fold0_hybrid_200e_1536p_valf1.json`
- `results/pu_training_summary_fold0_low_score_200e_1536p_valf1.json`
- `results/pu_training_summary_fold0_random_200e_1536p_valf1.json`
