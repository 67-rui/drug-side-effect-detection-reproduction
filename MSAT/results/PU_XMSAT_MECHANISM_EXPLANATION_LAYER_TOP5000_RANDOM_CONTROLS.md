# PU-XMSAT 机制解释层完成报告

本报告把解释层产物合并为一个论文/汇报入口：关键机制子图、成分贡献、靶点贡献和机制路径贡献。

- 机制案例数: 20
- 已提取关键机制子图案例数: 20
- 完整子图节点均已量化: yes
- 正向成分贡献条目: 2
- 正向靶点贡献条目: 2
- 正向机制路径贡献条目: 11
- Near-zero 成分贡献条目: 18
- Near-zero 靶点贡献条目: 19
- Near-zero 机制路径贡献条目: 9
- 负向成分贡献条目: 0
- 负向靶点贡献条目: 0
- 负向机制路径贡献条目: 0
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint perturbation sensitivity. This remains local model sensitivity, not causal or external validation.

本报告只解释当前已量化案例中的局部扰动敏感性；不是因果效应、不是 SHAP 值、不是外部临床验证。

## 关键机制子图

| Case | Source | Key subgraph | Node coverage | Top component | Top target | Top pathway |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3989 | 6 nodes (3 components, 3 targets), 6 edges, 6 paths | 6/6 | `Compound #1073 (0.000013)` | `Target #7213 (0.000005)` | `path:2 (0.000018)` |
| 2 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2481 | 8 nodes (4 components, 4 targets), 5 edges, 5 paths | 8/8 | `Compound #1073 (0.000020)` | `Target #15692 (0.000102)` | `path:2 (0.000124)` |
| 3 | `pu_xmsat_global_unobserved_pairs` herb 495 -> ADR 3989 | 3 nodes (1 components, 2 targets), 2 edges, 2 paths | 3/3 | `Compound #821 (0.000208)` | `Target #2586 (0.000005)` | `path:1 (0.000214)` |
| 4 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 24 | 3 nodes (2 components, 1 targets), 2 edges, 2 paths | 3/3 | `Compound #745 (0.000003)` | `Target #19336 (0.000000)` | `path:1 (0.000003)` |
| 5 | `pu_xmsat_global_unobserved_pairs` herb 500 -> ADR 3989 | 3 nodes (1 components, 2 targets), 2 edges, 2 paths | 3/3 | `Compound #610 (-0.000000)` | `Target #7213 (0.000001)` | `path:1 (0.000000)` |
| 6 | `pu_xmsat_global_unobserved_pairs` herb 495 -> ADR 4997 | 2 nodes (1 components, 1 targets), 1 edges, 1 paths | 2/2 | `Compound #821 (0.000204)` | `Target #2586 (0.000001)` | `path:1 (0.000205)` |
| 7 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2453 | 5 nodes (3 components, 2 targets), 4 edges, 4 paths | 5/5 | `Compound #1073 (0.000022)` | `Target #7260 (0.000003)` | `path:1 (0.000025)` |
| 8 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3387 | 3 nodes (1 components, 2 targets), 2 edges, 2 paths | 3/3 | `Compound #1073 (0.000028)` | `Target #20703 (0.000001)` | `path:2 (0.000029)` |
| 9 | `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 4997 | 12 nodes (6 components, 6 targets), 8 edges, 8 paths | 12/12 | `Compound #480 (0.000033)` | `Target #2586 (0.000001)` | `path:2 (0.000034)` |
| 10 | `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 3989 | 8 nodes (5 components, 3 targets), 8 edges, 8 paths | 8/8 | `Compound #480 (0.000032)` | `Target #1933 (0.000005)` | `path:2 (0.000038)` |
| 11 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2540 | 7 nodes (3 components, 4 targets), 5 edges, 5 paths | 7/7 | `Compound #745 (0.000005)` | `Target #14492 (-0.000000)` | `path:3 (0.000005)` |
| 12 | `pu_xmsat_global_unobserved_pairs` herb 373 -> ADR 4230 | 2 nodes (1 components, 1 targets), 1 edges, 1 paths | 2/2 | `Compound #761 (0.000318)` | `Target #7802 (-0.000000)` | `path:1 (0.000318)` |
| 13 | `pu_xmsat_global_unobserved_pairs` herb 495 -> ADR 1810 | 2 nodes (1 components, 1 targets), 1 edges, 1 paths | 2/2 | `Compound #821 (0.000262)` | `Target #19336 (0.000001)` | `path:1 (0.000263)` |
| 14 | `pu_xmsat_global_unobserved_pairs` herb 500 -> ADR 5468 | 2 nodes (1 components, 1 targets), 1 edges, 1 paths | 2/2 | `Compound #610 (-0.000000)` | `Target #11486 (0.000004)` | `path:1 (0.000004)` |
| 15 | `pu_xmsat_global_unobserved_pairs` herb 373 -> ADR 2931 | 9 nodes (2 components, 7 targets), 4 edges, 7 paths | 9/9 | `Compound #761 (0.000310)` | `Target #15721 (0.001174)` | `path:1 (0.001174)` |
| 16 | `pu_xmsat_global_unobserved_pairs` herb 495 -> ADR 2095 | 3 nodes (1 components, 2 targets), 2 edges, 2 paths | 3/3 | `Compound #821 (0.000313)` | `Target #11486 (0.000005)` | `path:2 (0.000320)` |
| 17 | `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 1810 | 9 nodes (6 components, 3 targets), 8 edges, 8 paths | 9/9 | `Compound #480 (0.000036)` | `Target #13438 (0.000001)` | `path:2 (0.000038)` |
| 18 | `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 2095 | 9 nodes (4 components, 5 targets), 8 edges, 8 paths | 9/9 | `Compound #480 (0.000041)` | `Target #11486 (0.000005)` | `path:2 (0.000046)` |
| 19 | `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 4759 | 10 nodes (5 components, 5 targets), 7 edges, 8 paths | 10/10 | `Compound #480 (0.000030)` | `Target #7213 (0.000014)` | `path:3 (0.000044)` |
| 20 | `pu_xmsat_global_unobserved_pairs` herb 373 -> ADR 1155 | 6 nodes (2 components, 4 targets), 2 edges, 5 paths | 6/6 | `Compound #761 (0.000298)` | `Target #19336 (0.000001)` | `path:4 (0.000300)` |

## 成分贡献

| Rank | Feature | Display | Source | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:761` | Compound #761 | unmapped_graph_id | 3 | 3 | 0.000309 | 0.000318 | 3 | 0 | 0 |
| 2 | `compound:821` | Compound #821 | unmapped_graph_id | 4 | 4 | 0.000247 | 0.000313 | 4 | 0 | 0 |
| 3 | `compound:480` | Compound #480 | unmapped_graph_id | 5 | 5 | 0.000034 | 0.000041 | 0 | 5 | 0 |
| 4 | `compound:1073` | Compound #1073 | unmapped_graph_id | 4 | 4 | 0.000021 | 0.000028 | 0 | 4 | 0 |
| 5 | `compound:1121` | Compound #1121 | unmapped_graph_id | 1 | 1 | 0.000011 | 0.000011 | 0 | 1 | 0 |
| 6 | `compound:745` | Compound #745 | unmapped_graph_id | 2 | 2 | 0.000004 | 0.000005 | 0 | 2 | 0 |
| 7 | `compound:132` | Compound #132 | unmapped_graph_id | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 8 | `compound:1257` | Compound #1257 | unmapped_graph_id | 2 | 2 | 0.000000 | 0.000000 | 0 | 2 | 0 |
| 9 | `compound:965` | Compound #965 | unmapped_graph_id | 3 | 3 | 0.000000 | 0.000000 | 0 | 3 | 0 |
| 10 | `compound:435` | Compound #435 | unmapped_graph_id | 3 | 3 | 0.000000 | 0.000000 | 0 | 3 | 0 |
| 11 | `compound:278` | Compound #278 | unmapped_graph_id | 2 | 2 | -0.000000 | 0.000000 | 0 | 2 | 0 |
| 12 | `compound:876` | Compound #876 | unmapped_graph_id | 3 | 3 | -0.000000 | 0.000000 | 0 | 3 | 0 |
| 13 | `compound:1019` | Compound #1019 | unmapped_graph_id | 1 | 1 | -0.000000 | -0.000000 | 0 | 1 | 0 |
| 14 | `compound:610` | Compound #610 | unmapped_graph_id | 2 | 2 | -0.000000 | -0.000000 | 0 | 2 | 0 |
| 15 | `compound:699` | Compound #699 | unmapped_graph_id | 1 | 1 | -0.000000 | -0.000000 | 0 | 1 | 0 |
| 16 | `compound:613` | Compound #613 | unmapped_graph_id | 3 | 3 | -0.000003 | -0.000002 | 0 | 3 | 0 |
| 17 | `compound:1023` | Compound #1023 | unmapped_graph_id | 5 | 5 | -0.000003 | 0.000001 | 0 | 5 | 0 |
| 18 | `compound:1243` | Compound #1243 | unmapped_graph_id | 3 | 3 | -0.000004 | 0.000001 | 0 | 3 | 0 |
| 19 | `compound:1329` | Compound #1329 | unmapped_graph_id | 1 | 1 | -0.000013 | -0.000013 | 0 | 1 | 0 |
| 20 | `compound:443` | Compound #443 | unmapped_graph_id | 4 | 4 | -0.000041 | -0.000033 | 0 | 4 | 0 |

## 靶点贡献

| Rank | Feature | Display | Source | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 | unmapped_graph_id | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `target:1782` | Target #1782 | unmapped_graph_id | 1 | 1 | 0.000096 | 0.000096 | 0 | 1 | 0 |
| 3 | `target:15692` | Target #15692 | unmapped_graph_id | 2 | 2 | 0.000052 | 0.000102 | 1 | 1 | 0 |
| 4 | `target:19496` | Target #19496 | unmapped_graph_id | 1 | 1 | 0.000007 | 0.000007 | 0 | 1 | 0 |
| 5 | `target:1933` | Target #1933 | unmapped_graph_id | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 6 | `target:13357` | Target #13357 | unmapped_graph_id | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 7 | `target:11486` | Target #11486 | unmapped_graph_id | 3 | 3 | 0.000005 | 0.000005 | 0 | 3 | 0 |
| 8 | `target:7213` | Target #7213 | unmapped_graph_id | 5 | 5 | 0.000005 | 0.000014 | 0 | 5 | 0 |
| 9 | `target:19382` | Target #19382 | unmapped_graph_id | 1 | 1 | 0.000004 | 0.000004 | 0 | 1 | 0 |
| 10 | `target:2432` | Target #2432 | unmapped_graph_id | 3 | 3 | 0.000004 | 0.000006 | 0 | 3 | 0 |
| 11 | `target:1774` | Target #1774 | unmapped_graph_id | 3 | 3 | 0.000003 | 0.000005 | 0 | 3 | 0 |
| 12 | `target:7260` | Target #7260 | unmapped_graph_id | 1 | 1 | 0.000003 | 0.000003 | 0 | 1 | 0 |
| 13 | `target:2146` | Target #2146 | unmapped_graph_id | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 14 | `target:2586` | Target #2586 | unmapped_graph_id | 4 | 4 | 0.000002 | 0.000005 | 0 | 4 | 0 |
| 15 | `target:469` | Target #469 | unmapped_graph_id | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 16 | `target:6478` | Target #6478 | unmapped_graph_id | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 17 | `target:590` | Target #590 | unmapped_graph_id | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 18 | `target:7938` | Target #7938 | unmapped_graph_id | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 19 | `target:9481` | Target #9481 | unmapped_graph_id | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |
| 20 | `target:12639` | Target #12639 | unmapped_graph_id | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |

## 机制路径贡献

| Rank | Feature | Display | Source | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` | Target #15721 |  | 1 | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `compound:821;target:11486` | Compound #821;Target #11486 |  | 1 | 1 | 0.000320 | 0.000320 | 1 | 0 | 0 |
| 3 | `compound:821;target:469` | Compound #821;Target #469 |  | 1 | 1 | 0.000315 | 0.000315 | 1 | 0 | 0 |
| 4 | `compound:761;target:7802` | Compound #761;Target #7802 |  | 2 | 2 | 0.000314 | 0.000318 | 2 | 0 | 0 |
| 5 | `compound:761;target:2432` | Compound #761;Target #2432 |  | 1 | 1 | 0.000310 | 0.000310 | 1 | 0 | 0 |
| 6 | `compound:761;target:19336` | Compound #761;Target #19336 |  | 1 | 1 | 0.000300 | 0.000300 | 1 | 0 | 0 |
| 7 | `compound:821;target:19336` | Compound #821;Target #19336 |  | 1 | 1 | 0.000263 | 0.000263 | 1 | 0 | 0 |
| 8 | `compound:821;target:1774` | Compound #821;Target #1774 |  | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 9 | `compound:821;target:2586` | Compound #821;Target #2586 |  | 2 | 2 | 0.000210 | 0.000214 | 2 | 0 | 0 |
| 10 | `compound:1073;target:15692` | Compound #1073;Target #15692 |  | 1 | 1 | 0.000124 | 0.000124 | 1 | 0 | 0 |
| 11 | `compound:965;target:15692` | Compound #965;Target #15692 |  | 1 | 1 | 0.000102 | 0.000102 | 1 | 0 | 0 |
| 12 | `compound:1023;target:1782` | Compound #1023;Target #1782 |  | 1 | 1 | 0.000097 | 0.000097 | 0 | 1 | 0 |
| 13 | `compound:480;target:11486` | Compound #480;Target #11486 |  | 1 | 1 | 0.000046 | 0.000046 | 0 | 1 | 0 |
| 14 | `compound:480;target:7213` | Compound #480;Target #7213 |  | 2 | 2 | 0.000044 | 0.000044 | 0 | 2 | 0 |
| 15 | `compound:480;target:1933` | Compound #480;Target #1933 |  | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 16 | `compound:480;target:13438` | Compound #480;Target #13438 |  | 1 | 1 | 0.000038 | 0.000038 | 0 | 1 | 0 |
| 17 | `compound:480;target:19336` | Compound #480;Target #19336 |  | 1 | 1 | 0.000037 | 0.000037 | 0 | 1 | 0 |
| 18 | `compound:480;target:2432` | Compound #480;Target #2432 |  | 1 | 1 | 0.000035 | 0.000035 | 0 | 1 | 0 |
| 19 | `compound:480;target:7938` | Compound #480;Target #7938 |  | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |
| 20 | `compound:480;target:2586` | Compound #480;Target #2586 |  | 1 | 1 | 0.000034 | 0.000034 | 0 | 1 | 0 |

## 论文写作边界

- 可以写：当前已量化机制案例完成关键子图抽取，并对成分、靶点、机制路径进行局部置零扰动评分。
- 可以写：score drop 为原始预测分数减去遮蔽后分数；绝对值不超过 0.0001 的扰动归为 near-zero。
- 不要写：这些贡献是因果贡献、SHAP 归因、临床机制证明，或可自动升级外部证据等级。
