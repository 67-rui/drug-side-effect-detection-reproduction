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

## Mechanism Subgraph and Contribution Quantification

The explanation layer now includes a local perturbation-based contribution report in `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`, with structured exports in `results/contribution_quantification.json` and `results/contribution_quantification.csv`. A paper-facing aggregate summary is also available in `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`, with structured exports in `results/contribution_aggregate_summary.json` and `results/contribution_aggregate_summary.csv`. The procedure extracts a key mechanism subgraph from the available paths, then zeroes selected compound/target node input features or all node features in a path and re-scores the same CMM-ADR pair with the local trained predictor checkpoint.

Current status:

| Case | Source | Key subgraph | Top node drop | Top path drop | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| herb 277 -> ADR 2931 | `case_zhishi_diarrhoea` | 11 nodes / 8 edges / 14 paths | `target:3223`, 0.009835 | `compound:523 -> target:3223`, 0.010074 | A concrete perturbation-sensitive target/path is identified, but the external evidence remains direction-conflicting |
| herb 237 -> ADR 3989 | `table5_top15` | 2 nodes / 1 edge / 1 path | `compound:1073`, 0.000021 | `compound:1073 -> target:2586`, 0.000021 | The graph path exists, but local perturbation sensitivity is nearly zero and manual evidence review remains unsupported |

Aggregate summary:

| Aggregate | Top feature/path | Cases | Occurrences | Mean drop | Max drop | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Path | `compound:523;target:3223` | 1 | 1 | 0.010074 | 0.010074 | Strongest current perturbation-sensitive path, from the Zhishi-diarrhoea case |
| Node | `target:3223` | 1 | 1 | 0.009835 | 0.009835 | Strongest current perturbation-sensitive target |

This should be described as a subgraph- and path-level sensitivity analysis rather than SHAP, causal attribution, or confirmed biological mechanism. Negative score drops mean the model score increased after masking; they are suppressive or non-supportive sensitivity signals, not confirmed protective biology. The report currently uses the local `saved_models/best_model_for_prediction.pt` checkpoint, so it should not be claimed as final full-positive hybrid PU-XMSAT checkpoint attribution unless a PU predictor checkpoint is explicitly exported and re-scored.

## Recommended Manuscript Wording

Use:

> To address incomplete-label noise in unobserved CMM-ADR pairs, we extended MSAT with a positive-unlabeled training protocol that separates observed positives, reliable negatives, and unlabeled pairs. After correcting candidate-cache construction and using the full-positive pair budget, the mechanism-aware hybrid PU-XMSAT setting achieved seed-robust improvements over the reproduced MSAT baseline on AUC, F1, and MCC, with a consistent positive AUPRC trend. Across two seeds, hybrid PU-XMSAT reached AUC approximately 0.9804, AUPRC approximately 0.9780, F1 approximately 0.9348-0.9351, and MCC approximately 0.8683-0.8684. A focused PU-weight sensitivity analysis supported `unlabeled_weight=0.2` and `reliable_negative_weight=0.8` as a balanced default.

For the explanation layer:

> As a conservative mechanism-interpretation workflow, we further quantified local node sensitivity for selected mechanism-supported cases by zeroing compound or target node input features and re-scoring the same CMM-ADR pair. This analysis identified a perturbation-sensitive target in the Zhishi-diarrhoea case, while the Fragaria case showed negligible local sensitivity. These outputs support mechanism triage and case prioritization, but should not be interpreted as causal effects or externally validated adverse-reaction evidence.

Expanded wording:

> We extracted key mechanism subgraphs and quantified both node-level and path-level perturbation sensitivity for selected cases. In the Zhishi-diarrhoea case, the highest local sensitivity was concentrated on the `compound:523 -> target:3223` path, whereas the Fragaria case showed negligible perturbation sensitivity. This provides a transparent mechanism-prioritization layer, but it does not by itself validate the biological direction or replace external evidence review.

For causal-bias boundaries:

> A causal-bias framework was used to define the interpretation boundary of PU-XMSAT. The method mitigates incomplete-label bias by separating observed positives, reliable negatives, and unlabeled pairs, but the current graph data do not include patient-level co-medication, indication, exposure denominator, dose, or reporting propensity. Therefore, model outputs should be interpreted as pharmacovigilance risk signals and local sensitivity measures rather than causal effect estimates.

Avoid:

- Do not write that PU-XMSAT universally or definitively outperforms MSAT on every metric.
- Do not hide that the AUPRC gain is smaller and one hybrid seed has a borderline paired p value versus MSAT.
- Do not use legacy prefix-cache pilots as strategy-selection evidence.
- Do not treat Table 5 or Table 6 as part of the main performance experiment.
- Do not promote automated literature search hits to direct evidence unless `verified_support=True` is backed by manual source review.
- Do not present the current Grade C cases as confirmed adverse-reaction evidence after manual review.
- Do not present perturbation score drops as SHAP values, causal effects, or final hybrid PU checkpoint attributions.
- Do not claim that PU-XMSAT controls co-medication, indication bias, reporting bias, exposure population, dose, or preparation quality.

## Source Files

Primary tracked sources:

- `results/summary.json`
- `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`
- `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv`
- `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv`
- `results/pu_xmsat_hybrid_seed_robustness_summary.csv`
- `results/pu_xmsat_hybrid_weight_sensitivity_summary.csv`
- `results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`
- `results/PU_XMSAT_FULL_MSAT_PILOT_REPORT.md`
- `results/PU_XMSAT_CASE_EVIDENCE_REPORT.md`
- `results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md`
- `results/PU_XMSAT_CASE_SELECTION_DECISION.md`
- `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`
- `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`
- `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md`
- `results/PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md`
- `results/case_evidence_report.json`
- `results/case_evidence_report.csv`
- `results/case_evidence_manual_review.json`
- `results/contribution_quantification.json`
- `results/contribution_quantification.csv`
- `results/contribution_aggregate_summary.json`
- `results/contribution_aggregate_summary.csv`

Raw PU training JSON files are retained locally and on the server for auditability, but they are intentionally ignored by git unless promoted into curated exports.
