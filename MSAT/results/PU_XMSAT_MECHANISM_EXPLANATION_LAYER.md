# PU-XMSAT 机制解释层完成报告

本报告把解释层产物合并为一个论文/汇报入口：关键机制子图、成分贡献、靶点贡献和机制路径贡献。

- 机制案例数: 2
- 已提取关键机制子图案例数: 2
- 完整子图节点均已量化: yes
- 正向成分贡献条目: 3
- 正向靶点贡献条目: 8
- 正向机制路径贡献条目: 8
- Checkpoint: `/Users/a67_2024/Desktop/drug-detect/MSAT/saved_models/best_model_for_prediction.pt`
- Checkpoint context: Local predictor checkpoint sensitivity analysis. This is not final full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint is exported and used.

本报告只解释当前已量化案例中的局部扰动敏感性；不是因果效应、不是 SHAP 值、不是外部临床验证。

## 关键机制子图

| Case | Source | Key subgraph | Node coverage | Top component | Top target | Top pathway |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `case_zhishi_diarrhoea` herb 277 -> ADR 2931 | 11 nodes (3 components, 8 targets), 8 edges, 14 paths | 11/11 | `compound:523 (0.000239)` | `target:3223 (0.009835)` | `path:4 (0.010074)` |
| 2 | `table5_top15` herb 237 -> ADR 3989 | 2 nodes (1 components, 1 targets), 1 edges, 1 paths | 2/2 | `compound:1073 (0.000021)` | `target:2586 (0.000000)` | `path:1 (0.000021)` |

## 成分贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:523` | 1 | 1 | 0.000239 | 0.000239 | 1 | 0 |
| 2 | `compound:435` | 1 | 1 | 0.000214 | 0.000214 | 1 | 0 |
| 3 | `compound:1073` | 1 | 1 | 0.000021 | 0.000021 | 1 | 0 |
| 4 | `compound:875` | 1 | 1 | -0.005442 | -0.005442 | 0 | 1 |

## 靶点贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:3223` | 1 | 1 | 0.009835 | 0.009835 | 1 | 0 |
| 2 | `target:8101` | 1 | 1 | 0.000071 | 0.000071 | 1 | 0 |
| 3 | `target:12337` | 1 | 1 | 0.000028 | 0.000028 | 1 | 0 |
| 4 | `target:8967` | 1 | 1 | 0.000028 | 0.000028 | 1 | 0 |
| 5 | `target:2432` | 1 | 1 | 0.000006 | 0.000006 | 1 | 0 |
| 6 | `target:12333` | 1 | 1 | 0.000003 | 0.000003 | 1 | 0 |
| 7 | `target:7802` | 1 | 1 | 0.000002 | 0.000002 | 1 | 0 |
| 8 | `target:14208` | 1 | 1 | 0.000000 | 0.000000 | 1 | 0 |
| 9 | `target:2586` | 1 | 1 | 0.000000 | 0.000000 | 0 | 0 |

## 机制路径贡献

| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |
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

## 论文写作边界

- 可以写：当前两个机制案例均完成关键子图抽取，并对成分、靶点、机制路径进行局部置零扰动评分。
- 可以写：score drop 为原始预测分数减去遮蔽后分数，正值表示遮蔽后模型分数下降。
- 不要写：这些贡献是因果贡献、SHAP 归因、临床机制证明，或最终 PU checkpoint 的严格归因。
