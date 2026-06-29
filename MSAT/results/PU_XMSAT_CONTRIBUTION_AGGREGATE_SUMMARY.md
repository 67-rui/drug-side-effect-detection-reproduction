# PU-XMSAT Contribution Aggregate Summary

This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.

- Batch candidates summarized: 2
- Perturbation-quantified cases: 2
- Positive node perturbation rows: 3
- Near-zero node perturbation rows: 9
- Negative node perturbation rows: 1
- Positive path perturbation rows: 7
- Near-zero path perturbation rows: 3
- Negative path perturbation rows: 5
- Checkpoint: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Checkpoint context: Fallback batch interpretability reuses existing contribution rows from the local predictor checkpoint because no final full-positive hybrid PU-XMSAT predictor checkpoint is available.
- Candidate source: `transitional_mechanism_supported_artifacts`

These are perturbation sensitivity aggregates, not causal or SHAP attributions.
They are not causal effects, not SHAP-equivalent values, and not external clinical validation.

- Fewer than requested top-K: Only 2 candidates with explicit mechanism paths were available.

## Top Pathway Aggregates

| Rank | Path features | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523;target:3223` | 1 | 1 | 0.010074 | 0.010074 | 1 | 0 | 0 |
| 2 | `compound:435;target:8101` | 1 | 1 | 0.000285 | 0.000285 | 1 | 0 | 0 |
| 3 | `compound:523;target:12337` | 1 | 2 | 0.000267 | 0.000267 | 2 | 0 | 0 |
| 4 | `compound:435;target:8967` | 1 | 1 | 0.000241 | 0.000241 | 1 | 0 | 0 |
| 5 | `compound:523;target:7802` | 1 | 2 | 0.000241 | 0.000241 | 2 | 0 | 0 |
| 6 | `target:8101` | 1 | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 7 | `target:8967` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 8 | `compound:1073;target:2586` | 1 | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 9 | `compound:875;target:2432` | 1 | 2 | -0.005437 | -0.005437 | 0 | 0 | 2 |
| 10 | `compound:875;target:12333` | 1 | 1 | -0.005439 | -0.005439 | 0 | 0 | 1 |

## Top Target Aggregates

| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:3223` | `target` | 1 | 1 | 0.009835 | 0.009835 | 1 | 0 | 0 |
| 2 | `target:8101` | `target` | 1 | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 3 | `target:12337` | `target` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 4 | `target:8967` | `target` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 5 | `target:2432` | `target` | 1 | 1 | 0.000006 | 0.000006 | 0 | 1 | 0 |
| 6 | `target:12333` | `target` | 1 | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 7 | `target:7802` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 8 | `target:14208` | `target` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 9 | `target:2586` | `target` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |

## Top Component Aggregates

| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523` | `compound` | 1 | 1 | 0.000239 | 0.000239 | 1 | 0 | 0 |
| 2 | `compound:435` | `compound` | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 3 | `compound:1073` | `compound` | 1 | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 4 | `compound:875` | `compound` | 1 | 1 | -0.005442 | -0.005442 | 0 | 0 | 1 |

## Legacy Top Path Aggregates

| Rank | Path features | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523;target:3223` | 1 | 1 | 0.010074 | 0.010074 | 1 | 0 | 0 |
| 2 | `compound:435;target:8101` | 1 | 1 | 0.000285 | 0.000285 | 1 | 0 | 0 |
| 3 | `compound:523;target:12337` | 1 | 2 | 0.000267 | 0.000267 | 2 | 0 | 0 |
| 4 | `compound:435;target:8967` | 1 | 1 | 0.000241 | 0.000241 | 1 | 0 | 0 |
| 5 | `compound:523;target:7802` | 1 | 2 | 0.000241 | 0.000241 | 2 | 0 | 0 |
| 6 | `target:8101` | 1 | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 7 | `target:8967` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 8 | `compound:1073;target:2586` | 1 | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 9 | `compound:875;target:2432` | 1 | 2 | -0.005437 | -0.005437 | 0 | 0 | 2 |
| 10 | `compound:875;target:12333` | 1 | 1 | -0.005439 | -0.005439 | 0 | 0 | 1 |

## Top Node Aggregates

| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:3223` | `target` | 1 | 1 | 0.009835 | 0.009835 | 1 | 0 | 0 |
| 2 | `compound:523` | `compound` | 1 | 1 | 0.000239 | 0.000239 | 1 | 0 | 0 |
| 3 | `compound:435` | `compound` | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 4 | `target:8101` | `target` | 1 | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 5 | `target:12337` | `target` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 6 | `target:8967` | `target` | 1 | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 7 | `compound:1073` | `compound` | 1 | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 8 | `target:2432` | `target` | 1 | 1 | 0.000006 | 0.000006 | 0 | 1 | 0 |
| 9 | `target:12333` | `target` | 1 | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 10 | `target:7802` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
