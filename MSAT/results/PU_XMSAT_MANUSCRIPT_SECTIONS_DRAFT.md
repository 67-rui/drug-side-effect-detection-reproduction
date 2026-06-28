# PU-XMSAT Manuscript Sections Draft

**Date:** 2026-06-27
**Branch:** `codex/pu-xmsat-implementation`
**Baseline anchor:** `baseline/msat-reproduction-20260626`
**Purpose:** draft Methods, Results, and Discussion text for the PU-XMSAT extension. The text below is intentionally conservative and should be edited for journal style before submission.

## Methods Draft

### Motivation and Problem Setting

The reproduced MSAT protocol treats unobserved Chinese materia medica adverse drug reaction (CMM-ADR) pairs as negative samples during supervised training. This assumption is practical for binary classification, but it can introduce label noise because an unobserved pair does not necessarily indicate a true absence of association. To reduce this incomplete-label bias, we extended MSAT with a positive-unlabeled learning variant, PU-XMSAT. The extension keeps the reproduced MSAT graph architecture and cross-validation protocol as the baseline anchor, while modifying the construction and weighting of CMM-ADR supervision pairs.

### PU-XMSAT Dataset Construction

For each cross-validation fold, observed CMM-ADR associations in the training partition were treated as positive pairs. Unobserved CMM-ADR pairs were separated into two groups: reliable negatives and unlabeled pairs. Reliable negatives were selected from unobserved pairs by a candidate scoring procedure that combines baseline prediction score, graph-structural support, similarity to known positive associations, ADR frequency, and mechanism-related flags. This candidate cache was generated with deterministic randomized bounded sampling to avoid prefix-selection bias. Earlier prefix-cache experiments were retained only as training-pipeline diagnostics and were not used as final strategy evidence.

The final full-positive PU-XMSAT setting used 66,015 training pairs per fold, corresponding to balanced positive, reliable-negative, and unlabeled partitions under the full-positive pair budget. Reliable-negative pairs were assigned label 0 and unlabeled pairs were also optimized under the binary objective but with reduced sample weight. The main setting used `unlabeled_weight=0.2` and `reliable_negative_weight=0.8`.

### Model and Training

PU-XMSAT used the same `MSATTCMFSFinal` backend as the reproduced MSAT implementation. The message-passing graph followed the reproduction protocol version `2026-06-23-val-test-edge-hidden`, in which validation and test positive CMM-ADR supervision edges are hidden from the training graph to avoid inductive leakage. The PU training backend used weighted binary cross entropy over the fold-specific PU training arrays. Model selection was based on validation AUC, and thresholded test metrics used a validation-F1-selected threshold rather than a fixed 0.5 threshold.

To improve reproducibility of the full MSAT PU backend, NumPy and PyTorch random seeds were reset before each fold-level model initialization. The main seed-controlled hybrid experiments used seed 2026 and seed 1337.

### Sampling and Weight Sensitivity

Three reliable-negative sampling strategies were evaluated during pilot development: `random`, `low_score`, and `hybrid`. Final manuscript claims should focus on the corrected randomized candidate cache and the full-positive budget. The strongest setting was the mechanism-aware `hybrid` sampling strategy, which selects reliable negatives by the combined candidate score.

To check whether the result depended on a single PU weight choice, a focused sensitivity analysis was run for the full-positive hybrid setting using seed 1337 and reliable-negative weight 0.8. The tested unlabeled weights were 0.1, 0.2, and 0.4. The default `unlabeled_weight=0.2` setting was retained because it provided the best balance between ranking metrics and thresholded metrics.

### Statistical Comparison

All primary comparisons used the same 10 official folds as the reproduced MSAT baseline. Mean metrics were computed over fold-level test results. Paired fold-level t-tests were used to compare PU-XMSAT against the reproduced MSAT baseline and, where relevant, to compare hybrid against random PU sampling under the same seed-controlled setting. These paired tests should be interpreted as evidence for the reproduced experimental protocol rather than as a claim of universal superiority.

## Results Draft

### Corrected PU-XMSAT Reaches Baseline-Level Performance Under Random Sampling

After candidate-cache correction and expansion to the full-positive pair budget, random PU-XMSAT reached baseline-level performance relative to the reproduced MSAT main experiment. The seed 42 random full-positive run achieved AUC 0.979617, AUPRC 0.977273, F1 0.932120, and MCC 0.862509. A repeated seed 2026 run achieved AUC 0.979732, AUPRC 0.977662, F1 0.933776, and MCC 0.866051. Compared with the reproduced MSAT baseline, the random seed 2026 run improved all four mean metrics, but fold-level paired tests did not cross the 0.05 threshold. Therefore, random PU-XMSAT should be described as a stable baseline-level feasibility result rather than a statistically supported improvement.

### Mechanism-Aware Hybrid Sampling Provides the Strongest PU-XMSAT Result

The full-positive hybrid PU-XMSAT setting produced the strongest corrected result. With seed 2026, hybrid PU-XMSAT reached AUC 0.980420, AUPRC 0.977929, F1 0.935064, and MCC 0.868409. Relative to the reproduced MSAT baseline, the fold-level mean deltas were +0.001149 for AUC, +0.000834 for AUPRC, +0.003613 for F1, and +0.005889 for MCC. Paired t-tests were below 0.05 for all four metrics.

The result was reproduced with seed 1337. This second hybrid run reached AUC 0.980392, AUPRC 0.977983, F1 0.934767, and MCC 0.868331. Relative to MSAT, seed 1337 remained significantly higher on AUC, F1, and MCC, while the AUPRC gain was positive but borderline (p=0.056348). Across the two hybrid seeds, the metric ranges were extremely small: 0.000028 for AUC, 0.000054 for AUPRC, 0.000297 for F1, and 0.000078 for MCC. These results support the robustness of the full-positive hybrid PU-XMSAT setting.

### Hybrid Sampling Improves Over Random Sampling in the Seed-Controlled Setting

Under seed 2026, hybrid PU-XMSAT improved over random PU-XMSAT on AUC, F1, and MCC. The paired fold-level deltas for hybrid versus random were +0.000688 for AUC, +0.001288 for F1, and +0.002358 for MCC, with paired p values below 0.05. AUPRC was also higher by +0.000267, but this difference was not statistically significant. This pattern suggests that the mechanism-aware reliable-negative score mainly improves ranking and thresholded discrimination, while the AUPRC gain is smaller.

### PU Weight Sensitivity Supports the Default Weighting

The focused PU weight sensitivity analysis tested unlabeled weights 0.1, 0.2, and 0.4 with reliable-negative weight fixed at 0.8. The default u0.2/rn0.8 setting achieved AUC 0.980392, AUPRC 0.977983, F1 0.934767, and MCC 0.868331. Reducing unlabeled weight to 0.1 weakened all four metrics, with significant decreases in AUC and AUPRC relative to the default. Increasing unlabeled weight to 0.4 produced a similar AUC but slightly lower AUPRC, F1, and MCC. These results support u0.2/rn0.8 as the balanced default and indicate that the hybrid result is not a fragile artifact of a single weight choice.

### Case-Level Mechanism and Evidence Screening

As a first paper-facing explanation loop, we generated a case evidence report from the existing MSAT/Table 5-style candidate artifacts and curated case-study outputs. Among 16 candidate rows, two rows had mechanistic graph/path support and were assigned Grade C, while 14 rows remained prediction-only Grade D candidates. Eight rows had automated literature search records, but none had manually verified direct literature support, so no row should currently be promoted to Grade B. This result should be interpreted as an explanation and screening workflow rather than an equivalent reproduction of the original Table 5/6 evidence tables.

## Discussion Draft

### Main Interpretation

PU-XMSAT addresses a methodological limitation exposed during MSAT reproduction: unobserved CMM-ADR pairs should not automatically be interpreted as confirmed negatives. By separating observed positives, reliable negatives, and unlabeled pairs, PU-XMSAT reduces the pressure to learn from potentially mislabeled negative examples. The full-positive hybrid setting produced seed-robust gains over the reproduced MSAT baseline on AUC, F1, and MCC, with a consistent positive AUPRC trend. This supports the hypothesis that reliable-negative selection and down-weighted unlabeled training can improve pharmacovigilance prediction under incomplete labels.

### Why the Hybrid Setting Matters

The hybrid reliable-negative strategy performed better than random sampling in the seed-controlled full-positive setting. This suggests that the mechanism-aware candidate score is not merely a data-processing detail, but contributes useful information for selecting negative supervision pairs. The result also aligns with the broader research direction of adding mechanistic structure and interpretability to adverse reaction prediction. In the manuscript, hybrid sampling should be presented as the main PU-XMSAT configuration, while random sampling should be reported as an important feasibility and ablation baseline.

### Claim Boundary

The current evidence supports a statistically promising and seed-robust PU-XMSAT improvement under the reproduced MSAT protocol. The claim should remain precise. It is appropriate to state that full-positive hybrid PU-XMSAT improved AUC, F1, and MCC over the reproduced MSAT baseline across two seeds, with a stable positive AUPRC trend. It is not appropriate to claim universal superiority on every metric or under every possible sampling and weight setting. The AUPRC gain is smaller than the AUC/F1/MCC gains, and one seed has a borderline paired p value for AUPRC versus MSAT.

### Limitations

First, PU-XMSAT still depends on the quality of the reliable-negative scoring function. Although the corrected random candidate cache removed a clear prefix-selection artifact, the candidate score is heuristic and should be further validated with external evidence. Second, the two-seed robustness analysis supports stability but does not exhaust all sources of stochastic variation. Third, Table 5 and Table 6 in the original MSAT paper remain external validation and interpretation analyses, not main performance experiments. The current public-material reproduction does not fully recover the paper's Table 5 support rate, so PU-XMSAT performance claims should be separated from Table 5 external evidence claims.

The current case-level evidence report also remains intentionally conservative. Automated literature records are useful for screening, but they are not direct evidence until a human reviewer confirms the specific herb-ADR or mechanism claim. Grade C rows can support mechanistic discussion, whereas Grade D rows should be retained only as candidate predictions for future review.

### Next Manuscript Step

The next writing step should be to integrate these sections with the existing MSAT reproduction narrative. The paper should first establish that the reproduced MSAT baseline is protocol-aligned, then motivate incomplete-label noise, then introduce PU-XMSAT as a targeted extension. The Results section should report the full-positive hybrid two-seed table, the paired comparisons, the weight-sensitivity table, and the conservative case evidence screening table. The Discussion should emphasize that PU-XMSAT strengthens the reproduced baseline under incomplete-label assumptions while preserving a conservative claim boundary.

## Source Mapping

Use these tracked files when editing the final manuscript:

- Main result table: `results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md`
- Hybrid seed comparison: `results/pu_xmsat_hybrid_seed_robustness_summary.csv`
- Hybrid versus MSAT paired statistics: `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`, `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv`
- Hybrid versus random statistics: `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv`
- Weight sensitivity: `results/pu_xmsat_hybrid_weight_sensitivity_summary.csv`
- Full progress context: `results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`
