# PU-XMSAT Contribution Aggregate Summary

This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.

- Batch candidates summarized: 1
- Top-prediction candidates checked: 50
- Coverage-missing top-prediction candidates: 49
- Perturbation-quantified cases: 1
- Positive node perturbation rows: 0
- Near-zero node perturbation rows: 6
- Negative node perturbation rows: 0
- Positive path perturbation rows: 0
- Near-zero path perturbation rows: 12
- Negative path perturbation rows: 0
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint attribution.
- Candidate source: `final_pu_xmsat_top_predictions`
- All node aggregates retained: 6
- All path aggregates retained: 6

These are perturbation sensitivity aggregates, not causal or SHAP attributions.
They are not causal effects, not SHAP-equivalent values, and not external clinical validation.

- Fewer than requested top-K: Only 1 candidates with explicit mechanism paths were available.

## Top Pathway Aggregates

| Rank | Path features | Display path | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073;target:7213` | Compound #1073;Target #7213 | 1 | 2 | 0.000018 | 0.000018 | 0 | 2 | 0 |
| 2 | `compound:1073;target:2586` | Compound #1073;Target #2586 | 1 | 2 | 0.000015 | 0.000015 | 0 | 2 | 0 |
| 3 | `compound:965;target:7213` | Compound #965;Target #7213 | 1 | 2 | 0.000005 | 0.000005 | 0 | 2 | 0 |
| 4 | `compound:965;target:2586` | Compound #965;Target #2586 | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 5 | `compound:1023;target:7213` | Compound #1023;Target #7213 | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 6 | `compound:1023;target:6478` | Compound #1023;Target #6478 | 1 | 2 | -0.000001 | -0.000001 | 0 | 2 | 0 |

## Top Target Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:7213` | Target #7213 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 2 | `target:2586` | Target #2586 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 3 | `target:6478` | Target #6478 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |

## Top Component Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073` | Compound #1073 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000013 | 0.000013 | 0 | 1 | 0 |
| 2 | `compound:965` | Compound #965 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 3 | `compound:1023` | Compound #1023 | `unmapped_graph_id` | `compound` | 1 | 1 | -0.000003 | -0.000003 | 0 | 1 | 0 |

## Legacy Top Path Aggregates

| Rank | Path features | Display path | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073;target:7213` | Compound #1073;Target #7213 | 1 | 2 | 0.000018 | 0.000018 | 0 | 2 | 0 |
| 2 | `compound:1073;target:2586` | Compound #1073;Target #2586 | 1 | 2 | 0.000015 | 0.000015 | 0 | 2 | 0 |
| 3 | `compound:965;target:7213` | Compound #965;Target #7213 | 1 | 2 | 0.000005 | 0.000005 | 0 | 2 | 0 |
| 4 | `compound:965;target:2586` | Compound #965;Target #2586 | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 5 | `compound:1023;target:7213` | Compound #1023;Target #7213 | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 6 | `compound:1023;target:6478` | Compound #1023;Target #6478 | 1 | 2 | -0.000001 | -0.000001 | 0 | 2 | 0 |

## Top Node Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073` | Compound #1073 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000013 | 0.000013 | 0 | 1 | 0 |
| 2 | `target:7213` | Target #7213 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 3 | `target:2586` | Target #2586 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 4 | `target:6478` | Target #6478 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 5 | `compound:965` | Compound #965 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 6 | `compound:1023` | Compound #1023 | `unmapped_graph_id` | `compound` | 1 | 1 | -0.000003 | -0.000003 | 0 | 1 | 0 |
