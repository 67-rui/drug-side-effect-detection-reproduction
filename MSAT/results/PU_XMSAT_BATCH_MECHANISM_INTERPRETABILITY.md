# PU-XMSAT Batch Mechanism Interpretability

- Candidate source: `transitional_mechanism_supported_artifacts`
- Candidate source note: Current candidates come from mechanism-supported transitional artifacts, not final PU-XMSAT top-ranking export.
- Checkpoint path: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Checkpoint is final PU-XMSAT: no
- Checkpoint context: Fallback batch interpretability reuses existing contribution rows from the local predictor checkpoint because no final full-positive hybrid PU-XMSAT predictor checkpoint is available.
- Quantified case count: 2
- Unquantified explicit-path candidates: 0
- Cases with explicit mechanism paths: 2
- Near-zero sensitivity cases: 1
- Negative score_drop cases: 1
- Fewer than requested top-K: Only 2 candidates with explicit mechanism paths were available.

Perturbation score drops are local sensitivity signals for mechanism triage; they are not causal effects, not SHAP values, and not external clinical validation.
Negative score_drop is not protective biology; it means the score increased after masking.

## Top Component/Compound Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523` | 1 | 0.000239 | 0.000239 | 1 | 0 | 0 |
| 2 | `compound:435` | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 3 | `compound:1073` | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 4 | `compound:875` | 1 | -0.005442 | -0.005442 | 0 | 0 | 1 |

## Top Target Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:3223` | 1 | 0.009835 | 0.009835 | 1 | 0 | 0 |
| 2 | `target:8101` | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 3 | `target:12337` | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 4 | `target:8967` | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 5 | `target:2432` | 1 | 0.000006 | 0.000006 | 0 | 1 | 0 |
| 6 | `target:12333` | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 7 | `target:7802` | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 8 | `target:14208` | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 9 | `target:2586` | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |

## Top Pathway/Path Contributions

| Rank | Path features | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523;target:3223` | 1 | 0.010074 | 0.010074 | 1 | 0 | 0 |
| 2 | `compound:435;target:8101` | 1 | 0.000285 | 0.000285 | 1 | 0 | 0 |
| 3 | `compound:523;target:12337` | 1 | 0.000267 | 0.000267 | 2 | 0 | 0 |
| 4 | `compound:435;target:8967` | 1 | 0.000241 | 0.000241 | 1 | 0 | 0 |
| 5 | `compound:523;target:7802` | 1 | 0.000241 | 0.000241 | 2 | 0 | 0 |
| 6 | `target:8101` | 1 | 0.000071 | 0.000071 | 0 | 1 | 0 |
| 7 | `target:8967` | 1 | 0.000028 | 0.000028 | 0 | 1 | 0 |
| 8 | `compound:1073;target:2586` | 1 | 0.000021 | 0.000021 | 0 | 1 | 0 |
| 9 | `compound:875;target:2432` | 1 | -0.005437 | -0.005437 | 0 | 0 | 2 |
| 10 | `compound:875;target:12333` | 1 | -0.005439 | -0.005439 | 0 | 0 | 1 |

## Near-Zero Sensitivity Cases

- `table5_top15` herb 237 -> ADR 3989

## Negative score_drop Cases

- `case_zhishi_diarrhoea` herb 277 -> ADR 2931

## Case-Level Explanation Examples

- `table5_top15` herb 237 -> ADR 3989: top `compound:1073;target:2586` drop 0.000021; class `near_zero`.
- `case_zhishi_diarrhoea` herb 277 -> ADR 2931: top `compound:523;target:3223` drop 0.010074; class `positive`.

## Claim Boundary

This batch uses mechanism-supported candidate artifacts rather than final PU-XMSAT top-ranking export when no final export is present. It also uses the local predictor checkpoint unless an explicit final PU checkpoint is supplied. Perturbation sensitivity is not causal evidence, not SHAP, not clinical validation, and cannot upgrade evidence grades.
