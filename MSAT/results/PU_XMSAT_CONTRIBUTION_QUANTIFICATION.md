# PU-XMSAT Contribution Quantification

This report quantifies local contribution by zeroing input feature vectors for mechanism nodes or whole mechanism paths, then re-scoring the same CMM-ADR pair with the trained MSAT predictor.

- Cases quantified: 1
- Generated at: 2026-06-29T14:43:41.817720
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint perturbation sensitivity. This remains local model sensitivity, not causal or external validation.

Perturbation score drops are local sensitivity signals, not causal effects.
Negative score drops mean the score increased after masking; they should be interpreted as suppressive or non-supportive sensitivity signals, not as confirmed protective biology.

## Case 1: herb 237 -> ADR 3989

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998971
- Key subgraph nodes: 6
- Key subgraph edges: 6
- Quantified node refs: 6/6
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:1073` | `compound` | 0.998959 | 0.000013 |
| `target:7213` | `target` | 0.998966 | 0.000005 |
| `target:2586` | `target` | 0.998969 | 0.000002 |
| `target:6478` | `target` | 0.998970 | 0.000001 |
| `compound:965` | `compound` | 0.998971 | 0.000000 |
| `compound:1023` | `compound` | 0.998974 | -0.000003 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:1073`, `target:7213` | 0.998954 | 0.000018 |
| `path:8` | `compound:1073`, `target:7213` | 0.998954 | 0.000018 |
| `path:1` | `compound:1073`, `target:2586` | 0.998957 | 0.000015 |
| `path:7` | `compound:1073`, `target:2586` | 0.998957 | 0.000015 |
| `path:10` | `compound:965`, `target:7213` | 0.998966 | 0.000005 |
| `path:4` | `compound:965`, `target:7213` | 0.998966 | 0.000005 |
| `path:3` | `compound:965`, `target:2586` | 0.998969 | 0.000002 |
| `path:9` | `compound:965`, `target:2586` | 0.998969 | 0.000002 |
| `path:11` | `compound:1023`, `target:7213` | 0.998969 | 0.000002 |
| `path:5` | `compound:1023`, `target:7213` | 0.998969 | 0.000002 |
| `path:12` | `compound:1023`, `target:6478` | 0.998973 | -0.000001 |
| `path:6` | `compound:1023`, `target:6478` | 0.998973 | -0.000001 |

