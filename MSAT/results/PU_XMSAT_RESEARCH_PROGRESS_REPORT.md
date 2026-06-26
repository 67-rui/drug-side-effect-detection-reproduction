# PU-XMSAT Research Progress Report

**Date:** 2026-06-26  
**Project branch:** `codex/pu-xmsat-implementation`  
**Baseline anchor:** `baseline/msat-reproduction-20260626`  
**Current status:** full MSAT PU backend is runnable; fold0, bounded 3-fold, and bounded 10-fold pilot experiments are complete; candidate cache prefix bias has been identified and fixed; PU-XMSAT is not yet a demonstrated performance improvement over the reproduced MSAT baseline.

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

## Current Interpretation

The most important result is not that one strategy has already won, but that negative sampling changes the behavior of the PU-XMSAT model in measurable ways.

`random` produces the strongest AUC/AUPRC in fold0 and the bounded 3-fold pilot, but `hybrid` becomes stronger on AUC/AUPRC in the bounded 10-fold pilot. This indicates that fold0 and 3-fold evidence was not sufficient to select a final strategy. However, because those runs used the legacy prefix-selected candidate cache, the strategy ordering should be treated as provisional until re-tested with the randomized candidate cache.

All calibrated runs selected threshold `0.99`, meaning the model is not well calibrated as a probability estimator. Therefore, AUC/AUPRC should remain the primary evaluation metrics, while F1/MCC should be clearly described as validation-threshold-calibrated secondary metrics.

Compared with the reproduced MSAT baseline, the bounded PU-XMSAT pilot is still weaker in raw predictive performance. This is not a reason to discard the direction, but it changes the research interpretation: the current contribution is a working PU-XMSAT pipeline and a diagnosis of reliable-negative sampling behavior. The next performance-oriented step is to remove or enlarge the current 1,536-pair training cap so the PU model sees a training signal closer to the original MSAT protocol.

## Paper-Writing Notes

The current work can support the following future manuscript statements once multi-fold validation is complete:

- The reproduction identified incomplete-label noise as a plausible limitation of the original binary negative sampling protocol.
- PU-XMSAT introduces a three-part training set construction: observed positives, reliable negatives, and unlabeled pairs.
- Preliminary fold0 experiments show that PU training is feasible on the full MSAT architecture and that sampling strategy materially affects both ranking and thresholded metrics.
- A bounded 3-fold pilot suggests that random reliable-negative sampling is currently stronger for ranking metrics, while hybrid scoring may help thresholded metrics.
- A bounded 10-fold pilot reverses the 3-fold ranking result under the legacy candidate cache: hybrid sampling gives stronger AUC/AUPRC, while random sampling gives stronger F1/MCC.
- Candidate-cache construction matters: a prefix-selected unobserved-pair cache can bias PU negative sampling and should not be used for final strategy comparison.
- Threshold calibration is necessary for fair interpretation of F1/MCC under PU training, but the current threshold grid selecting 0.99 in all folds shows that probability calibration remains unresolved.

The current work should not yet be written as:

- PU-XMSAT outperforms MSAT in the final experiment.
- `hybrid`, `low_score`, or `random` is the definitive best sampling strategy.
- Fold0 pilot results are equivalent to a formal 10-fold reproduction or extension experiment.

## Next Experimental Plan

1. Re-run fold0 budget scaling with the randomized 50,000-row candidate cache so the next comparison is not based on prefix-selected unobserved pairs.
2. Start with `hybrid`, because it is the current 10-fold ranking leader under the legacy cache, but treat this as a retest rather than a confirmed best strategy.
3. If larger-budget fold0 improves AUC/AUPRC, run a bounded multi-fold check before another 10-fold run.
4. Add probability calibration as a separate ablation after the ranking experiment improves, because all current `val_f1` runs select the maximum threshold.
5. Preserve the current 10-fold bounded results as a negative/diagnostic finding for the paper: naive bounded PU training is feasible, but not yet a direct performance improvement over MSAT.

## Reproducibility Notes

The PU experiments use independent output names and do not overwrite baseline `summary.json`, `table5_summary.json`, or `saved_models/best_model_for_prediction.pt`. Raw pilot JSON files and logs are kept locally and on the server but are ignored by git unless explicitly promoted into a curated result package.
