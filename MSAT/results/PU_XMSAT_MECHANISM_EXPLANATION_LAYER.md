# PU-XMSAT 机制解释层完成报告

本报告把解释层产物合并为一个论文/汇报入口：关键机制子图、成分贡献、靶点贡献和机制路径贡献。

- 机制案例数: 1
- 已提取关键机制子图案例数: 1
- 完整子图节点均已量化: yes
- 正向成分贡献条目: 0
- 正向靶点贡献条目: 0
- 正向机制路径贡献条目: 0
- Near-zero 成分贡献条目: 3
- Near-zero 靶点贡献条目: 3
- Near-zero 机制路径贡献条目: 6
- 负向成分贡献条目: 0
- 负向靶点贡献条目: 0
- 负向机制路径贡献条目: 0
- Checkpoint: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint perturbation sensitivity. This remains local model sensitivity, not causal or external validation.

本报告只解释当前已量化案例中的局部扰动敏感性；不是因果效应、不是 SHAP 值、不是外部临床验证。

## 关键机制子图

| Case | Source | Key subgraph | Node coverage | Top component | Top target | Top pathway |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3989 | 6 nodes (3 components, 3 targets), 6 edges, 12 paths | 6/6 | `compound:1073 (0.000013)` | `target:7213 (0.000005)` | `path:2 (0.000018)` |

## 成分贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073` | 1 | 1 | 0.000013 | 0.000013 | 0 | 1 | 0 |
| 2 | `compound:965` | 1 | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 3 | `compound:1023` | 1 | 1 | -0.000003 | -0.000003 | 0 | 1 | 0 |

## 靶点贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:7213` | 1 | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 2 | `target:2586` | 1 | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 3 | `target:6478` | 1 | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |

## 机制路径贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073;target:7213` | 1 | 2 | 0.000018 | 0.000018 | 0 | 2 | 0 |
| 2 | `compound:1073;target:2586` | 1 | 2 | 0.000015 | 0.000015 | 0 | 2 | 0 |
| 3 | `compound:965;target:7213` | 1 | 2 | 0.000005 | 0.000005 | 0 | 2 | 0 |
| 4 | `compound:965;target:2586` | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 5 | `compound:1023;target:7213` | 1 | 2 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 6 | `compound:1023;target:6478` | 1 | 2 | -0.000001 | -0.000001 | 0 | 2 | 0 |

## 论文写作边界

- 可以写：当前已量化机制案例完成关键子图抽取，并对成分、靶点、机制路径进行局部置零扰动评分。
- 可以写：score drop 为原始预测分数减去遮蔽后分数；绝对值不超过 0.0001 的扰动归为 near-zero。
- 不要写：这些贡献是因果贡献、SHAP 归因、临床机制证明，或可自动升级外部证据等级。
