# PU-XMSAT Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在已复现 MSAT 主实验的基础上，实现可靠负样本选择、PU Learning 训练、机制子图解释和外部证据辅助验证，形成可比较、可消融、可写入论文的改进实验体系。  
**Architecture:** 保留原始 MSAT 主训练链路作为冻结基线，在其外侧增加独立实验模块：负样本策略模块、PU Loss 模块、解释模块、证据模块和报告模块。所有新实验必须输出结构化 JSON/CSV，避免污染原始复现实验产物。  
**Tech Stack:** Python, PyTorch, NumPy, pandas, scikit-learn, pytest, existing MSAT data loaders, existing MSAT training/evaluation scripts.  

---

## 1. 实施原则

1. 不修改已经验证过的原始 MSAT 复现基线，除非为了增加兼容参数，并且必须保持默认行为不变。
2. 所有新增实验脚本必须显式写入 `MSAT/results` 下的独立文件，不能覆盖主实验结果。
3. 所有负样本、PU 权重、解释结果和证据结果必须可追溯到输入数据、随机种子和配置文件。
4. 每一个新增模块都需要先有最小单元测试，再运行小规模 smoke test，最后才进入完整训练。
5. 新方法的实验评价必须同时包含性能指标、消融指标和解释性指标。

## 2. 目标文件结构

新增或调整文件建议如下：

```text
MSAT/
  experiments/
    reliable_negative_sampling.py
    pu_dataset_builder.py
    pu_loss.py
    run_pu_msat_experiment.py
    run_negative_sampling_ablation.py
  inference/
    subgraph_explainer.py
    contribution_scoring.py
  scripts/
    run_explanation_case_study.py
    build_evidence_screening_table.py
    summarize_pu_xmsat_results.py
  tests/
    test_reliable_negative_sampling.py
    test_pu_dataset_builder.py
    test_pu_loss.py
    test_subgraph_explainer.py
    test_evidence_screening_table.py
  results/
    pu_negative_sampling_summary.json
    pu_training_summary.json
    pu_ablation_summary.json
    explanation_case_studies.json
    evidence_screening_summary.json
    PU_XMSAT_EXPERIMENT_REPORT.md
```

如果当前仓库已有同类目录，应优先复用既有目录命名；上述结构作为实施时的目标组织方式。

## 3. 第一阶段：冻结复现基线

**目标：** 确保任何新实验都能与当前已复现的 MSAT 基线进行可重复比较。

- [ ] 记录当前主实验结果文件路径和关键指标。

  需要固化的结果：

  ```text
  MSAT/results/summary.json
  ```

  当前已知指标：

  ```text
  AUC   = 0.9793
  AUPRC = 0.9771
  F1    = 0.9315
  MCC   = 0.8625
  ```

- [ ] 新增基线锁定报告 `MSAT/results/PU_XMSAT_BASELINE_LOCK.md`。

  报告内容应包含：

  ```text
  1. 原始 MSAT 代码版本
  2. 当前 git commit
  3. 数据文件清单
  4. 主实验指标
  5. 训练随机种子
  6. checkpoint 哈希
  7. 允许变更和禁止变更范围
  ```

- [ ] 增加结果完整性检查脚本 `MSAT/scripts/verify_baseline_lock.py`。

  该脚本至少检查：

  ```python
  REQUIRED_RESULTS = [
      "MSAT/results/summary.json",
      "MSAT/results/reproduction_gap_diagnosis.json",
      "MSAT/results/TABLE5_PROTOCOL_DECISION.md",
  ]
  ```

- [ ] 运行基线检查命令。

  ```bash
  python MSAT/scripts/verify_baseline_lock.py
  ```

**验收标准：**

1. 能够从结果文件中读取主实验指标。
2. 能够确认 Table 5 复现缺口报告存在。
3. 新增方法运行前后不会覆盖 `summary.json`。

## 4. 第二阶段：可靠负样本选择

**目标：** 从未观测药物-副作用组合中筛选更可信的负样本，替代原始随机负采样的一部分实验。

### 4.1 数据输入

可靠负样本模块需要读取：

```text
1. 已观测正样本 pair 列表
2. 药物集合
3. 副作用集合
4. 药物相似性或特征矩阵
5. 副作用频率或度数
6. 知识图谱边表
7. 可选：基线 MSAT 对未观测 pair 的预测分数
```

### 4.2 可靠负样本评分

新增文件：

```text
MSAT/experiments/reliable_negative_sampling.py
```

核心接口建议：

```python
def build_unobserved_pairs(drug_ids, side_effect_ids, positive_pairs):
    """Return all drug-side effect pairs not observed as positives."""


def score_reliable_negative_candidates(
    unobserved_pairs,
    positive_pairs,
    drug_similarity=None,
    side_effect_frequency=None,
    baseline_scores=None,
    graph_features=None,
):
    """Assign a reliability score to each unobserved pair."""


def select_reliable_negatives(candidate_scores, ratio, seed, strategy):
    """Select reliable negative pairs according to a named strategy."""
```

建议实现三种策略：

1. `random`：原始随机负采样，作为对照。
2. `low_score`：选择基线模型预测分数最低的未观测 pair。
3. `hybrid`：综合低预测分数、低结构支持和相似药物排除规则。

### 4.3 单元测试

新增文件：

```text
MSAT/tests/test_reliable_negative_sampling.py
```

测试点：

- [ ] 未观测集合不包含任何正样本。
- [ ] 同一随机种子下选择结果稳定。
- [ ] `ratio=1` 时负样本数量与正样本数量一致。
- [ ] `low_score` 策略优先选择低预测分数 pair。
- [ ] `hybrid` 策略不会选择与相似药物强关联的高风险候选。

测试命令：

```bash
python -m pytest MSAT/tests/test_reliable_negative_sampling.py -q
```

### 4.4 消融脚本

新增文件：

```text
MSAT/experiments/run_negative_sampling_ablation.py
```

命令形式：

```bash
python MSAT/experiments/run_negative_sampling_ablation.py \
  --strategies random low_score hybrid \
  --negative-ratios 1 5 10 \
  --seeds 0 1 2 \
  --output MSAT/results/pu_negative_sampling_summary.json
```

输出 JSON 结构：

```json
{
  "experiment": "negative_sampling_ablation",
  "strategies": {
    "random": {},
    "low_score": {},
    "hybrid": {}
  },
  "metrics": ["auc", "auprc", "f1", "mcc", "precision", "recall"],
  "artifacts": []
}
```

**验收标准：**

1. 三种负采样策略可独立运行。
2. 输出每种策略在不同负样本比例下的指标。
3. 不覆盖原始 MSAT 主实验结果。

## 5. 第三阶段：PU Dataset 与 PU Loss

**目标：** 将未观测 pair 建模为未标注样本，而不是强制负样本。

### 5.1 PU 数据集构建

新增文件：

```text
MSAT/experiments/pu_dataset_builder.py
```

核心接口：

```python
def build_pu_training_pairs(positive_pairs, unobserved_pairs, unlabeled_ratio, seed):
    """Build positive and unlabeled training pairs for PU learning."""


def assign_unlabeled_weights(unobserved_pairs, candidate_scores, min_weight, max_weight):
    """Assign negative-risk weights to unlabeled pairs."""
```

权重原则：

1. 越像潜在正样本的未标注 pair，负权重越低。
2. 越可靠的负样本，负权重越高。
3. 所有权重必须在 `[min_weight, max_weight]` 范围内。

### 5.2 PU Loss 实现

新增文件：

```text
MSAT/experiments/pu_loss.py
```

第一版建议实现 Weighted BCE PU Loss：

```python
import torch
import torch.nn.functional as F


def weighted_pu_bce_loss(logits, labels, sample_weights):
    losses = F.binary_cross_entropy_with_logits(logits, labels.float(), reduction="none")
    return (losses * sample_weights.float()).mean()
```

后续可扩展 Non-negative PU Risk：

```python
def nnpu_risk_loss(logits_positive, logits_unlabeled, positive_prior, beta=0.0):
    """Compute non-negative PU risk after positive prior calibration."""
```

### 5.3 单元测试

新增文件：

```text
MSAT/tests/test_pu_dataset_builder.py
MSAT/tests/test_pu_loss.py
```

测试点：

- [ ] PU 数据集中正样本标签为 1，未标注样本参与训练但不被简单等同于强负样本。
- [ ] sample weight 维度与 logits 一致。
- [ ] 高权重样本对 loss 的影响大于低权重样本。
- [ ] loss 在 CPU 环境下可反向传播。

测试命令：

```bash
python -m pytest MSAT/tests/test_pu_dataset_builder.py MSAT/tests/test_pu_loss.py -q
```

### 5.4 训练脚本

新增文件：

```text
MSAT/experiments/run_pu_msat_experiment.py
```

命令形式：

```bash
python MSAT/experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --loss weighted_pu_bce \
  --unlabeled-ratio 5 \
  --min-unlabeled-weight 0.05 \
  --max-unlabeled-weight 0.70 \
  --seeds 0 1 2 3 4 \
  --output MSAT/results/pu_training_summary.json
```

输出内容：

```json
{
  "experiment": "pu_msat",
  "baseline": "original_msat",
  "sampling_strategy": "hybrid",
  "loss": "weighted_pu_bce",
  "seeds": [],
  "fold_metrics": [],
  "mean_metrics": {},
  "std_metrics": {}
}
```

**验收标准：**

1. 能在单 seed、单 fold 下完成 smoke test。
2. 能输出与原始 MSAT 相同的评价指标。
3. 如果性能没有明显提升，也能输出负样本质量和鲁棒性分析结果。

## 6. 第四阶段：机制子图解释

**目标：** 对高置信药物-副作用预测输出关键成分、靶点和路径贡献。

### 6.1 子图解释模块

新增文件：

```text
MSAT/inference/subgraph_explainer.py
MSAT/inference/contribution_scoring.py
```

核心接口：

```python
def extract_candidate_subgraph(drug_id, side_effect_id, graph, max_hops, path_templates):
    """Extract interpretable mechanism subgraph for one prediction."""


def rank_nodes_by_attention(model_outputs, subgraph):
    """Rank nodes using model attention scores when available."""


def score_perturbation_contribution(model, pair, subgraph, node_groups):
    """Measure prediction score drop after masking node groups."""
```

路径模板：

```text
drug -> ingredient -> target -> side_effect
drug -> ingredient -> target -> disease -> side_effect
drug -> target -> side_effect
drug -> disease -> side_effect
```

### 6.2 案例脚本

新增文件：

```text
MSAT/scripts/run_explanation_case_study.py
```

命令形式：

```bash
python MSAT/scripts/run_explanation_case_study.py \
  --predictions MSAT/results/pu_training_predictions.csv \
  --top-k-pairs 20 \
  --top-k-nodes 10 \
  --output MSAT/results/explanation_case_studies.json
```

输出字段：

```json
{
  "drug": "",
  "side_effect": "",
  "prediction_score": 0.0,
  "top_ingredients": [],
  "top_targets": [],
  "top_paths": [],
  "contribution_scores": {}
}
```

### 6.3 解释性测试

新增文件：

```text
MSAT/tests/test_subgraph_explainer.py
```

测试点：

- [ ] 子图提取结果包含起点 drug 和终点 side effect。
- [ ] 路径模板不会输出不符合医学解释方向的任意路径。
- [ ] 贡献度排序结果可重复。
- [ ] 屏蔽高贡献节点后预测分数下降不小于屏蔽低贡献节点的平均下降。

测试命令：

```bash
python -m pytest MSAT/tests/test_subgraph_explainer.py -q
```

**验收标准：**

1. 至少输出 20 个高置信候选案例。
2. 每个案例包含 Top-K 成分、靶点和路径。
3. 至少 5 个案例能够被人工检查并写入阶段报告。

## 7. 第五阶段：外部证据辅助验证

**目标：** 为高置信预测案例建立文献和数据库证据追踪流程。

### 7.1 证据表构建

新增文件：

```text
MSAT/scripts/build_evidence_screening_table.py
```

输入：

```text
MSAT/results/explanation_case_studies.json
MSAT/results/table5_literature_evidence.json
```

输出：

```text
MSAT/results/evidence_screening_summary.json
MSAT/results/evidence_screening_table.csv
```

证据分级：

```text
A: 数据库或说明书直接记录
B: 文献直接报告药物-副作用关系
C: 文献支持成分、靶点或机制路径
D: 暂无明确支持或证据不一致
```

### 7.2 大模型辅助边界

实施时必须遵守：

1. 大模型输出只能用于证据摘要和候选分类。
2. 大模型输出不能直接写成训练标签。
3. 每条证据必须保留原始来源、检索关键词和摘要。
4. 对进入最终报告的案例必须进行人工复核。

### 7.3 测试

新增文件：

```text
MSAT/tests/test_evidence_screening_table.py
```

测试点：

- [ ] 每条证据记录包含来源字段。
- [ ] 证据等级只能是 A、B、C、D。
- [ ] 没有证据的案例不会被错误标记为强证据。
- [ ] 输出 CSV 和 JSON 的案例数量一致。

测试命令：

```bash
python -m pytest MSAT/tests/test_evidence_screening_table.py -q
```

**验收标准：**

1. 形成一个可人工检查的 evidence screening table。
2. 至少 10 个高置信候选有外部证据分级。
3. 最终报告中明确区分模型预测、外部证据和人工判断。

## 8. 第六阶段：实验矩阵

完整实验矩阵如下：

| 实验编号 | 模型 | 负样本策略 | Loss | 解释模块 | 证据模块 | 目的 |
| --- | --- | --- | --- | --- | --- | --- |
| E0 | MSAT | random | BCE | 否 | 否 | 原始复现基线 |
| E1 | MSAT-RN | low_score | BCE | 否 | 否 | 测试低分可靠负样本 |
| E2 | MSAT-RN | hybrid | BCE | 否 | 否 | 测试混合可靠负样本 |
| E3 | PU-MSAT | random | weighted PU BCE | 否 | 否 | 测试 PU Loss |
| E4 | PU-MSAT | hybrid | weighted PU BCE | 否 | 否 | 测试 RN + PU |
| E5 | PU-XMSAT | hybrid | weighted PU BCE | 是 | 否 | 解释性案例分析 |
| E6 | PU-XMSAT-Evidence | hybrid | weighted PU BCE | 是 | 是 | 生成升级版案例表 |

运行顺序：

- [ ] 先运行 E0 的基线读取，不重新训练。
- [ ] 运行 E1、E2 的小规模 smoke test。
- [ ] 运行 E3、E4 的单 fold smoke test。
- [ ] 在服务器可用时运行 E1 到 E4 的完整训练。
- [ ] 完整训练结束后运行 E5、E6 的解释与证据流程。

## 9. 第七阶段：服务器训练策略

在服务器重新可用前，本地只执行代码检查、单元测试和小规模 smoke test。服务器可用后再运行长时间训练。

### 9.1 本地预检

本地必须通过：

```bash
python -m pytest MSAT/tests/test_reliable_negative_sampling.py -q
python -m pytest MSAT/tests/test_pu_dataset_builder.py MSAT/tests/test_pu_loss.py -q
python -m pytest MSAT/tests/test_subgraph_explainer.py -q
python -m pytest MSAT/tests/test_evidence_screening_table.py -q
```

### 9.2 服务器训练命令

建议在服务器上使用 `tmux` 或 `nohup`：

```bash
tmux new -s pu_xmsat
python MSAT/experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --loss weighted_pu_bce \
  --unlabeled-ratio 5 \
  --seeds 0 1 2 3 4 \
  --output MSAT/results/pu_training_summary.json
```

负采样消融：

```bash
python MSAT/experiments/run_negative_sampling_ablation.py \
  --strategies random low_score hybrid \
  --negative-ratios 1 5 10 \
  --seeds 0 1 2 \
  --output MSAT/results/pu_negative_sampling_summary.json
```

解释与证据：

```bash
python MSAT/scripts/run_explanation_case_study.py \
  --predictions MSAT/results/pu_training_predictions.csv \
  --top-k-pairs 20 \
  --top-k-nodes 10 \
  --output MSAT/results/explanation_case_studies.json

python MSAT/scripts/build_evidence_screening_table.py \
  --cases MSAT/results/explanation_case_studies.json \
  --output-json MSAT/results/evidence_screening_summary.json \
  --output-csv MSAT/results/evidence_screening_table.csv
```

### 9.3 自动关机建议

长时间训练可以使用训练完成后自动关机策略，但必须先确认结果同步成功。建议包装脚本逻辑为：

```bash
python MSAT/experiments/run_pu_msat_experiment.py ... && \
python MSAT/scripts/summarize_pu_xmsat_results.py && \
git status --short && \
shutdown -h now
```

如果服务器中没有配置 git 凭据，则先压缩结果：

```bash
tar -czf pu_xmsat_results_$(date +%Y%m%d_%H%M%S).tar.gz MSAT/results
```

## 10. 第八阶段：结果汇总报告

新增文件：

```text
MSAT/scripts/summarize_pu_xmsat_results.py
MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md
```

报告结构：

```text
1. 实验背景
2. 原始 MSAT 复现结果
3. 可靠负样本策略结果
4. PU Learning 结果
5. 消融实验
6. 解释性案例
7. 外部证据分级
8. 与论文 Table 5 的关系
9. 局限性
10. 后续工作
```

汇总命令：

```bash
python MSAT/scripts/summarize_pu_xmsat_results.py \
  --baseline MSAT/results/summary.json \
  --negative MSAT/results/pu_negative_sampling_summary.json \
  --pu MSAT/results/pu_training_summary.json \
  --explanation MSAT/results/explanation_case_studies.json \
  --evidence MSAT/results/evidence_screening_summary.json \
  --output MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md
```

**验收标准：**

1. 报告能直接说明新方法相对 MSAT 的提升或不足。
2. 报告能解释如果性能无提升，是否在标签噪声鲁棒性或解释性上有价值。
3. 报告能生成适合导师讨论的图表和案例。

## 11. 代码提交策略

建议分四个 commit：

```text
1. docs: add research direction and implementation plan
2. feat: add reliable negative sampling and PU dataset builder
3. feat: add PU training and ablation scripts
4. feat: add explanation and evidence screening workflow
```

每个 commit 前至少运行对应模块测试。文档 commit 可以只运行：

```bash
git diff --check
```

功能 commit 必须运行对应 pytest。

## 12. 完整验收清单

- [ ] 原始 MSAT 主实验结果被锁定，后续实验不覆盖。
- [ ] 可靠负样本策略能够生成可追溯 pair 列表。
- [ ] PU Dataset 能区分正样本和未标注样本。
- [ ] Weighted PU Loss 能反向传播并接入训练脚本。
- [ ] 消融实验至少覆盖 random、low_score、hybrid 三种采样策略。
- [ ] 服务器完整训练输出均值和标准差。
- [ ] 解释模块能输出 Top-K 成分、靶点和机制路径。
- [ ] 证据模块能输出 A/B/C/D 分级。
- [ ] 最终报告区分模型预测、机制解释、外部证据和人工判断。
- [ ] 新增实验可以支撑一版论文式方法章节和实验章节。

## 13. 推荐执行顺序

第一轮实现只做最小闭环：

```text
可靠负样本 hybrid 策略
Weighted PU BCE Loss
单 seed smoke test
20 个解释案例
证据分级表
```

第二轮再扩展：

```text
多 seed 完整训练
负样本比例敏感性分析
nnPU Loss
稳定性解释评价
外部数据库多源检索
```

第三轮形成论文材料：

```text
方法图
实验表
消融表
案例表
局限性分析
未来因果图扩展
```

## 14. 与导师建议的对应关系

| 导师建议 | 本计划中的落地方式 | 当前优先级 |
| --- | --- | --- |
| 加入因果论和因果图 | 当前先做 DAG 偏倚分析，后续数据充分后做因果校正 | 中 |
| 基于注意力权重提取关键子图，做 SHAP 分析 | 实现 attention ranking、perturbation drop 和 SHAP-style 扩展接口 | 高 |
| 负采样策略需要考虑未观测不等于无关联 | 作为主线，实现 reliable negative sampling 与 PU Learning | 最高 |
| 模态缺乏，可用大模型辅助评估 | 作为证据筛选层，不直接作为训练标签 | 中 |

## 15. 结束条件

本计划完成时，应具备以下交付物：

1. 一套不破坏原始 MSAT 复现协议的新实验代码。
2. 一组可靠负样本和 PU Learning 对比结果。
3. 一组解释性案例和外部证据分级表。
4. 一份可提交给导师讨论的完整实验报告。
5. 一个清晰结论：新方法在预测性能、标签噪声鲁棒性、解释性或证据支持方面相对原始 MSAT 的具体改进。
