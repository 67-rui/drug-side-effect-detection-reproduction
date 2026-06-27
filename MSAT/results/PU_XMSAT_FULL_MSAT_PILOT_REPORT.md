# PU-XMSAT Full MSAT Pilot Report

**Date:** 2026-06-27
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

## Candidate Cache Caveat

After the bounded 10-fold pilot, the candidate cache generation script was audited and fixed. The original tracked `pu_candidate_scores.sample.jsonl` contained 1,000 prefix-selected unobserved pairs, all from `herb_id=0`. This means the fold0, 3-fold, and 10-fold bounded pilots above are still useful as training-pipeline and runtime diagnostics, but they should not be treated as final negative-sampling strategy evidence.

The cache builder now uses deterministic random bounded sampling by default, and the tracked 1,000-row sample cache has been refreshed to cover 507 herbs. A larger local 50,000-row random cache was also generated for the next budget-scaling experiment.

## Corrected Random-Cache Budget Scaling

After fixing candidate-cache sampling, `hybrid` was used for budget scaling with the randomized 50,000-row candidate cache, and `random` was then promoted to a corrected 10-fold run at the strongest bounded budget. These corrected runs should be treated as the current valid PU-XMSAT pilots, while the prefix-cache results above remain diagnostic.

| Run | PU pairs | Folds | AUC mean±std | AUPRC mean±std | F1 mean±std | MCC mean±std | Thresholds | Best epochs | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |
| hybrid fold0 random50k | 1,536 | 1 | 0.9028 | 0.8968 | 0.8398 | 0.6860 | 0.66 | 39 | 68.1s |
| hybrid fold0 random50k | 3,072 | 1 | 0.9319 | 0.9215 | 0.8734 | 0.7484 | 0.36 | 65 | 80.3s |
| hybrid fold0 random50k | 6,144 | 1 | 0.9383 | 0.9197 | 0.8861 | 0.7738 | 0.46 | 21 | 60.1s |
| hybrid fold0 random50k | 12,288 | 1 | 0.9563 | 0.9450 | 0.8952 | 0.7963 | 0.59 | 26 | 62.6s |
| hybrid 3-fold random50k | 6,144 | 3 | 0.9446±0.0027 | 0.9338±0.0094 | 0.8927±0.0076 | 0.7811±0.0110 | 0.37, 0.44, 0.55 | 26, 30, 24 | 187.2s |
| hybrid 3-fold random50k | 12,288 | 3 | 0.9564±0.0039 | 0.9468±0.0071 | 0.9057±0.0062 | 0.8074±0.0089 | 0.42, 0.40, 0.37 | 28, 37, 27 | 193.2s |
| 10-fold hybrid random50k | 12,288 | 10 | 0.9547±0.0034 | 0.9458±0.0066 | 0.9035±0.0033 | 0.8039±0.0049 | 0.29-0.52 | 23-31 | 632.1s |
| 10-fold random random50k | 12,288 | 10 | 0.9748±0.0016 | 0.9719±0.0020 | 0.9272±0.0039 | 0.8521±0.0069 | 0.28-0.51 | 23-37 | 643.8s |

## Interpretation

The full MSAT PU backend is now operational on GPU. AUC and AUPRC improve as epochs and PU pair count increase, and the best validation AUC occurs at the final epoch for all three runs. This suggests the pilot has not yet reached a clear plateau.

Threshold-dependent metrics need care. Recall is nearly 1.0 at the fixed `0.5` threshold, while precision and MCC remain weak. Validation-threshold calibration improves interpretability of F1/MCC, but all three calibrated runs selected the upper grid boundary (`0.99`), which indicates that probability calibration is still poor and thresholded metrics should be reported as secondary.

The corrected random-cache runs change the interpretation substantially. The prefix-cache pilots should be treated only as training-pipeline diagnostics. With the randomized 50,000-row candidate cache and a 12,288-pair budget, `random` sampling reaches AUC 0.9748 and AUPRC 0.9719 over 10 folds, while `hybrid` reaches AUC 0.9547 and AUPRC 0.9458. This confirms that the candidate-cache bias was a major bottleneck and that the PU-XMSAT direction remains technically viable.

The strongest corrected PU-XMSAT result is still slightly below the reproduced MSAT main baseline: AUC 0.9793, AUPRC 0.9771, F1 0.9315, MCC 0.8625. Therefore it should be described as a near-baseline corrected pilot and not yet as a final performance improvement.

## Recommendation

Do not claim PU-XMSAT superiority yet. The next technical step should explore an even larger/full-positive budget for `random`, because it is now the strongest corrected strategy and is already close to the MSAT baseline. The paper-facing claim can now be strengthened to: PU-XMSAT is implemented, reproducible, and after correcting candidate-cache sampling reaches a near-baseline 10-fold result.

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
- `results/pu_training_summary_10fold_hybrid_200e_12288p_valf1_random50k.json`
- `results/pu_training_summary_10fold_random_200e_12288p_valf1_random50k.json`
- `results/pu_training_summary_3fold_hybrid_200e_12288p_valf1_random50k.json`
- `results/pu_training_summary_3fold_hybrid_200e_6144p_valf1_random50k.json`
- `results/pu_training_summary_fold0_hybrid_200e_12288p_valf1_random50k.json`
- `results/pu_training_summary_fold0_hybrid_200e_1536p_valf1_random50k.json`
- `results/pu_training_summary_fold0_hybrid_200e_3072p_valf1_random50k.json`
- `results/pu_training_summary_fold0_hybrid_200e_6144p_valf1_random50k.json`
