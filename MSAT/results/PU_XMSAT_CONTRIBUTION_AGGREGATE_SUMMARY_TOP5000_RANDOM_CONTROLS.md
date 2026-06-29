# PU-XMSAT Contribution Aggregate Summary

This report summarizes node-level and path-level perturbation sensitivity across quantified mechanism cases.

- Batch candidates summarized: 20
- Top-prediction candidates checked: 5000
- Coverage-missing top-prediction candidates: 4609
- Perturbation-quantified cases: 20
- Positive node perturbation rows: 9
- Near-zero node perturbation rows: 103
- Negative node perturbation rows: 0
- Positive path perturbation rows: 13
- Near-zero path perturbation rows: 73
- Negative path perturbation rows: 0
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint attribution.
- Candidate source: `final_pu_xmsat_top_predictions`
- All node aggregates retained: 59
- All path aggregates retained: 81

These are perturbation sensitivity aggregates, not causal or SHAP attributions.
They are not causal effects, not SHAP-equivalent values, and not external clinical validation.

## Top Pathway Aggregates

| Rank | Path features | Display path | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `compound:821;target:11486` | Compound #821;Target #11486 | 1 | 1 | 0.000320 | 0.000320 | 1 | 0 | 0 |
| 3 | `compound:821;target:469` | Compound #821;Target #469 | 1 | 1 | 0.000315 | 0.000315 | 1 | 0 | 0 |
| 4 | `compound:761;target:7802` | Compound #761;Target #7802 | 2 | 2 | 0.000314 | 0.000318 | 2 | 0 | 0 |
| 5 | `compound:761;target:2432` | Compound #761;Target #2432 | 1 | 1 | 0.000310 | 0.000310 | 1 | 0 | 0 |
| 6 | `compound:761;target:19336` | Compound #761;Target #19336 | 1 | 1 | 0.000300 | 0.000300 | 1 | 0 | 0 |
| 7 | `compound:821;target:19336` | Compound #821;Target #19336 | 1 | 1 | 0.000263 | 0.000263 | 1 | 0 | 0 |
| 8 | `compound:821;target:1774` | Compound #821;Target #1774 | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 9 | `compound:821;target:2586` | Compound #821;Target #2586 | 2 | 2 | 0.000210 | 0.000214 | 2 | 0 | 0 |
| 10 | `compound:1073;target:15692` | Compound #1073;Target #15692 | 1 | 1 | 0.000124 | 0.000124 | 1 | 0 | 0 |
| 11 | `compound:965;target:15692` | Compound #965;Target #15692 | 1 | 1 | 0.000102 | 0.000102 | 1 | 0 | 0 |
| 12 | `compound:1023;target:1782` | Compound #1023;Target #1782 | 1 | 1 | 0.000097 | 0.000097 | 0 | 1 | 0 |
| 13 | `compound:480;target:11486` | Compound #480;Target #11486 | 1 | 1 | 0.000046 | 0.000046 | 0 | 1 | 0 |
| 14 | `compound:480;target:7213` | Compound #480;Target #7213 | 2 | 2 | 0.000044 | 0.000044 | 0 | 2 | 0 |
| 15 | `compound:480;target:1933` | Compound #480;Target #1933 | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 16 | `compound:480;target:13438` | Compound #480;Target #13438 | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 17 | `compound:480;target:19336` | Compound #480;Target #19336 | 1 | 1 | 0.000037 | 0.000037 | 0 | 1 | 0 |
| 18 | `compound:480;target:2432` | Compound #480;Target #2432 | 1 | 1 | 0.000035 | 0.000035 | 0 | 1 | 0 |
| 19 | `compound:480;target:7938` | Compound #480;Target #7938 | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |
| 20 | `compound:480;target:2586` | Compound #480;Target #2586 | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |

## Top Target Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 | `unmapped_graph_id` | `target` | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `target:1782` | Target #1782 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000096 | 0.000096 | 0 | 1 | 0 |
| 3 | `target:15692` | Target #15692 | `unmapped_graph_id` | `target` | 2 | 2 | 0.000052 | 0.000102 | 1 | 1 | 0 |
| 4 | `target:19496` | Target #19496 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000007 | 0.000007 | 0 | 1 | 0 |
| 5 | `target:1933` | Target #1933 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 6 | `target:13357` | Target #13357 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 7 | `target:11486` | Target #11486 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000005 | 0.000005 | 0 | 3 | 0 |
| 8 | `target:7213` | Target #7213 | `unmapped_graph_id` | `target` | 5 | 5 | 0.000005 | 0.000014 | 0 | 5 | 0 |
| 9 | `target:19382` | Target #19382 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000004 | 0.000004 | 0 | 1 | 0 |
| 10 | `target:2432` | Target #2432 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000004 | 0.000006 | 0 | 3 | 0 |
| 11 | `target:1774` | Target #1774 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000003 | 0.000005 | 0 | 3 | 0 |
| 12 | `target:7260` | Target #7260 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 13 | `target:2146` | Target #2146 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 14 | `target:2586` | Target #2586 | `unmapped_graph_id` | `target` | 4 | 4 | 0.000002 | 0.000005 | 0 | 4 | 0 |
| 15 | `target:469` | Target #469 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 16 | `target:6478` | Target #6478 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 17 | `target:590` | Target #590 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 18 | `target:7938` | Target #7938 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 19 | `target:9481` | Target #9481 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 20 | `target:12639` | Target #12639 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |

## Top Component Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:761` | Compound #761 | `unmapped_graph_id` | `compound` | 3 | 3 | 0.000309 | 0.000318 | 3 | 0 | 0 |
| 2 | `compound:821` | Compound #821 | `unmapped_graph_id` | `compound` | 4 | 4 | 0.000247 | 0.000313 | 4 | 0 | 0 |
| 3 | `compound:480` | Compound #480 | `unmapped_graph_id` | `compound` | 5 | 5 | 0.000034 | 0.000041 | 0 | 5 | 0 |
| 4 | `compound:1073` | Compound #1073 | `unmapped_graph_id` | `compound` | 4 | 4 | 0.000021 | 0.000028 | 0 | 4 | 0 |
| 5 | `compound:1121` | Compound #1121 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000011 | 0.000011 | 0 | 1 | 0 |
| 6 | `compound:745` | Compound #745 | `unmapped_graph_id` | `compound` | 2 | 2 | 0.000004 | 0.000005 | 0 | 2 | 0 |
| 7 | `compound:132` | Compound #132 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 8 | `compound:1257` | Compound #1257 | `unmapped_graph_id` | `compound` | 2 | 2 | 0.000000 | 0.000000 | 0 | 2 | 0 |
| 9 | `compound:965` | Compound #965 | `unmapped_graph_id` | `compound` | 3 | 3 | 0.000000 | 0.000000 | 0 | 3 | 0 |
| 10 | `compound:435` | Compound #435 | `unmapped_graph_id` | `compound` | 3 | 3 | 0.000000 | 0.000000 | 0 | 3 | 0 |
| 11 | `compound:278` | Compound #278 | `unmapped_graph_id` | `compound` | 2 | 2 | -0.000000 | 0.000000 | 0 | 2 | 0 |
| 12 | `compound:876` | Compound #876 | `unmapped_graph_id` | `compound` | 3 | 3 | -0.000000 | 0.000000 | 0 | 3 | 0 |
| 13 | `compound:1019` | Compound #1019 | `unmapped_graph_id` | `compound` | 1 | 1 | -0.000000 | -0.000000 | 0 | 1 | 0 |
| 14 | `compound:610` | Compound #610 | `unmapped_graph_id` | `compound` | 2 | 2 | -0.000000 | -0.000000 | 0 | 2 | 0 |
| 15 | `compound:699` | Compound #699 | `unmapped_graph_id` | `compound` | 1 | 1 | -0.000000 | -0.000000 | 0 | 1 | 0 |
| 16 | `compound:613` | Compound #613 | `unmapped_graph_id` | `compound` | 3 | 3 | -0.000003 | -0.000002 | 0 | 3 | 0 |
| 17 | `compound:1023` | Compound #1023 | `unmapped_graph_id` | `compound` | 5 | 5 | -0.000003 | 0.000001 | 0 | 5 | 0 |
| 18 | `compound:1243` | Compound #1243 | `unmapped_graph_id` | `compound` | 3 | 3 | -0.000004 | 0.000001 | 0 | 3 | 0 |
| 19 | `compound:1329` | Compound #1329 | `unmapped_graph_id` | `compound` | 1 | 1 | -0.000013 | -0.000013 | 0 | 1 | 0 |
| 20 | `compound:443` | Compound #443 | `unmapped_graph_id` | `compound` | 4 | 4 | -0.000041 | -0.000033 | 0 | 4 | 0 |

## Legacy Top Path Aggregates

| Rank | Path features | Display path | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `compound:821;target:11486` | Compound #821;Target #11486 | 1 | 1 | 0.000320 | 0.000320 | 1 | 0 | 0 |
| 3 | `compound:821;target:469` | Compound #821;Target #469 | 1 | 1 | 0.000315 | 0.000315 | 1 | 0 | 0 |
| 4 | `compound:761;target:7802` | Compound #761;Target #7802 | 2 | 2 | 0.000314 | 0.000318 | 2 | 0 | 0 |
| 5 | `compound:761;target:2432` | Compound #761;Target #2432 | 1 | 1 | 0.000310 | 0.000310 | 1 | 0 | 0 |
| 6 | `compound:761;target:19336` | Compound #761;Target #19336 | 1 | 1 | 0.000300 | 0.000300 | 1 | 0 | 0 |
| 7 | `compound:821;target:19336` | Compound #821;Target #19336 | 1 | 1 | 0.000263 | 0.000263 | 1 | 0 | 0 |
| 8 | `compound:821;target:1774` | Compound #821;Target #1774 | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 9 | `compound:821;target:2586` | Compound #821;Target #2586 | 2 | 2 | 0.000210 | 0.000214 | 2 | 0 | 0 |
| 10 | `compound:1073;target:15692` | Compound #1073;Target #15692 | 1 | 1 | 0.000124 | 0.000124 | 1 | 0 | 0 |
| 11 | `compound:965;target:15692` | Compound #965;Target #15692 | 1 | 1 | 0.000102 | 0.000102 | 1 | 0 | 0 |
| 12 | `compound:1023;target:1782` | Compound #1023;Target #1782 | 1 | 1 | 0.000097 | 0.000097 | 0 | 1 | 0 |
| 13 | `compound:480;target:11486` | Compound #480;Target #11486 | 1 | 1 | 0.000046 | 0.000046 | 0 | 1 | 0 |
| 14 | `compound:480;target:7213` | Compound #480;Target #7213 | 2 | 2 | 0.000044 | 0.000044 | 0 | 2 | 0 |
| 15 | `compound:480;target:1933` | Compound #480;Target #1933 | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 16 | `compound:480;target:13438` | Compound #480;Target #13438 | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 17 | `compound:480;target:19336` | Compound #480;Target #19336 | 1 | 1 | 0.000037 | 0.000037 | 0 | 1 | 0 |
| 18 | `compound:480;target:2432` | Compound #480;Target #2432 | 1 | 1 | 0.000035 | 0.000035 | 0 | 1 | 0 |
| 19 | `compound:480;target:7938` | Compound #480;Target #7938 | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |
| 20 | `compound:480;target:2586` | Compound #480;Target #2586 | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |

## Top Node Aggregates

| Rank | Feature | Display name | Name source | Type | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 | `unmapped_graph_id` | `target` | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `compound:761` | Compound #761 | `unmapped_graph_id` | `compound` | 3 | 3 | 0.000309 | 0.000318 | 3 | 0 | 0 |
| 3 | `compound:821` | Compound #821 | `unmapped_graph_id` | `compound` | 4 | 4 | 0.000247 | 0.000313 | 4 | 0 | 0 |
| 4 | `target:1782` | Target #1782 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000096 | 0.000096 | 0 | 1 | 0 |
| 5 | `target:15692` | Target #15692 | `unmapped_graph_id` | `target` | 2 | 2 | 0.000052 | 0.000102 | 1 | 1 | 0 |
| 6 | `compound:480` | Compound #480 | `unmapped_graph_id` | `compound` | 5 | 5 | 0.000034 | 0.000041 | 0 | 5 | 0 |
| 7 | `compound:1073` | Compound #1073 | `unmapped_graph_id` | `compound` | 4 | 4 | 0.000021 | 0.000028 | 0 | 4 | 0 |
| 8 | `compound:1121` | Compound #1121 | `unmapped_graph_id` | `compound` | 1 | 1 | 0.000011 | 0.000011 | 0 | 1 | 0 |
| 9 | `target:19496` | Target #19496 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000007 | 0.000007 | 0 | 1 | 0 |
| 10 | `target:1933` | Target #1933 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 11 | `target:13357` | Target #13357 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 12 | `target:11486` | Target #11486 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000005 | 0.000005 | 0 | 3 | 0 |
| 13 | `target:7213` | Target #7213 | `unmapped_graph_id` | `target` | 5 | 5 | 0.000005 | 0.000014 | 0 | 5 | 0 |
| 14 | `target:19382` | Target #19382 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000004 | 0.000004 | 0 | 1 | 0 |
| 15 | `compound:745` | Compound #745 | `unmapped_graph_id` | `compound` | 2 | 2 | 0.000004 | 0.000005 | 0 | 2 | 0 |
| 16 | `target:2432` | Target #2432 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000004 | 0.000006 | 0 | 3 | 0 |
| 17 | `target:1774` | Target #1774 | `unmapped_graph_id` | `target` | 3 | 3 | 0.000003 | 0.000005 | 0 | 3 | 0 |
| 18 | `target:7260` | Target #7260 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 19 | `target:2146` | Target #2146 | `unmapped_graph_id` | `target` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 20 | `target:2586` | Target #2586 | `unmapped_graph_id` | `target` | 4 | 4 | 0.000002 | 0.000005 | 0 | 4 | 0 |
