# PU-XMSAT Manuscript Results Draft

**Date:** 2026-06-27  
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

## Recommended Manuscript Wording

Use:

> To address incomplete-label noise in unobserved CMM-ADR pairs, we extended MSAT with a positive-unlabeled training protocol that separates observed positives, reliable negatives, and unlabeled pairs. After correcting candidate-cache construction and using the full-positive pair budget, the mechanism-aware hybrid PU-XMSAT setting achieved seed-robust improvements over the reproduced MSAT baseline on AUC, F1, and MCC, with a consistent positive AUPRC trend. Across two seeds, hybrid PU-XMSAT reached AUC approximately 0.9804, AUPRC approximately 0.9780, F1 approximately 0.9348-0.9351, and MCC approximately 0.8683-0.8684. A focused PU-weight sensitivity analysis supported `unlabeled_weight=0.2` and `reliable_negative_weight=0.8` as a balanced default.

Avoid:

- Do not write that PU-XMSAT universally or definitively outperforms MSAT on every metric.
- Do not hide that the AUPRC gain is smaller and one hybrid seed has a borderline paired p value versus MSAT.
- Do not use legacy prefix-cache pilots as strategy-selection evidence.
- Do not treat Table 5 or Table 6 as part of the main performance experiment.

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

Raw PU training JSON files are retained locally and on the server for auditability, but they are intentionally ignored by git unless promoted into curated exports.
