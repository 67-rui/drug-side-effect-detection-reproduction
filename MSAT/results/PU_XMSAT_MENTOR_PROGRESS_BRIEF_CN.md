# PU-XMSAT 阶段性研究进展汇报

**日期：** 2026-06-27
**分支：** `codex/pu-xmsat-implementation`
**定位：** 面向导师沟通的阶段性汇报草稿，用于说明当前 MSAT 复现完成度、PU-XMSAT 改进动机、已完成实验结果和下一步研究方向。

## 1. 当前项目进展概述

本项目最初目标是复现 MSAT 论文中关于中药-不良反应预测的主要实验结果，并在复现基础上寻找可解释、可继续发展的模型改进方向。当前项目已经完成 MSAT 主实验复现与协议核对，结果目录审计显示 `issues: []`，主实验协议版本为 `2026-06-23-val-test-edge-hidden`。该协议已避免验证集和测试集正样本边进入训练图，因而更符合归纳式评估要求。

复现得到的 MSAT 主实验基线为：

| 模型 | AUC | AUPRC | F1 | MCC |
| --- | ---: | ---: | ---: | ---: |
| MSAT reproduced baseline | 0.979271 | 0.977095 | 0.931451 | 0.862520 |

Table 5 和 Table 6 当前不作为主实验复现结论。它们更接近外部验证与解释性案例分析：Table 5 依赖作者未完全公开的候选生成、checkpoint 和证据筛选流程；Table 6 又依赖 Table 5 候选。因此当前应表述为“主实验与多数核心性能结果已复现，Table 5/6 在公开材料下无法论文等价复现”，不应声称 Table 5/6 已完整复现。

## 2. PU-XMSAT 的研究动机

在复现过程中，一个核心方法问题逐渐显现：原始二分类训练通常会将未观测到的中药-不良反应配对当作负样本，但在药物警戒场景中，“未观测”并不等于“无关联”。这种处理方式可能引入负样本标签噪声，尤其是在不良反应上报不完整、适应症偏倚、合并用药和人群暴露差异等因素存在时。

因此，本项目在 MSAT 复现基础上提出 PU-XMSAT，将训练配对划分为三类：

1. 观测到的正样本；
2. 经过候选评分筛选出的可靠负样本；
3. 仍保留不确定性的未标注样本。

PU-XMSAT 保留 MSAT 的图结构、10 折划分和训练后端，只改变监督配对构造与样本权重。未标注样本仍进入训练，但使用较低权重，以降低“未观测即负样本”的噪声影响。

## 3. 当前已完成的 PU-XMSAT 实验

目前已经完成 corrected random-cache、full-positive pair budget 下的 PU-XMSAT 主要对照实验。关键设置如下：

| 设置项 | 当前采用方案 |
| --- | --- |
| 训练后端 | `full_msat_pu` |
| 可靠负样本策略 | `hybrid` 为主，`random` 作为对照 |
| 候选缓存 | corrected randomized `random50k` |
| 配对规模 | full-positive `66,015` pairs / fold |
| 阈值选择 | validation-F1-selected threshold |
| 默认 PU 权重 | `unlabeled_weight=0.2`, `reliable_negative_weight=0.8` |

随机可靠负样本策略可以达到与 MSAT 基线接近的水平，但 paired fold-level t-test 未显示稳定显著优势。因此 random PU-XMSAT 更适合作为可行性与消融对照。

机制感知的 `hybrid` 策略是当前最强结果。该策略综合 baseline prediction score、图结构支持、与已知正样本的相似性、不良反应频率以及机制相关标志，选择更可靠的负样本。

## 4. 主要结果

### 4.1 MSAT 与 PU-XMSAT 主结果

| Setting | Seed | AUC | AUPRC | F1 | MCC | 解释 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| MSAT reproduced baseline | 42 | 0.979271 | 0.977095 | 0.931451 | 0.862520 | 复现基线 |
| PU-XMSAT random full-positive | 42 | 0.979617 | 0.977273 | 0.932120 | 0.862509 | PU 可行性结果 |
| PU-XMSAT random full-positive | 2026 | 0.979732 | 0.977662 | 0.933776 | 0.866051 | random 稳健性复跑 |
| PU-XMSAT hybrid full-positive | 2026 | 0.980420 | 0.977929 | 0.935064 | 0.868409 | 当前最强单次结果 |
| PU-XMSAT hybrid full-positive | 1337 | 0.980392 | 0.977983 | 0.934767 | 0.868331 | seed 稳健性结果 |

### 4.2 Hybrid PU-XMSAT 相对 MSAT 的提升

| 对比 | 指标 | 均值提升 | Paired t-test p | 解释 |
| --- | --- | ---: | ---: | --- |
| hybrid seed=2026 vs MSAT | AUC | +0.001149 | 0.000419 | 显著提升 |
| hybrid seed=2026 vs MSAT | AUPRC | +0.000834 | 0.003075 | 显著提升 |
| hybrid seed=2026 vs MSAT | F1 | +0.003613 | 0.007438 | 显著提升 |
| hybrid seed=2026 vs MSAT | MCC | +0.005889 | 0.017861 | 显著提升 |
| hybrid seed=1337 vs MSAT | AUC | +0.001121 | 0.001576 | 复跑后仍提升 |
| hybrid seed=1337 vs MSAT | AUPRC | +0.000888 | 0.056348 | 正向但边界显著 |
| hybrid seed=1337 vs MSAT | F1 | +0.003316 | 0.008698 | 复跑后仍提升 |
| hybrid seed=1337 vs MSAT | MCC | +0.005811 | 0.015257 | 复跑后仍提升 |

两次 hybrid seed 之间结果非常接近：AUC range 为 0.000028，AUPRC range 为 0.000054，F1 range 为 0.000297，MCC range 为 0.000078。这说明当前 hybrid PU-XMSAT 结果不是单一随机种子的偶然结果。

### 4.3 PU 权重敏感性

在 seed=1337、`reliable_negative_weight=0.8` 固定的条件下，测试了 `unlabeled_weight=0.1/0.2/0.4`：

| 权重设置 | AUC | AUPRC | F1 | MCC | 结论 |
| --- | ---: | ---: | ---: | ---: | --- |
| u0.1/rn0.8 | 0.979932 | 0.977368 | 0.933956 | 0.866775 | 未标注样本权重过低，整体变弱 |
| u0.2/rn0.8 | 0.980392 | 0.977983 | 0.934767 | 0.868331 | 当前平衡默认设置 |
| u0.4/rn0.8 | 0.980474 | 0.977902 | 0.934410 | 0.867410 | AUC 接近，但阈值指标略弱 |

该结果支持 `u0.2/rn0.8` 作为当前默认设置。它不是唯一可行权重，但在 ranking 指标和 thresholded metrics 之间更平衡。

## 5. 当前可以形成的研究结论

当前最稳妥的结论是：

> 在对 MSAT 主实验协议进行复现和修正后，项目发现“未观测中药-不良反应配对直接作为负样本”可能带来标签噪声。基于此，PU-XMSAT 将监督配对拆分为观测正样本、可靠负样本和未标注样本，并对未标注样本降低权重。实验结果显示，full-positive hybrid PU-XMSAT 在两个随机种子下相对复现 MSAT 基线稳定提升 AUC、F1 和 MCC，AUPRC 也保持正向趋势但提升幅度较小，其中一个 seed 的 AUPRC paired p 值为边界显著。

不建议写成：

1. PU-XMSAT 已经全面、绝对优于 MSAT；
2. PU-XMSAT 在所有指标和所有设置下都显著提升；
3. Table 5/6 已经完整复现；
4. Table 5/6 是主实验直接组成部分。

## 6. 下一步建议

当前不建议继续重复长时间训练，除非发现新的代码或数据问题。更有价值的下一步是把已有结果整理为论文材料，并补充解释性与外部证据：

1. 将 PU-XMSAT 写成论文中的方法扩展：重点说明未观测不等于负样本、可靠负样本选择、未标注样本降权训练。
2. 将当前表格整理成论文 Results 小节：主表报告 MSAT baseline、random PU-XMSAT、hybrid PU-XMSAT 两个 seed；补充 paired test 和权重敏感性表。
3. 补充案例分析或外部证据分级：不再强行声称 Table 5 等价复现，而是将其作为外部验证难点和未来解释性分析入口。
4. 如果继续扩展模型，可优先考虑导师建议中的三个方向：因果混杂控制、基于注意力/SHAP 的关键子图解释、更加严格的可靠负样本选择。

## 7. 给导师沟通时的推荐表述

可以这样概括当前工作：

> 我目前已经完成 MSAT 主实验的复现和协议核对，主实验指标与论文核心结果基本对齐，但 Table 5/6 属于外部验证和解释性案例，公开材料下暂时无法论文等价复现。基于复现中发现的“未观测不等于无关联”问题，我进一步实现了 PU-XMSAT，把未观测配对拆分为可靠负样本和未标注样本，并对未标注样本降权训练。当前 full-positive hybrid PU-XMSAT 在两个随机种子下相对复现 MSAT 基线稳定提升 AUC、F1 和 MCC，AUPRC 保持正向趋势但幅度较小。下一步我计划把这部分整理为论文方法和结果，同时补充可靠负样本选择的解释性与外部证据。

## 8. 对应项目文件

- 结果表草稿：`results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md`
- 英文正文草稿：`results/PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md`
- 研究进展记录：`results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`
- 项目长期记忆：`PROJECT_MEMORY.md`
- 当前审计文件：`results/reproduction_state_audit.json`
