# PU-XMSAT Research Progress Report

**Date:** 2026-06-26  
**Project branch:** `codex/pu-xmsat-implementation`  
**Baseline anchor:** `baseline/msat-reproduction-20260626`  
**Current status:** full MSAT PU backend is runnable; fold0 and bounded 3-fold pilot experiments are complete; formal 10-fold PU-XMSAT claims are not yet complete.

## Research Motivation

The original MSAT reproduction has reached a stable baseline for the main experiment, but the reproduction process exposed a key methodological limitation: unobserved herb-ADR pairs are not necessarily true negative associations. Treating all unobserved pairs as negatives can introduce label noise and may distort both prediction and interpretation. PU-XMSAT therefore extends MSAT by separating observed positives, reliable negatives, and unlabeled pairs, and by training with sample-weighted PU objectives.

This direction directly supports the planned research theme: improving Chinese materia medica adverse reaction prediction under incomplete labels, with mechanism-aware explanation and external evidence screening as downstream support.

## Implemented Components

The current implementation has completed the first full technical path from data construction to GPU training:

- Reliable negative candidate scoring and three sampling strategies: `hybrid`, `low_score`, `random`.
- PU dataset construction with observed positive, reliable negative, and unlabeled pair partitions.
- Weighted PU BCE objective and a training helper that supports sample weights without changing the default MSAT baseline training path.
- `full_msat_pu` backend using `MSATTCMFSFinal`, official fold splits, validation/test positive edge hiding, and independent PU output artifacts.
- Validation-threshold calibration option: `fixed_0_5` or `val_f1`.
- PU experiment reports and evidence screening reports separated from baseline result artifacts to avoid result pollution.

## Completed Pilot Experiments

### Budget Scaling Under Hybrid Sampling

| Fold | Sampling | PU pairs | Epochs | Threshold | AUC | AUPRC | F1 | MCC | Best epoch | Runtime |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | hybrid | 384 | 50 | fixed 0.5 | 0.8497 | 0.8402 | 0.6605 | 0.1234 | 50 | 27.7s |
| 0 | hybrid | 768 | 100 | fixed 0.5 | 0.8643 | 0.8511 | 0.6543 | 0.0441 | 100 | 52.3s |
| 0 | hybrid | 1536 | 200 | fixed 0.5 | 0.8855 | 0.8745 | 0.6551 | 0.0607 | 200 | 101.9s |

The ranking metrics improve as training budget and PU pair count increase, suggesting that the full PU training path is learning meaningful signal rather than only passing a smoke test. The fixed threshold, however, produces weak MCC because the score distribution is poorly calibrated.

### Threshold-Calibrated Sampling Comparison

| Fold | Sampling | PU pairs | Epochs | Threshold strategy | Selected threshold | AUC | AUPRC | F1 | MCC | Best epoch | Runtime |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | hybrid | 1536 | 200 | val_f1 | 0.9900 | 0.8832 | 0.8706 | 0.6585 | 0.1037 | 197 | 99.7s |
| 0 | low_score | 1536 | 200 | val_f1 | 0.9900 | 0.8313 | 0.8079 | 0.7532 | 0.4665 | 7 | 52.9s |
| 0 | random | 1536 | 200 | val_f1 | 0.9900 | 0.9167 | 0.9175 | 0.6627 | 0.1417 | 200 | 101.1s |

### Bounded 3-Fold Sampling Comparison

The fold0 result suggested different winners depending on metric type, so a bounded 3-fold pilot was run with the same 200 epoch / 1,536 pair / `val_f1` setting.

| Sampling | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Selected thresholds | Best epochs | Runtime |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| hybrid | 0.8696±0.0130 | 0.8583±0.0220 | 0.6953±0.0317 | 0.1984±0.1885 | 0.99, 0.99, 0.99 | 12, 136, 199 | 253.1s |
| low_score | 0.8722±0.0311 | 0.8658±0.0420 | 0.6821±0.0181 | 0.1644±0.1055 | 0.99, 0.99, 0.99 | 193, 174, 11 | 252.4s |
| random | 0.8852±0.0170 | 0.8805±0.0207 | 0.6739±0.0143 | 0.1251±0.0326 | 0.99, 0.99, 0.99 | 200, 200, 162 | 298.7s |

## Current Interpretation

The most important result is not that one strategy has already won, but that negative sampling changes the behavior of the PU-XMSAT model in measurable ways.

`random` produces the strongest AUC/AUPRC in both fold0 and the bounded 3-fold pilot, so it is currently the best candidate if the paper prioritizes ranking ability. `hybrid` has the best 3-fold F1/MCC after threshold calibration, but its MCC variance is large, so it should be framed as a secondary threshold-metric candidate rather than a definitive winner. `low_score` looked strong on fold0 F1/MCC, but the 3-fold result does not preserve that advantage.

All calibrated runs selected threshold `0.99`, meaning the model is not well calibrated as a probability estimator. Therefore, AUC/AUPRC should remain the primary evaluation metrics in the next paper-facing experiment, while F1/MCC should be clearly described as validation-threshold-calibrated secondary metrics. A later version can add temperature scaling or validation Platt calibration, but calibration should not block the next 10-fold ranking experiment.

## Paper-Writing Notes

The current work can support the following future manuscript statements once multi-fold validation is complete:

- The reproduction identified incomplete-label noise as a plausible limitation of the original binary negative sampling protocol.
- PU-XMSAT introduces a three-part training set construction: observed positives, reliable negatives, and unlabeled pairs.
- Preliminary fold0 experiments show that PU training is feasible on the full MSAT architecture and that sampling strategy materially affects both ranking and thresholded metrics.
- A bounded 3-fold pilot suggests that random reliable-negative sampling is currently stronger for ranking metrics, while hybrid scoring may help thresholded metrics.
- Threshold calibration is necessary for fair interpretation of F1/MCC under PU training, but ranking metrics should be emphasized before probability calibration is improved.

The current work should not yet be written as:

- PU-XMSAT outperforms MSAT in the final experiment.
- `hybrid`, `low_score`, or `random` is the definitive best sampling strategy.
- Fold0 pilot results are equivalent to a formal 10-fold reproduction or extension experiment.

## Next Experimental Plan

1. Run a formal 10-fold PU-XMSAT experiment with `random` sampling, 200 epochs, 1,536 pairs, and `val_f1` threshold reporting.
2. If compute budget allows, run the same 10-fold protocol for `hybrid` as a secondary comparison focused on thresholded metrics.
3. Summarize mean and standard deviation for AUC, AUPRC, F1, MCC, selected threshold, best epoch, and runtime.
4. Compare the selected PU-XMSAT protocol against the reproduced MSAT baseline, while clearly stating that the current PU experiments use a bounded pair budget and are an extension rather than an exact reproduction table.
5. After the 10-fold ranking result is available, decide whether probability calibration should become a separate ablation.

## Reproducibility Notes

The PU experiments use independent output names and do not overwrite baseline `summary.json`, `table5_summary.json`, or `saved_models/best_model_for_prediction.pt`. Raw pilot JSON files and logs are kept locally and on the server but are ignored by git unless explicitly promoted into a curated result package.
