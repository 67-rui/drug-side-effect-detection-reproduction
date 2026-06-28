# PU-XMSAT Contribution Quantification

This report quantifies local contribution by zeroing input feature vectors for mechanism nodes or whole mechanism paths, then re-scoring the same CMM-ADR pair with the trained MSAT predictor.

- Cases quantified: 2
- Generated at: 2026-06-28T21:24:20.279254
- Checkpoint: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Checkpoint context: Local predictor checkpoint sensitivity analysis. This is not final full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint is exported and used.

Perturbation score drops are local sensitivity signals, not causal effects.
Negative score drops mean the score increased after masking; they should be interpreted as suppressive or non-supportive sensitivity signals, not as confirmed protective biology.

## Case 1: herb 277 -> ADR 2931

- Source: `case_zhishi_diarrhoea`
- Original score: 0.476290
- Key subgraph nodes: 11
- Key subgraph edges: 8

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `target:3223` | `target` | 0.466455 | 0.009835 |
| `compound:523` | `compound` | 0.476051 | 0.000239 |
| `target:8101` | `target` | 0.476218 | 0.000071 |
| `target:12337` | `target` | 0.476262 | 0.000028 |
| `target:8967` | `target` | 0.476262 | 0.000028 |
| `target:7802` | `target` | 0.476288 | 0.000002 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:4` | `compound:523`, `target:3223` | 0.466216 | 0.010074 |
| `path:13` | `compound:435`, `target:8101` | 0.476005 | 0.000285 |
| `path:5` | `compound:523`, `target:12337` | 0.476023 | 0.000267 |
| `path:9` | `compound:523`, `target:12337` | 0.476023 | 0.000267 |
| `path:14` | `compound:435`, `target:8967` | 0.476048 | 0.000241 |
| `path:10` | `compound:523`, `target:7802` | 0.476049 | 0.000241 |
| `path:3` | `compound:523`, `target:7802` | 0.476049 | 0.000241 |
| `path:2` | `target:8101` | 0.476218 | 0.000071 |
| `path:1` | `target:8967` | 0.476262 | 0.000028 |
| `path:11` | `compound:875`, `target:2432` | 0.481726 | -0.005437 |
| `path:6` | `compound:875`, `target:2432` | 0.481726 | -0.005437 |
| `path:8` | `compound:875`, `target:12333` | 0.481729 | -0.005439 |
| `path:12` | `compound:875`, `target:14208` | 0.481732 | -0.005442 |
| `path:7` | `compound:875`, `target:14208` | 0.481732 | -0.005442 |

## Case 2: herb 237 -> ADR 3989

- Source: `table5_top15`
- Original score: 0.999185
- Key subgraph nodes: 2
- Key subgraph edges: 1

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:1073` | `compound` | 0.999164 | 0.000021 |
| `target:2586` | `target` | 0.999185 | 0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:1073`, `target:2586` | 0.999164 | 0.000021 |

