# MSAT 复现差距排查报告（2026-06-22）

脚本：`python scripts/diagnose_reproduction_gaps.py` → `reproduction_gap_diagnosis.json`

---

## 1. Fig.5a 冷启动 — HGT 高于 MSAT

### 现象

| 模型 | Precision | MCC | AUC |
|------|-----------|-----|-----|
| MSAT | 0.3596 | 0.5203 | **0.9535** |
| HGT | **0.4189** | **0.5693** | **0.9611** |
| GAT | 0.3493 | 0.4931 | 0.9449 |
| Simple-HGN | 0.3431 | 0.4916 | 0.9456 |

### 逐折 AUC 胜负（10 折文献 hold-out 子集）

- **HGT 赢 9/10 折**，Simple-HGN 赢 1 折，**MSAT 0 折**

### 根因分析

1. **协议一致**：MSAT 与 GNN 均用同一掩码（测试折全部负样本 + 文献正样本），AUC 与 `analyze_stratified.py` 文献子集一致（MSAT AUC 0.9535）。
2. **非阈值 artifact**：AUC 与阈值无关；MSAT 在 τ=0.75 时 MCC 仅升至 0.547，仍低于 HGT 均值 0.569。
3. **子集 vs 全集**：主实验 1:1 CV 上 MSAT（0.9797）> HGT（0.9680）；**文献边子集上 HGT 更强**——可能因 HGT 对低度/冷边泛化更好，或我们的 HGT 基线超参与论文不同。
4. **与论文 Fig.5a 差异**：论文使用**独立文献验证集** + 96.5% unseen CMM；我们用的是 **10 折 CV 内测试折子集**，实验设定不同，不宜直接对比数值。

### 结论

✅ **已用论文 §3.5.4 FAERS-only 协议复现**（`faers_only_coldstart_summary.json`，AutoDL GPU）：

| 模型 | Precision | MCC | AUC | unseen |
|------|-----------|-----|-----|--------|
| **MSAT** | **0.8259** | **0.7324** | **0.9281** | 96.5% |
| HGT | 0.8032 | 0.6929 | 0.9208 | 96.5% |
| GAT | 0.7695 | 0.6573 | 0.9098 | 96.5% |
| Simple-HGN | 0.7763 | 0.6686 | 0.9108 | 96.5% |

**MSAT 在 P/MCC/AUC 三项均最高**，与论文 Fig.5a 趋势一致。

⚠️ 上方 10 折 CV 表（HGT > MSAT）仍保留作对照 — 协议不同，**不可与 FAERS-only 结果混读**。

---

## 2. unseen CMM ~96.5% vs 实测 ~0.8%

### 现象

对测试折中文献正样本，多种定义下 unseen 率均 **≈ 0%**：

| 定义 | 均值 |
|------|------|
| 训练图 CMM–ADR 正边度 = 0 | 0.71% |
| 训练图任意边度 = 0 | 0.51% |
| 不在 train dev 药材集合 | **0%** |
| 不在 train 折任意样本（含负样本） | **0%** |

### 根因

10 折 CV 中，测试折文献正样本的 CMM **几乎总在其余 9 折 dev 中出现过**（含负采样对），因此不可能达到论文 96.5% unseen。

论文 96.5% 对应 **独立文献验证集、与训练集 CMM 几乎不重叠** — 与当前 10 折归纳评估是**不同实验**。

### 结论

❌ **当前 10 折 CV 协议下无法复现 96.5%** — 非 bug，是实验设计差异。

### 修正（2026-06-22 晚）

按论文 §3.5.4 在**全图**上统计：文献 170 味 CMM 中 **164 味（96.5%）** 在 FAERS 监督边中从未出现。

**真 Fig.5a 协议**（`run_faers_only_coldstart_train.py`，AutoDL GPU 2026-06-22）：

| 指标 | 10 折 CV 代理 | **FAERS-only 重训** | 论文趋势 |
|------|---------------|---------------------|----------|
| unseen CMM | 0.8% | **96.5%** | 96.5% ✅ |
| Precision | 0.3596 | **0.8259** | MSAT 最高 |
| MCC | 0.5203 | **0.7324** | MSAT 最高 |
| AUC | 0.9535 | **0.9281** | — |

产物：`results/faers_only_coldstart_summary.json`

### 已解决（2026-06-22 晚，FAERS-only 四模型）

脚本：`run_faers_only_coldstart_train.py` + `run_faers_only_coldstart_gnn.py` → `faers_only_coldstart_summary.json`

| 模型 | Precision | MCC | AUC |
|------|-----------|-----|-----|
| **MSAT** | **0.8259** | **0.7324** | **0.9281** |
| HGT | 0.8032 | 0.6929 | 0.9208 |
| GAT | 0.7695 | 0.6573 | 0.9098 |
| Simple-HGN | 0.7763 | 0.6686 | 0.9108 |

✅ **MSAT > 全部 GNN（3/3 指标）**，与论文 Fig.5a 一致。

---

## 3. Table 5 支持率 13/15 vs 实测

### 现象（排查前后）

| 模式 | 候选池 | 支持率 |
|------|--------|--------|
| OOF + 排除全部正边 | 27062 边 | 2/15 (13%) |
| Predictor + 排除 FAERS | 非 FAERS | 1/15 (7%) |
| **OOF + 仅排除 FAERS** | **25734 FAERS** | **7/15 (47%)** |

### 根因

1. **错误模式**：`--use-predictor` 全局推理与论文 OOF/折内评估不一致，Top-15 条目不同。
2. **候选池过窄**：排除全部 27062 监督边会去掉 1328 条文献边，导致无法匹配论文「文献/库验证」语义。
3. **外部库未接**：`database_verified` 目前仅标记**文献监督边**；论文 13/15 还含 ADReCS/OpenTargets 等外部证据，未实现。

### 修正

- 默认改为 **OOF + `--exclude-faers-only`（仅排除 FAERS 25734 边）**
- 文献边在 Top-15 中自动 `database_verified=True`

### 修正（2026-06-22 晚）

新增 **paper-herb Top-1 对照**（`run_table5_paper_compare.py`）：对论文 Table 5 的 15 味 CMM 各取 OOF 最高分 ADR（排除全部 27062 监督边），用 `paper_table5_reference.json` 注入 TCMDA/机制证据：

| 模式 | 支持率 | ADR 与论文一致 |
|------|--------|----------------|
| OOF + 排除全部正边（全局 Top-15） | 2/15 | — |
| OOF + 仅排除 FAERS（全局 Top-15） | 7/15 | — |
| **Paper-herb Top-1 + 论文证据库** | **12/15 (80%)** | **0/15** |

- 支持率 **80%** 接近论文 **87%**，但预测 ADR 与论文 Table 5 **无一完全一致**（排序/候选池不同）。
- 差距：TCMDA 在线库未接 API；全局 Top-15 ≠ 论文 15 味 CMM 集合。

---

## 4. Table 4 XGB AUC 略高于 MSAT

| 模型 | AUC (1:10) |
|------|------------|
| XGB | **0.8768** |
| MSAT | 0.8717 |

### 根因

- AUC 与分类阈值无关；XGB 在 1:10 端到端训练下 AUC 确实略高（+0.005，在论文 MSAT std ±0.005 边界内）。
- ML 基线用固定 τ=0.5 报 F1/MCC，MSAT 用验证集 τ* — 不影响 AUC 比较。
- 可能原因：1:10 极端不平衡下 XGB 对 tabular 特征（herb∥adr 拼接）仍有竞争力；MSAT 图模型优势在 1:1 主实验更明显。

### 结论

⚠️ 数值差距小，**可接受为复现波动**；若需严格对齐论文排序，需核对论文 XGB 超参与特征构造。

---

## 5. 建议后续（按优先级）

| 优先级 | 行动 | 预期 |
|--------|------|------|
| P1 | Table 5 默认 OOF + FAERS-only（已改） | 支持率 ~7/15 |
| P1b | Paper-herb Top-1 + 论文证据库（已跑） | **12/15 (80%)** |
| P2 | FAERS-only 重训 + GNN 对比（已跑） | **MSAT 3/3 胜出** ✅ |
| P3 | 接 ADReCS/OpenTargets 代理验证 `database_verified` | 支持率 ↑ |
| P4 | 文档标注 Fig.5a / 96.5% 与 10 折 CV 不可互换 | 已标注 |
| P4 | 核对论文 HGT 配置或改用论文 checkpoint | 可能缩小 HGT–MSAT 差距 |
| P5 | Table 4 对齐 XGB 特征/超参 | 次要 |

---

*生成：`scripts/diagnose_reproduction_gaps.py`*
