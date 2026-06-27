# PU-XMSAT 组会/答辩 Slides 大纲

**日期：** 2026-06-27
**用途：** 将当前 MSAT 复现与 PU-XMSAT 改进结果整理成 10-12 页组会或答辩 PPT 结构。
**口径：** 本大纲只整理已验证结果，不新增实验结论；Table 5/6 保持“外部验证/解释性案例，公开材料下无法论文等价复现”的边界。

## Slide 1. 标题页

**标题建议：** 基于 MSAT 复现的 PU-XMSAT 中药不良反应预测改进研究

**核心信息：**

- 研究对象：中药-不良反应关联预测。
- 工作路径：先复现 MSAT 主实验，再针对未观测负样本噪声提出 PU-XMSAT。
- 当前状态：主实验复现已完成；PU-XMSAT 已完成 full-positive hybrid two-seed 与权重敏感性验证。

**建议视觉：** 左侧放“MSAT reproduction”，右侧放“PU-XMSAT extension”的流程箭头。

**讲稿提示：** 先说明这是一个复现加改进项目，不是单纯重新跑模型。

## Slide 2. 研究背景与问题

**核心信息：**

- 中药不良反应预测面临已知关联稀疏、上报不完整、机制复杂的问题。
- 原论文 MSAT 使用多源图结构进行中药-不良反应预测，是本项目复现锚点。
- 复现过程中发现一个关键问题：未观测配对被当成负样本，可能引入标签噪声。

**建议视觉：** 展示“observed positive / unobserved pair / assumed negative”的三段式示意。

**讲稿提示：** 重点解释“未观测不等于无关联”，为 PU Learning 引入做铺垫。

## Slide 3. 复现目标与协议修正

**核心信息：**

- 目标：复现 MSAT 主实验与核心评估指标。
- 当前主实验协议：`2026-06-23-val-test-edge-hidden`。
- 协议关键点：训练图隐藏验证集和测试集正样本边，避免归纳式评估中的信息泄漏。
- 审计状态：`issues: []`。

**建议视觉：** 用训练/验证/测试三块图说明 validation/test positive edges hidden from training graph。

**讲稿提示：** 说明复现不是只看指标，还包括检查数据切分、边隐藏和产物 provenance。

## Slide 4. MSAT 主实验复现结果

**核心信息：**

| 模型 | AUC | AUPRC | F1 | MCC |
| --- | ---: | ---: | ---: | ---: |
| MSAT reproduced baseline | 0.979271 | 0.977095 | 0.931451 | 0.862520 |

**建议视觉：** 简洁指标表或四个 metric cards。

**讲稿提示：** 这页只讲主实验锚点，避免把 Table 5/6 混入主实验指标。

## Slide 5. Table 5/6 的复现边界

**核心信息：**

- Table 5 是 Top-15 高置信未标注 CMM-ADR 预测的外部验证。
- Table 6 依赖 Table 5 候选，是下游 TCM 功能系统映射。
- 当前公开材料下无法论文等价复现 Table 5/6。
- 主要原因：候选生成流程、预测 checkpoint、证据筛选规则未完全公开；当前 Table 5 支持率为 1/15。

**建议视觉：** 用“main experiment”和“external validation/case interpretation”分区图。

**讲稿提示：** 这里要主动说明边界，体现复现工作的严谨性。

## Slide 6. PU-XMSAT 方法动机

**核心信息：**

- 原二分类训练假设：未观测 CMM-ADR pair 约等于 negative。
- 药物警戒场景中该假设较强，可能受到报告偏倚、适应症偏倚、合并用药和暴露人群差异影响。
- PU-XMSAT 将监督配对拆成：
  1. observed positives；
  2. reliable negatives；
  3. unlabeled pairs。
- 未标注样本进入训练但降低权重。

**建议视觉：** 三类样本的分流图：Positive / Reliable Negative / Unlabeled。

**讲稿提示：** 强调 PU-XMSAT 是从复现暴露出的问题自然延伸出来的，不是凭空换模型。

## Slide 7. PU-XMSAT 实验设置

**核心信息：**

| 设置项 | 当前方案 |
| --- | --- |
| 训练后端 | `full_msat_pu` |
| 采样策略 | `hybrid` 为主，`random` 为对照 |
| 候选缓存 | corrected randomized `random50k` |
| 配对规模 | full-positive `66,015` pairs / fold |
| 阈值选择 | validation-F1-selected threshold |
| 默认权重 | `unlabeled_weight=0.2`, `reliable_negative_weight=0.8` |

**建议视觉：** 实验配置表，不要放过多代码细节。

**讲稿提示：** 说明 random 是可行性和消融对照，hybrid 是当前主设置。

## Slide 8. PU-XMSAT 主结果

**核心信息：**

| Setting | Seed | AUC | AUPRC | F1 | MCC |
| --- | ---: | ---: | ---: | ---: | ---: |
| MSAT baseline | 42 | 0.979271 | 0.977095 | 0.931451 | 0.862520 |
| PU-XMSAT random | 42 | 0.979617 | 0.977273 | 0.932120 | 0.862509 |
| PU-XMSAT random | 2026 | 0.979732 | 0.977662 | 0.933776 | 0.866051 |
| PU-XMSAT hybrid | 2026 | 0.980420 | 0.977929 | 0.935064 | 0.868409 |
| PU-XMSAT hybrid | 1337 | 0.980392 | 0.977983 | 0.934767 | 0.868331 |

**建议视觉：** 表格加高亮 hybrid 两行；也可用柱状图突出 F1/MCC 提升。

**讲稿提示：** random 达到 baseline-level，hybrid 是当前最强结果。

## Slide 9. Hybrid 的统计比较与 seed 稳健性

**核心信息：**

- seed=2026 hybrid 相对 MSAT：AUC、AUPRC、F1、MCC paired t-test 均过 0.05。
- seed=1337 hybrid 相对 MSAT：AUC、F1、MCC 显著；AUPRC 正向但边界显著，p=0.056348。
- 两个 hybrid seed 的均值范围很小：
  - AUC range 0.000028；
  - AUPRC range 0.000054；
  - F1 range 0.000297；
  - MCC range 0.000078。

**建议视觉：** 两 seed 的四指标连线图或小表格。

**讲稿提示：** 结论要保守：seed-robust gains on AUC/F1/MCC，AUPRC 是稳定正向趋势。

## Slide 10. PU 权重敏感性

**核心信息：**

| 权重设置 | AUC | AUPRC | F1 | MCC | 结论 |
| --- | ---: | ---: | ---: | ---: | --- |
| u0.1/rn0.8 | 0.979932 | 0.977368 | 0.933956 | 0.866775 | 整体变弱 |
| u0.2/rn0.8 | 0.980392 | 0.977983 | 0.934767 | 0.868331 | 当前默认 |
| u0.4/rn0.8 | 0.980474 | 0.977902 | 0.934410 | 0.867410 | AUC 接近，F1/MCC 略弱 |

**建议视觉：** 三组权重的折线图或紧凑表格。

**讲稿提示：** 默认 u0.2/rn0.8 是平衡设置，不是随意选择。

## Slide 11. 当前结论与 claim 边界

**可以说：**

- 主实验与多数核心性能结果已复现，审计结果为 `issues: []`。
- Table 5/6 当前属于外部验证和解释性案例，公开材料下不能论文等价复现。
- Full-positive hybrid PU-XMSAT 在两个 seed 下稳定提升 AUC、F1、MCC，AUPRC 保持正向趋势。
- 权重敏感性支持 u0.2/rn0.8 作为当前默认设置。

**不要说：**

- 不要说全文 100% 复现。
- 不要说 Table 5/6 已完整复现。
- 不要说 PU-XMSAT 全面、绝对优于 MSAT。
- 不要隐藏 AUPRC 提升较小、一个 seed 边界显著的事实。

**建议视觉：** “Can claim / Cannot claim” 双栏表。

**讲稿提示：** 这一页体现研究边界，比单纯堆指标更重要。

## Slide 12. 下一步研究计划

**核心信息：**

近期不建议继续重复长时间训练，除非发现新代码或数据问题。下一步应从三个方向推进：

1. 论文正文整理：Methods 写 PU-XMSAT 构造，Results 写主表、paired test 和权重敏感性。
2. 外部证据与案例分析：把 Table 5/6 从“强行复现”转为外部证据分级和解释性分析入口。
3. 模型继续改进：沿导师建议推进因果混杂控制、关键子图解释、SHAP/注意力解释和更严格的可靠负样本策略。

**建议视觉：** 三条路线图：paper writing / external evidence / model extension。

**讲稿提示：** 最后强调当前阶段已经从“复现是否站得住”转向“如何把复现发现的问题发展成自己的研究贡献”。

## 附录建议

可根据场合准备 3 页 backup slides：

1. PU-XMSAT reliable-negative scoring 的组成因素；
2. Table 5 无法等价复现的证据链；
3. 当前 results 文件与 git 分支索引。
