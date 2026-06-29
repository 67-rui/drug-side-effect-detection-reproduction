# PU-XMSAT Contribution Quantification

This report quantifies local contribution by zeroing input feature vectors for mechanism nodes or whole mechanism paths, then re-scoring the same CMM-ADR pair with the trained MSAT predictor.

- Cases quantified: 20
- Generated at: 2026-06-29T15:41:22.875475
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
| `path:1` | `compound:1073`, `target:2586` | 0.998957 | 0.000015 |
| `path:4` | `compound:965`, `target:7213` | 0.998966 | 0.000005 |
| `path:3` | `compound:965`, `target:2586` | 0.998969 | 0.000002 |
| `path:5` | `compound:1023`, `target:7213` | 0.998969 | 0.000002 |
| `path:6` | `compound:1023`, `target:6478` | 0.998973 | -0.000001 |

## Case 2: herb 237 -> ADR 2481

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998298
- Key subgraph nodes: 8
- Key subgraph edges: 5
- Quantified node refs: 8/8
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `target:15692` | `target` | 0.998196 | 0.000102 |
| `target:1782` | `target` | 0.998202 | 0.000096 |
| `compound:1073` | `compound` | 0.998278 | 0.000020 |
| `target:2432` | `target` | 0.998292 | 0.000006 |
| `target:19382` | `target` | 0.998293 | 0.000004 |
| `compound:1023` | `compound` | 0.998297 | 0.000001 |
| `compound:132` | `compound` | 0.998297 | 0.000000 |
| `compound:965` | `compound` | 0.998298 | 0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:1073`, `target:15692` | 0.998174 | 0.000124 |
| `path:4` | `compound:965`, `target:15692` | 0.998196 | 0.000102 |
| `path:5` | `compound:1023`, `target:1782` | 0.998201 | 0.000097 |
| `path:3` | `compound:1073`, `target:19382` | 0.998273 | 0.000024 |
| `path:1` | `compound:132`, `target:2432` | 0.998292 | 0.000006 |

## Case 3: herb 495 -> ADR 3989

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998244
- Key subgraph nodes: 3
- Key subgraph edges: 2
- Quantified node refs: 3/3
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:821` | `compound` | 0.998036 | 0.000208 |
| `target:2586` | `target` | 0.998239 | 0.000005 |
| `target:1774` | `target` | 0.998239 | 0.000005 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:821`, `target:2586` | 0.998030 | 0.000214 |
| `path:2` | `compound:821`, `target:1774` | 0.998030 | 0.000214 |

## Case 4: herb 237 -> ADR 24

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998242
- Key subgraph nodes: 3
- Key subgraph edges: 2
- Quantified node refs: 3/3
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:745` | `compound` | 0.998238 | 0.000003 |
| `target:19336` | `target` | 0.998242 | 0.000000 |
| `compound:1023` | `compound` | 0.998248 | -0.000007 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:745`, `target:19336` | 0.998238 | 0.000003 |
| `path:2` | `compound:1023`, `target:19336` | 0.998248 | -0.000007 |

## Case 5: herb 500 -> ADR 3989

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998233
- Key subgraph nodes: 3
- Key subgraph edges: 2
- Quantified node refs: 3/3
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `target:7213` | `target` | 0.998232 | 0.000001 |
| `target:1774` | `target` | 0.998233 | 0.000000 |
| `compound:610` | `compound` | 0.998233 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:610`, `target:7213` | 0.998232 | 0.000000 |
| `path:2` | `compound:610`, `target:1774` | 0.998233 | 0.000000 |

## Case 6: herb 495 -> ADR 4997

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998161
- Key subgraph nodes: 2
- Key subgraph edges: 1
- Quantified node refs: 2/2
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:821` | `compound` | 0.997957 | 0.000204 |
| `target:2586` | `target` | 0.998160 | 0.000001 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:821`, `target:2586` | 0.997956 | 0.000205 |

## Case 7: herb 237 -> ADR 2453

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998109
- Key subgraph nodes: 5
- Key subgraph edges: 4
- Quantified node refs: 5/5
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:1073` | `compound` | 0.998087 | 0.000022 |
| `compound:1121` | `compound` | 0.998099 | 0.000011 |
| `target:7260` | `target` | 0.998107 | 0.000003 |
| `target:2146` | `target` | 0.998107 | 0.000002 |
| `compound:1023` | `compound` | 0.998118 | -0.000009 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:1073`, `target:7260` | 0.998085 | 0.000025 |
| `path:2` | `compound:1121`, `target:2146` | 0.998096 | 0.000013 |
| `path:3` | `compound:1121`, `target:7260` | 0.998096 | 0.000013 |
| `path:4` | `compound:1023`, `target:7260` | 0.998116 | -0.000006 |

## Case 8: herb 237 -> ADR 3387

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.998056
- Key subgraph nodes: 3
- Key subgraph edges: 2
- Quantified node refs: 3/3
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:1073` | `compound` | 0.998028 | 0.000028 |
| `target:20703` | `target` | 0.998055 | 0.000001 |
| `target:9880` | `target` | 0.998056 | 0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:1073`, `target:20703` | 0.998027 | 0.000029 |
| `path:1` | `compound:1073`, `target:9880` | 0.998028 | 0.000028 |

## Case 9: herb 618 -> ADR 4997

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997998
- Key subgraph nodes: 12
- Key subgraph edges: 8
- Quantified node refs: 12/12
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:480` | `compound` | 0.997966 | 0.000033 |
| `target:2586` | `target` | 0.997998 | 0.000001 |
| `target:5720` | `target` | 0.997998 | 0.000001 |
| `target:974` | `target` | 0.997998 | 0.000000 |
| `target:2197` | `target` | 0.997998 | 0.000000 |
| `compound:435` | `compound` | 0.997998 | 0.000000 |
| `target:17098` | `target` | 0.997998 | 0.000000 |
| `compound:278` | `compound` | 0.997999 | -0.000000 |
| `compound:876` | `compound` | 0.997999 | -0.000000 |
| `target:4` | `target` | 0.997999 | -0.000000 |
| `compound:613` | `compound` | 0.998001 | -0.000002 |
| `compound:443` | `compound` | 0.998032 | -0.000034 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:480`, `target:2586` | 0.997965 | 0.000034 |
| `path:1` | `compound:480`, `target:17098` | 0.997965 | 0.000033 |
| `path:5` | `compound:435`, `target:974` | 0.997998 | 0.000001 |
| `path:4` | `compound:876`, `target:5720` | 0.997998 | 0.000000 |
| `path:6` | `compound:278`, `target:4` | 0.997999 | -0.000000 |
| `path:3` | `compound:613`, `target:17098` | 0.998001 | -0.000002 |
| `path:8` | `compound:443`, `target:2197` | 0.998032 | -0.000033 |
| `path:7` | `compound:443`, `target:4` | 0.998032 | -0.000034 |

## Case 10: herb 618 -> ADR 3989

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997913
- Key subgraph nodes: 8
- Key subgraph edges: 8
- Quantified node refs: 8/8
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:480` | `compound` | 0.997880 | 0.000032 |
| `target:1933` | `target` | 0.997907 | 0.000005 |
| `target:1774` | `target` | 0.997907 | 0.000005 |
| `compound:1243` | `compound` | 0.997911 | 0.000001 |
| `target:7938` | `target` | 0.997911 | 0.000001 |
| `compound:1257` | `compound` | 0.997912 | 0.000000 |
| `compound:876` | `compound` | 0.997913 | 0.000000 |
| `compound:613` | `compound` | 0.997915 | -0.000002 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:480`, `target:1933` | 0.997875 | 0.000038 |
| `path:1` | `compound:480`, `target:7938` | 0.997879 | 0.000034 |
| `path:8` | `compound:1243`, `target:1933` | 0.997906 | 0.000007 |
| `path:5` | `compound:1257`, `target:1933` | 0.997907 | 0.000006 |
| `path:7` | `compound:876`, `target:1933` | 0.997907 | 0.000005 |
| `path:3` | `compound:613`, `target:1933` | 0.997910 | 0.000003 |
| `path:4` | `compound:613`, `target:1774` | 0.997910 | 0.000003 |
| `path:6` | `compound:876`, `target:7938` | 0.997911 | 0.000001 |

## Case 11: herb 237 -> ADR 2540

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997768
- Key subgraph nodes: 7
- Key subgraph edges: 5
- Quantified node refs: 7/7
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:745` | `compound` | 0.997764 | 0.000005 |
| `compound:1023` | `compound` | 0.997767 | 0.000001 |
| `compound:965` | `compound` | 0.997768 | 0.000000 |
| `target:14492` | `target` | 0.997768 | -0.000000 |
| `target:6814` | `target` | 0.997768 | -0.000000 |
| `target:13438` | `target` | 0.997769 | -0.000000 |
| `target:19336` | `target` | 0.997769 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:3` | `compound:745`, `target:19336` | 0.997764 | 0.000005 |
| `path:4` | `compound:1023`, `target:19336` | 0.997767 | 0.000001 |
| `path:5` | `compound:1023`, `target:13438` | 0.997767 | 0.000001 |
| `path:1` | `compound:965`, `target:14492` | 0.997768 | 0.000000 |
| `path:2` | `compound:965`, `target:6814` | 0.997768 | 0.000000 |

## Case 12: herb 373 -> ADR 4230

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997757
- Key subgraph nodes: 2
- Key subgraph edges: 1
- Quantified node refs: 2/2
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:761` | `compound` | 0.997439 | 0.000318 |
| `target:7802` | `target` | 0.997758 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:761`, `target:7802` | 0.997440 | 0.000318 |

## Case 13: herb 495 -> ADR 1810

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997630
- Key subgraph nodes: 2
- Key subgraph edges: 1
- Quantified node refs: 2/2
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:821` | `compound` | 0.997368 | 0.000262 |
| `target:19336` | `target` | 0.997629 | 0.000001 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:821`, `target:19336` | 0.997367 | 0.000263 |

## Case 14: herb 500 -> ADR 5468

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997626
- Key subgraph nodes: 2
- Key subgraph edges: 1
- Quantified node refs: 2/2
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `target:11486` | `target` | 0.997622 | 0.000004 |
| `compound:610` | `compound` | 0.997626 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `compound:610`, `target:11486` | 0.997623 | 0.000004 |

## Case 15: herb 373 -> ADR 2931

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997507
- Key subgraph nodes: 9
- Key subgraph edges: 4
- Quantified node refs: 9/9
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `target:15721` | `target` | 0.996333 | 0.001174 |
| `compound:761` | `compound` | 0.997197 | 0.000310 |
| `target:7802` | `target` | 0.997507 | 0.000000 |
| `target:10658` | `target` | 0.997507 | 0.000000 |
| `target:18046` | `target` | 0.997507 | 0.000000 |
| `target:7213` | `target` | 0.997507 | 0.000000 |
| `target:7684` | `target` | 0.997507 | 0.000000 |
| `compound:1019` | `compound` | 0.997507 | -0.000000 |
| `target:2432` | `target` | 0.997507 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:1` | `target:15721` | 0.996333 | 0.001174 |
| `path:7` | `compound:761`, `target:7802` | 0.997196 | 0.000311 |
| `path:6` | `compound:761`, `target:2432` | 0.997197 | 0.000310 |
| `path:2` | `target:10658` | 0.997507 | 0.000000 |
| `path:3` | `target:7684` | 0.997507 | 0.000000 |
| `path:4` | `compound:1019`, `target:7213` | 0.997507 | -0.000000 |
| `path:5` | `compound:1019`, `target:18046` | 0.997507 | -0.000000 |

## Case 16: herb 495 -> ADR 2095

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997488
- Key subgraph nodes: 3
- Key subgraph edges: 2
- Quantified node refs: 3/3
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:821` | `compound` | 0.997175 | 0.000313 |
| `target:11486` | `target` | 0.997483 | 0.000005 |
| `target:469` | `target` | 0.997486 | 0.000002 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:821`, `target:11486` | 0.997168 | 0.000320 |
| `path:1` | `compound:821`, `target:469` | 0.997173 | 0.000315 |

## Case 17: herb 618 -> ADR 1810

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997476
- Key subgraph nodes: 9
- Key subgraph edges: 8
- Quantified node refs: 9/9
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:480` | `compound` | 0.997440 | 0.000036 |
| `target:13438` | `target` | 0.997475 | 0.000001 |
| `target:9481` | `target` | 0.997475 | 0.000001 |
| `target:19336` | `target` | 0.997475 | 0.000001 |
| `compound:1257` | `compound` | 0.997476 | 0.000000 |
| `compound:435` | `compound` | 0.997476 | 0.000000 |
| `compound:876` | `compound` | 0.997476 | -0.000000 |
| `compound:1243` | `compound` | 0.997477 | -0.000001 |
| `compound:443` | `compound` | 0.997520 | -0.000044 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:480`, `target:13438` | 0.997438 | 0.000038 |
| `path:1` | `compound:480`, `target:19336` | 0.997438 | 0.000037 |
| `path:3` | `compound:1257`, `target:19336` | 0.997474 | 0.000001 |
| `path:6` | `compound:435`, `target:19336` | 0.997475 | 0.000001 |
| `path:4` | `compound:876`, `target:19336` | 0.997475 | 0.000001 |
| `path:5` | `compound:1243`, `target:19336` | 0.997476 | 0.000000 |
| `path:8` | `compound:443`, `target:9481` | 0.997519 | -0.000043 |
| `path:7` | `compound:443`, `target:19336` | 0.997519 | -0.000043 |

## Case 18: herb 618 -> ADR 2095

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997471
- Key subgraph nodes: 9
- Key subgraph edges: 8
- Quantified node refs: 9/9
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:480` | `compound` | 0.997430 | 0.000041 |
| `target:11486` | `target` | 0.997466 | 0.000005 |
| `target:7213` | `target` | 0.997467 | 0.000003 |
| `target:15692` | `target` | 0.997469 | 0.000002 |
| `target:590` | `target` | 0.997469 | 0.000001 |
| `target:20366` | `target` | 0.997470 | 0.000000 |
| `compound:435` | `compound` | 0.997470 | 0.000000 |
| `compound:278` | `compound` | 0.997471 | 0.000000 |
| `compound:443` | `compound` | 0.997504 | -0.000033 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:2` | `compound:480`, `target:11486` | 0.997425 | 0.000046 |
| `path:1` | `compound:480`, `target:7213` | 0.997426 | 0.000044 |
| `path:3` | `compound:435`, `target:11486` | 0.997465 | 0.000005 |
| `path:5` | `compound:278`, `target:11486` | 0.997466 | 0.000005 |
| `path:4` | `compound:435`, `target:590` | 0.997469 | 0.000002 |
| `path:6` | `compound:278`, `target:20366` | 0.997470 | 0.000000 |
| `path:8` | `compound:443`, `target:7213` | 0.997501 | -0.000030 |
| `path:7` | `compound:443`, `target:15692` | 0.997502 | -0.000032 |

## Case 19: herb 618 -> ADR 4759

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997356
- Key subgraph nodes: 10
- Key subgraph edges: 7
- Quantified node refs: 10/10
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:480` | `compound` | 0.997326 | 0.000030 |
| `target:7213` | `target` | 0.997342 | 0.000014 |
| `target:19496` | `target` | 0.997349 | 0.000007 |
| `target:2432` | `target` | 0.997351 | 0.000005 |
| `target:13357` | `target` | 0.997352 | 0.000005 |
| `target:12639` | `target` | 0.997356 | 0.000001 |
| `compound:613` | `compound` | 0.997360 | -0.000004 |
| `compound:1243` | `compound` | 0.997369 | -0.000013 |
| `compound:1329` | `compound` | 0.997369 | -0.000013 |
| `compound:443` | `compound` | 0.997409 | -0.000053 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:3` | `compound:480`, `target:7213` | 0.997312 | 0.000044 |
| `path:2` | `compound:480`, `target:2432` | 0.997321 | 0.000035 |
| `path:1` | `target:13357` | 0.997352 | 0.000005 |
| `path:4` | `compound:613`, `target:19496` | 0.997353 | 0.000003 |
| `path:7` | `compound:1329`, `target:19496` | 0.997362 | -0.000005 |
| `path:5` | `compound:1243`, `target:19496` | 0.997362 | -0.000005 |
| `path:6` | `compound:1243`, `target:12639` | 0.997368 | -0.000012 |
| `path:8` | `compound:443`, `target:19496` | 0.997402 | -0.000046 |

## Case 20: herb 373 -> ADR 1155

- Source: `pu_xmsat_global_unobserved_pairs`
- Original score: 0.997344
- Key subgraph nodes: 6
- Key subgraph edges: 2
- Quantified node refs: 6/6
- Node refs truncated: no

### Node Contributions

| Feature | Type | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `compound:761` | `compound` | 0.997045 | 0.000298 |
| `target:19336` | `target` | 0.997342 | 0.000001 |
| `target:19817` | `target` | 0.997344 | 0.000000 |
| `target:5663` | `target` | 0.997344 | 0.000000 |
| `compound:699` | `compound` | 0.997344 | -0.000000 |
| `target:2606` | `target` | 0.997344 | -0.000000 |

### Path Contributions

| Path | Features | Masked score | Score drop |
| --- | --- | ---: | ---: |
| `path:4` | `compound:761`, `target:19336` | 0.997044 | 0.000300 |
| `path:5` | `compound:699`, `target:19336` | 0.997343 | 0.000001 |
| `path:1` | `target:19817` | 0.997344 | 0.000000 |
| `path:3` | `target:5663` | 0.997344 | 0.000000 |
| `path:2` | `target:2606` | 0.997344 | -0.000000 |
