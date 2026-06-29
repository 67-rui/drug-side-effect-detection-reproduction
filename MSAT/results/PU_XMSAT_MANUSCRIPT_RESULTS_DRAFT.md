# PU-XMSAT Manuscript Results Draft

**Date:** 2026-06-29  
**Branch:** `codex/pu-xmsat-implementation`  
**Baseline anchor:** `baseline/msat-reproduction-20260626`  
**Purpose:** paper-facing result tables and wording for the PU-XMSAT extension. This document summarizes curated tracked result exports only; raw training JSON files remain ignored by git.

## Main Result Position

The reproduced MSAT baseline remains the protocol anchor. PU-XMSAT should be presented as an extension motivated by incomplete labels, not as a replacement for the MSAT reproduction.

The strongest PU-XMSAT setting is:

- Training backend: `full_msat_pu`
- Sampling strategy: `hybrid`
- Candidate cache: corrected randomized `random50k`
- Pair budget: full-positive `66,015` pairs
- Threshold strategy: validation-F1 threshold selection
- PU weights: `unlabeled_weight=0.2`, `reliable_negative_weight=0.8`

This setting is seed-robust across seed `2026` and seed `1337`, and the focused weight-sensitivity pass supports `u0.2/rn0.8` as the balanced default.

## Table A. MSAT Baseline and Main PU-XMSAT Runs

| Setting | Seed | AUC mean | AUPRC mean | F1 mean | MCC mean | Role |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| MSAT reproduced baseline | 42 | 0.979271 | 0.977095 | 0.931451 | 0.862520 | protocol anchor |
| PU-XMSAT random full-positive | 42 | 0.979617 | 0.977273 | 0.932120 | 0.862509 | baseline-level PU feasibility |
| PU-XMSAT random full-positive | 2026 | 0.979732 | 0.977662 | 0.933776 | 0.866051 | random robustness |
| PU-XMSAT hybrid full-positive | 2026 | 0.980420 | 0.977929 | 0.935064 | 0.868409 | strongest single run |
| PU-XMSAT hybrid full-positive | 1337 | 0.980392 | 0.977983 | 0.934767 | 0.868331 | seed robustness |

## Table B. Hybrid PU-XMSAT Versus MSAT

| Comparison | Metric | Mean delta | Wins/losses | Paired t-test p | Manuscript interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| hybrid seed=2026 vs MSAT | AUC | +0.001149 | 9/1 | 0.000419 | significant positive gain |
| hybrid seed=2026 vs MSAT | AUPRC | +0.000834 | 9/1 | 0.003075 | significant positive gain |
| hybrid seed=2026 vs MSAT | F1 | +0.003613 | 8/2 | 0.007438 | significant positive gain |
| hybrid seed=2026 vs MSAT | MCC | +0.005889 | 7/3 | 0.017861 | significant positive gain |
| hybrid seed=1337 vs MSAT | AUC | +0.001121 | 9/1 | 0.001576 | replicated positive gain |
| hybrid seed=1337 vs MSAT | AUPRC | +0.000888 | 6/4 | 0.056348 | positive but borderline |
| hybrid seed=1337 vs MSAT | F1 | +0.003316 | 9/1 | 0.008698 | replicated positive gain |
| hybrid seed=1337 vs MSAT | MCC | +0.005811 | 8/2 | 0.015257 | replicated positive gain |

## Table C. Hybrid Seed Robustness

| Metric | Hybrid seed=2026 | Hybrid seed=1337 | Seed range | Interpretation |
| --- | ---: | ---: | ---: | --- |
| AUC | 0.980420 | 0.980392 | 0.000028 | stable positive gain |
| AUPRC | 0.977929 | 0.977983 | 0.000054 | stable positive trend |
| F1 | 0.935064 | 0.934767 | 0.000297 | stable positive gain |
| MCC | 0.868409 | 0.868331 | 0.000078 | stable positive gain |

## Table D. PU Weight Sensitivity

All rows use full-positive `hybrid`, seed `1337`, and reliable-negative weight `0.8`.

| Setting | AUC | AUPRC | F1 | MCC | Delta vs default | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| u0.1/rn0.8 | 0.979932 | 0.977368 | 0.933956 | 0.866775 | AUC -0.000460; AUPRC -0.000615; F1 -0.000811; MCC -0.001555 | lower unlabeled weight weakens the result |
| u0.2/rn0.8 | 0.980392 | 0.977983 | 0.934767 | 0.868331 | reference | balanced default |
| u0.4/rn0.8 | 0.980474 | 0.977902 | 0.934410 | 0.867410 | AUC +0.000082; AUPRC -0.000081; F1 -0.000357; MCC -0.000921 | similar AUC, slightly weaker thresholded metrics |

## Case Explanation and Evidence Screening Status

The paper-facing explanation/evidence loop is now represented by `results/PU_XMSAT_CASE_EVIDENCE_REPORT.md`, with structured exports in `results/case_evidence_report.json` and `results/case_evidence_report.csv`.

Current status:

| Scope | Count | Interpretation |
| --- | ---: | --- |
| Case rows | 16 | 15 existing MSAT/Table 5-style candidates plus one curated Zhishi-diarrhoea case |
| Grade C rows | 2 | Mechanistic graph/path support is available, but direct external evidence is not verified |
| Grade D rows | 14 | Prediction-only candidates; retain for manual screening, not as evidence-backed claims |
| Rows with automated literature records | 8 | Search hits exist, but they do not meet the verified direct-support criterion |
| Rows with manually verified direct literature support | 0 | No row should currently be promoted to Grade B |
| Grade C rows after manual audit | 2 | Neither should be upgraded: one is externally unsupported, and one is mechanism-relevant but direction-conflicting |

This artifact should be used as the minimal mechanism/external-evidence workflow, not as a claim that Table 5/6 has been equivalently reproduced. The Grade C manual audit is stored in `results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md`; it confirms that the current Grade C rows support only hypothesis generation and screening, not confirmed external validation. The case-selection decision in `results/PU_XMSAT_CASE_SELECTION_DECISION.md` records that the current project does not yet have a strong positive external-validation case suitable for a Table 5-style claim.

## Cluster-Held-Out Generalization

The mentor-requested cluster-held-out experiment is now represented by `results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`, with structured exports in `results/cluster_holdout_generalization_summary.json` and `results/pu_xmsat_cluster_holdout_hybrid_seed2026_10cluster_200e_66015p_valf1.json`. This experiment uses the full-positive hybrid PU-XMSAT setting with seed 2026, 10 herb/CMM clusters, 10 heldout-cluster folds, 200 epochs, `max_pairs=66015`, and validation-F1 thresholding.

Current status:

| Protocol | Folds | AUC | AUPRC | F1 | MCC | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| cluster-heldout, hybrid seed=2026 | 10 | 0.889069 | 0.903219 | 0.176976 | 0.191914 | Harder new-CMM/herb-cluster generalization stress test; ranking signal remains, thresholded metrics degrade sharply |

Important caveats:

- Heldout herbs are filtered from PU training positives, reliable negatives, and unlabeled arrays through `allowed_train_herbs`.
- Validation/test positive CMM-ADR edges are hidden during evaluation.
- Mechanism edges are retained because the protocol tests structural generalization to held-out herb/CMM clusters, not blind removal of all biological annotations.
- Cluster sizes are imbalanced: heldout herb counts range from 1 to 207, and 3 heldout clusters contain fewer than 5 herbs. Macro means should therefore be read together with fold-level cluster sizes.
- This result should be written as a stricter generalization boundary, not as evidence of equally strong deployment performance on unseen herb clusters.

## Mechanism Subgraph and Contribution Quantification

The explanation layer now includes a final-checkpoint-aware perturbation-based contribution report in `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md`, with structured exports in `results/contribution_quantification_top5000_random_controls.json` and `results/contribution_quantification_top5000_random_controls.csv`. A paper-facing aggregate summary is also available in `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md`, with structured exports in `results/contribution_aggregate_summary_top5000_random_controls.json` and `results/contribution_aggregate_summary_top5000_random_controls.csv`. The most direct handoff for writing and mentor review is `results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md`, with structured exports in `results/mechanism_explanation_layer_top5000_random_controls.json` and `results/mechanism_explanation_layer_top5000_random_controls.csv`. The procedure extracts key mechanism subgraphs from parseable final top-5000 prediction paths, then zeroes parsed compound/target node input features in the selected subgraphs or all node features in a path and re-scores the same CMM-ADR pair with the formal full-positive hybrid PU-XMSAT checkpoint.

Current status:

| Scope | Count / value | Interpretation |
| --- | ---: | --- |
| Final top predictions checked | 5000 | Complete final PU-XMSAT top-ranking export |
| Explicit-path candidates | 391 / 5000 | Sparse but systematically measured mechanism coverage |
| Top-50 / Top-100 / Top-500 / Top-1000 coverage | 1/50; 8/100; 31/500; 64/1000 | Top-ranked predictions are mostly not covered by explicit mechanism paths |
| Mechanism-supported candidates selected | 20 | Batch-level contribution quantification target set |
| Quantified cases | 20 | All selected mechanism-supported cases were perturbed |
| Near-zero sensitivity cases | 12 | Most selected cases show small local sensitivity |
| Negative case-level score_drop cases | 0 | No selected case had negative case-level score_drop |
| Ready strong external evidence cases | 0 | Perturbation does not upgrade evidence grade |

Aggregate summary:

| Aggregate | Top feature/path | Cases | Occurrences | Mean drop | Max drop | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Component | `compound:761` / `Compound #761` | 3 | 3 | 0.000309 | 0.000318 | Top component sensitivity; display is an unmapped graph-id fallback |
| Target | `target:15721` / `Target #15721` | 1 | 1 | 0.001174 | 0.001174 | Top target sensitivity; display is an unmapped graph-id fallback |
| Path | `target:15721` / `Target #15721` | 1 | 1 | 0.001174 | 0.001174 | Top pathway sensitivity; should remain a local perturbation signal |

Random controls are available for component, target, and pathway perturbations. The control counts are 100, 100, and 86, with maximum score drops 0.0000004768, 0.0000010729, and 0.0000299215, respectively. The split explanation-layer summary contains 20 component features, 20 target features, and 20 pathway feature groups. The completion audit records 20 subgraph cases and `all_subgraph_nodes_quantified=true`. This should be described as a final-checkpoint-aware subgraph-, component-, target-, and path-level sensitivity screen with random-control context rather than SHAP, causal attribution, or confirmed biological mechanism. Negative score drops mean the model score increased after masking; they are suppressive or non-supportive sensitivity signals, not confirmed protective biology.

## Recommended Manuscript Wording

Use:

> To address incomplete-label noise in unobserved CMM-ADR pairs, we extended MSAT with a positive-unlabeled training protocol that separates observed positives, reliable negatives, and unlabeled pairs. After correcting candidate-cache construction and using the full-positive pair budget, the mechanism-aware hybrid PU-XMSAT setting achieved seed-robust improvements over the reproduced MSAT baseline on AUC, F1, and MCC, with a consistent positive AUPRC trend. Across two seeds, hybrid PU-XMSAT reached AUC approximately 0.9804, AUPRC approximately 0.9780, F1 approximately 0.9348-0.9351, and MCC approximately 0.8683-0.8684. A focused PU-weight sensitivity analysis supported `unlabeled_weight=0.2` and `reliable_negative_weight=0.8` as a balanced default.

For the explanation layer:

> As a conservative mechanism-interpretation workflow, we further exported a formal full-positive hybrid PU-XMSAT checkpoint, ranked the top-5000 unobserved CMM-ADR predictions, and quantified local sensitivity for 20 candidates with parseable explicit mechanism paths. Explicit-path coverage was sparse but measurable: 391 of 5000 top-ranked candidates had parseable paths. The explanation-layer handoff separates component, target, and mechanism-path contributions and includes random perturbation controls, but these outputs should not be interpreted as SHAP values, causal effects, or externally validated adverse-reaction evidence.

Expanded wording:

> We extracted key mechanism subgraphs and quantified node-level, component-level, target-level, and path-level perturbation sensitivity under the formal PU-XMSAT checkpoint. Among the top-5000 final predictions, 391 candidates had parseable explicit mechanism paths, and 20 mechanism-supported candidates were selected for perturbation scoring. The largest aggregate target/pathway sensitivity involved `target:15721` with mean/max drop 0.001174, while the largest component sensitivity involved `compound:761` with mean drop 0.000309. These identifiers currently use unmapped graph-id fallback names, so the result should be interpreted as checkpoint-aware mechanism prioritization rather than validated biological naming or external evidence.

For cluster-held-out generalization:

> To probe generalization beyond the official random-like folds, we evaluated full-positive hybrid PU-XMSAT under a cluster-held-out protocol that held out one herb/CMM cluster per fold. The model retained ranking signal under this stricter setting (AUC 0.8891, AUPRC 0.9032), but thresholded metrics dropped substantially (F1 0.1770, MCC 0.1919). This indicates that new-cluster generalization is a harder deployment setting and should be reported as a stress test rather than as equivalent performance to the official-fold protocol.

For causal-bias boundaries:

> A causal-bias framework was used to define the interpretation boundary of PU-XMSAT. The method mitigates incomplete-label bias by separating observed positives, reliable negatives, and unlabeled pairs, but the current graph data do not include patient-level co-medication, indication, exposure denominator, dose, or reporting propensity. Therefore, model outputs should be interpreted as pharmacovigilance risk signals and local sensitivity measures rather than causal effect estimates.

Avoid:

- Do not write that PU-XMSAT universally or definitively outperforms MSAT on every metric.
- Do not hide that the AUPRC gain is smaller and one hybrid seed has a borderline paired p value versus MSAT.
- Do not use legacy prefix-cache pilots as strategy-selection evidence.
- Do not treat Table 5 or Table 6 as part of the main performance experiment.
- Do not promote automated literature search hits to direct evidence unless `verified_support=True` is backed by manual source review.
- Do not present the current Grade C cases as confirmed adverse-reaction evidence after manual review.
- Do not present perturbation score drops as SHAP values, causal effects, or external validation evidence.
- Do not hide that explicit mechanism coverage is sparse: only 391/5000 top predictions had parseable paths.
- Do not hide cluster-heldout caveats: three heldout clusters have fewer than 5 herbs and F1/MCC are weak.
- Do not claim that PU-XMSAT controls co-medication, indication bias, reporting bias, exposure population, dose, or preparation quality.

## Source Files

Primary tracked sources:

- `results/summary.json`
- `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`
- `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv`
- `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv`
- `results/pu_xmsat_hybrid_seed_robustness_summary.csv`
- `results/pu_xmsat_hybrid_weight_sensitivity_summary.csv`
- `results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md`
- `results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`
- `results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`
- `results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md`
- `results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE_TOP5000_RANDOM_CONTROLS.md`
- `results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`
- `results/PU_XMSAT_FULL_MSAT_PILOT_REPORT.md`
- `results/PU_XMSAT_CASE_EVIDENCE_REPORT.md`
- `results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md`
- `results/PU_XMSAT_CASE_SELECTION_DECISION.md`
- `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`
- `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`
- `results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER.md`
- `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md`
- `results/PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md`
- `results/case_evidence_report.json`
- `results/case_evidence_report.csv`
- `results/case_evidence_manual_review.json`
- `results/contribution_quantification.json`
- `results/contribution_quantification.csv`
- `results/contribution_aggregate_summary.json`
- `results/contribution_aggregate_summary.csv`
- `results/mechanism_explanation_layer.json`
- `results/mechanism_explanation_layer.csv`

Raw PU training JSON files are retained locally and on the server for auditability, but they are intentionally ignored by git unless promoted into curated exports.
