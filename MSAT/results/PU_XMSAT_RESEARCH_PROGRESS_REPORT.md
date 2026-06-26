# PU-XMSAT Research Progress Report

**Date:** 2026-06-27
**Project branch:** `codex/pu-xmsat-implementation`  
**Baseline anchor:** `baseline/msat-reproduction-20260626`  
**Current status:** full MSAT PU backend is runnable; prefix-cache pilots, candidate-cache audit, corrected random-cache budget scaling, and a corrected 10-fold PU-XMSAT pilot are complete. PU-XMSAT is now technically strong but still not a demonstrated performance improvement over the reproduced MSAT baseline.

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

### Bounded 10-Fold PU-XMSAT Pilot

The 3-fold pilot was then promoted to a bounded 10-fold run for `random` and `hybrid`. Both runs use 200 epochs, 1,536 PU pairs, reliable negative weight 0.8, unlabeled weight 0.2, and validation-F1 threshold selection.

| Sampling | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Threshold pattern | Runtime |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| hybrid | 0.8998±0.0116 | 0.8989±0.0147 | 0.6758±0.0105 | 0.1350±0.0480 | all 0.99 | 995.6s |
| random | 0.8805±0.0246 | 0.8745±0.0279 | 0.6845±0.0162 | 0.1845±0.0803 | all 0.99 | 906.3s |

### Candidate Cache Audit

After the bounded 10-fold run, the tracked 1,000-row `pu_candidate_scores.sample.jsonl` was inspected and found to contain only prefix-selected pairs from `herb_id=0`. This makes the completed bounded pilots valuable for validating the training loop, logging, runtime, and metric reporting, but it weakens their use as final evidence for negative-sampling strategy selection.

The candidate cache builder has been fixed to use deterministic random bounded sampling by default. The tracked 1,000-row sample cache now covers 507 herbs, and a local 50,000-row random cache covers all 651 herbs and 5,973 ADRs for the next budget-scaling experiment.

### Corrected Random-Cache Budget Scaling

After candidate-cache sampling was fixed, `hybrid` was re-tested with a randomized 50,000-row candidate cache. This corrected setting is the current most reliable PU-XMSAT evidence.

| Run | PU pairs | Folds | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Threshold pattern | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| fold0 | 1,536 | 1 | 0.9028 | 0.8968 | 0.8398 | 0.6860 | 0.66 | 68.1s |
| fold0 | 3,072 | 1 | 0.9319 | 0.9215 | 0.8734 | 0.7484 | 0.36 | 80.3s |
| fold0 | 6,144 | 1 | 0.9383 | 0.9197 | 0.8861 | 0.7738 | 0.46 | 60.1s |
| fold0 | 12,288 | 1 | 0.9563 | 0.9450 | 0.8952 | 0.7963 | 0.59 | 62.6s |
| 3-fold | 6,144 | 3 | 0.9446±0.0027 | 0.9338±0.0094 | 0.8927±0.0076 | 0.7811±0.0110 | 0.37, 0.44, 0.55 | 187.2s |
| 3-fold | 12,288 | 3 | 0.9564±0.0039 | 0.9468±0.0071 | 0.9057±0.0062 | 0.8074±0.0089 | 0.42, 0.40, 0.37 | 193.2s |
| 10-fold | 12,288 | 10 | 0.9547±0.0034 | 0.9458±0.0066 | 0.9035±0.0033 | 0.8039±0.0049 | 0.29-0.52 | 632.1s |

## Current Interpretation

The most important result is not that one strategy has already won, but that negative sampling changes the behavior of the PU-XMSAT model in measurable ways.

The legacy prefix-cache runs are useful as training-pipeline diagnostics, but the corrected random-cache run should be treated as the current valid pilot. Candidate-cache construction had a major effect: after replacing prefix-selected pairs with a randomized 50,000-row cache and increasing the pair budget to 12,288, 10-fold AUC rose to 0.9547 and AUPRC rose to 0.9458.

The corrected run also improves threshold behavior. Instead of selecting the `0.99` boundary in every fold, the 10-fold corrected run selects thresholds between 0.29 and 0.52. This suggests that the earlier threshold pathology was at least partly caused by candidate-cache bias and too-small pair budgets.

Compared with the reproduced MSAT baseline, the corrected PU-XMSAT pilot is still weaker in raw predictive performance: MSAT has AUC 0.9793, AUPRC 0.9771, F1 0.9315, and MCC 0.8625. This is not a reason to discard the direction; it means the current contribution is a corrected, reproducible PU-XMSAT pipeline that is approaching but not yet exceeding the reproduced baseline.

## Paper-Writing Notes

The current work can support the following future manuscript statements once multi-fold validation is complete:

- The reproduction identified incomplete-label noise as a plausible limitation of the original binary negative sampling protocol.
- PU-XMSAT introduces a three-part training set construction: observed positives, reliable negatives, and unlabeled pairs.
- Preliminary fold0 experiments show that PU training is feasible on the full MSAT architecture and that sampling strategy materially affects both ranking and thresholded metrics.
- A bounded 3-fold pilot suggests that random reliable-negative sampling is currently stronger for ranking metrics, while hybrid scoring may help thresholded metrics.
- A bounded 10-fold pilot reverses the 3-fold ranking result under the legacy candidate cache: hybrid sampling gives stronger AUC/AUPRC, while random sampling gives stronger F1/MCC.
- Candidate-cache construction matters: a prefix-selected unobserved-pair cache can bias PU negative sampling and should not be used for final strategy comparison.
- After correcting candidate-cache sampling and increasing the PU pair budget, `hybrid` reaches 10-fold AUC 0.9547 and AUPRC 0.9458, with validation-selected thresholds in a reasonable range.
- Threshold calibration is necessary for fair interpretation of F1/MCC under PU training, but after cache correction it no longer collapses to the 0.99 boundary.

The current work should not yet be written as:

- PU-XMSAT outperforms MSAT in the final experiment.
- `hybrid`, `low_score`, or `random` is the definitive best sampling strategy.
- Fold0 pilot results are equivalent to a formal 10-fold reproduction or extension experiment.

## Next Experimental Plan

1. Compare `hybrid` and `random` under the corrected 50,000-row candidate cache at the same 12,288-pair budget, because only `hybrid` has been retested at this corrected budget so far.
2. If compute allows, test a larger/full-positive budget for `hybrid` to see whether the remaining gap to MSAT is due to the artificial pair cap.
3. Run a calibration ablation only after the ranking experiment is finalized, because corrected-cache thresholds are already much healthier than the legacy-cache thresholds.
4. Preserve the legacy prefix-cache results as a methodological caution: candidate-cache construction can materially change PU learning conclusions.
5. Do not write PU-XMSAT as outperforming MSAT unless a corrected-cache multi-fold result actually exceeds the reproduced baseline.

## Reproducibility Notes

The PU experiments use independent output names and do not overwrite baseline `summary.json`, `table5_summary.json`, or `saved_models/best_model_for_prediction.pt`. Raw pilot JSON files and logs are kept locally and on the server but are ignored by git unless explicitly promoted into a curated result package.
