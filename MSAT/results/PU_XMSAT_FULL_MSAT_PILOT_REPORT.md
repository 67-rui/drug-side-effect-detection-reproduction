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

## Bounded 3-Fold Strategy Comparison

To check whether the fold0 pattern was stable, a bounded 3-fold pilot was run with the same budget: 200 epochs, 1,536 PU pairs, reliable negative weight 0.8, unlabeled weight 0.2, and validation-F1 threshold selection.

| Sampling strategy | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Selected thresholds | Best epochs | Runtime |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| hybrid | 0.8696±0.0130 | 0.8583±0.0220 | 0.6953±0.0317 | 0.1984±0.1885 | 0.99, 0.99, 0.99 | 12, 136, 199 | 253.1s |
| low_score | 0.8722±0.0311 | 0.8658±0.0420 | 0.6821±0.0181 | 0.1644±0.1055 | 0.99, 0.99, 0.99 | 193, 174, 11 | 252.4s |
| random | 0.8852±0.0170 | 0.8805±0.0207 | 0.6739±0.0143 | 0.1251±0.0326 | 0.99, 0.99, 0.99 | 200, 200, 162 | 298.7s |

## Bounded 10-Fold PU-XMSAT Pilot

The next step promoted the strongest 3-fold ranking candidate (`random`) and the strongest mechanism-scored candidate (`hybrid`) to 10 folds under the same bounded budget: 200 epochs, 1,536 PU pairs, reliable negative weight 0.8, unlabeled weight 0.2, and validation-F1 threshold selection.

| Sampling strategy | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Selected thresholds | Best epochs | Runtime |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| hybrid | 0.8998±0.0116 | 0.8989±0.0147 | 0.6758±0.0105 | 0.1350±0.0480 | all 0.99 | 200, 200, 200, 200, 200, 200, 200, 153, 200, 200 | 995.6s |
| random | 0.8805±0.0246 | 0.8745±0.0279 | 0.6845±0.0162 | 0.1845±0.0803 | all 0.99 | 137, 200, 11, 200, 13, 200, 200, 200, 200, 183 | 906.3s |

## Interpretation

The full MSAT PU backend is now operational on GPU. AUC and AUPRC improve as epochs and PU pair count increase, and the best validation AUC occurs at the final epoch for all three runs. This suggests the pilot has not yet reached a clear plateau.

Threshold-dependent metrics need care. Recall is nearly 1.0 at the fixed `0.5` threshold, while precision and MCC remain weak. Validation-threshold calibration improves interpretability of F1/MCC, but all three calibrated runs selected the upper grid boundary (`0.99`), which indicates that probability calibration is still poor and thresholded metrics should be reported as secondary.

The negative-sampling comparison is now clearer but still not final. In the bounded 10-fold pilot, `hybrid` has the stronger ranking metrics, while `random` has stronger thresholded F1/MCC. This reverses part of the 3-fold signal and shows why the 10-fold check was necessary. Neither bounded PU setting currently approaches the reproduced MSAT baseline AUC/AUPRC, so the result should be written as a validated PU-XMSAT training pipeline and strategy comparison, not as a completed performance improvement over MSAT.

## Recommendation

Do not claim PU-XMSAT superiority yet. The next technical improvement should increase the PU training budget or remove the artificial 1,536-pair cap so that PU-XMSAT uses a training signal closer to the original MSAT fold size. A second priority is probability calibration, because all validation-threshold runs selected the `0.99` boundary. Until those are addressed, the paper-facing claim should be limited to: PU-XMSAT is implemented, reproducible, and exposes measurable trade-offs among reliable-negative sampling strategies.

## Raw Artifacts

The raw JSON summaries are available locally and on the server but are ignored by git to avoid result-artifact pollution:

- `results/pu_training_summary_fold0_50e_384p.json`
- `results/pu_training_summary_fold0_100e_768p.json`
- `results/pu_training_summary_fold0_200e_1536p.json`
- `results/pu_training_summary_fold0_hybrid_200e_1536p_valf1.json`
- `results/pu_training_summary_fold0_low_score_200e_1536p_valf1.json`
- `results/pu_training_summary_fold0_random_200e_1536p_valf1.json`
- `results/pu_training_summary_3fold_hybrid_200e_1536p_valf1.json`
- `results/pu_training_summary_3fold_low_score_200e_1536p_valf1.json`
- `results/pu_training_summary_3fold_random_200e_1536p_valf1.json`
- `results/pu_training_summary_10fold_hybrid_200e_1536p_valf1.json`
- `results/pu_training_summary_10fold_random_200e_1536p_valf1.json`
