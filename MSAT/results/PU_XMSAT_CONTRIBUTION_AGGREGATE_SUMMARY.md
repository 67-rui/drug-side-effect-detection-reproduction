# PU-XMSAT Contribution Aggregate Summary

This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.

- Cases summarized: 2
- Positive node perturbation rows: 11
- Positive path perturbation rows: 10
- Checkpoint: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Checkpoint context: Local predictor checkpoint sensitivity analysis. This is not final full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint is exported and used.

These are perturbation sensitivity aggregates, not causal or SHAP attributions.
They are not causal effects, not SHAP-equivalent values, and not external clinical validation.

## Top Path Aggregates

| Rank | Path features | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523;target:3223` | 1 | 1 | 0.010074 | 0.010074 | 1 | 0 |
| 2 | `compound:435;target:8101` | 1 | 1 | 0.000285 | 0.000285 | 1 | 0 |
| 3 | `compound:523;target:12337` | 1 | 2 | 0.000267 | 0.000267 | 2 | 0 |
| 4 | `compound:435;target:8967` | 1 | 1 | 0.000241 | 0.000241 | 1 | 0 |
| 5 | `compound:523;target:7802` | 1 | 2 | 0.000241 | 0.000241 | 2 | 0 |
| 6 | `target:8101` | 1 | 1 | 0.000071 | 0.000071 | 1 | 0 |
| 7 | `target:8967` | 1 | 1 | 0.000028 | 0.000028 | 1 | 0 |
| 8 | `compound:1073;target:2586` | 1 | 1 | 0.000021 | 0.000021 | 1 | 0 |
| 9 | `compound:875;target:2432` | 1 | 2 | -0.005437 | -0.005437 | 0 | 2 |
| 10 | `compound:875;target:12333` | 1 | 1 | -0.005439 | -0.005439 | 0 | 1 |

## Top Node Aggregates

| Rank | Feature | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:3223` | `target` | 1 | 1 | 0.009835 | 0.009835 | 1 | 0 |
| 2 | `compound:523` | `compound` | 1 | 1 | 0.000239 | 0.000239 | 1 | 0 |
| 3 | `compound:435` | `compound` | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 |
| 4 | `target:8101` | `target` | 1 | 1 | 0.000071 | 0.000071 | 1 | 0 |
| 5 | `target:12337` | `target` | 1 | 1 | 0.000028 | 0.000028 | 1 | 0 |
| 6 | `target:8967` | `target` | 1 | 1 | 0.000028 | 0.000028 | 1 | 0 |
| 7 | `compound:1073` | `compound` | 1 | 1 | 0.000021 | 0.000021 | 1 | 0 |
| 8 | `target:2432` | `target` | 1 | 1 | 0.000006 | 0.000006 | 1 | 0 |
| 9 | `target:12333` | `target` | 1 | 1 | 0.000003 | 0.000003 | 1 | 0 |
| 10 | `target:7802` | `target` | 1 | 1 | 0.000002 | 0.000002 | 1 | 0 |
