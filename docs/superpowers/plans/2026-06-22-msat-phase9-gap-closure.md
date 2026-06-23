# MSAT Phase 9 — 缺口闭合计划

> **Goal:** 闭合 Phase 8 后仍与论文不一致的条目，使 `REPRODUCTION_REPORT.md` §12 中 ❌/⚠️ 项尽量降为 ✅。  
> **验收:** 数值差距 < 0.1；下游解释要求**趋势/协议/表格结构**一致。  
> **前提:** Phase 0–8 GPU 结果已在服务器；本地以 CPU 分析 + 脚本修复为主，重推理/重训练放服务器。

**基线报告:** `MSAT/results/REPRODUCTION_REPORT.md` §12（2026-06-22）

---

## 一、缺口清单（按优先级）

| ID | 论文条目 | 现状 | Phase 9 任务 | 依赖 |
|----|----------|------|--------------|------|
| **9E** | Fig.5a 冷启动四模型 | MSAT `insufficient_samples`；基线无预测 | 对齐 `analyze_stratified` 文献 hold-out 掩码；产出 Precision/MCC/AUC | 本地 summary.json |
| **9E+** | Fig.5a GNN 基线 | 未跑 | `run_coldstart_gnn.py` 导出测试折分数（服务器 GPU） | 9E 模块 |
| **9F1** | Table 5 Top-15 | 支持 2/15 | 增加 `--use-predictor` 全局推理；扩展 mechanistic 判定 | best_model.pt |
| **9F2** | Table 6 映射 | 多数默认 Qi-Blood-Fluid | 从论文 Table 6 反推 PT/SOC 规则 | table5 CSV |
| **9F3** | §4.5.1 枳实案例 | 显示名错、分数低 | `paper_herb_display` 优先；命名路径 nobiletin/ABCG2 | entity_names |
| **9C** | Table 4 XGB > MSAT | +0.005 AUC | 审查 τ* / 基线超参（可选，P3） | 服务器 |
| **9G** | GCN fold 离群 | fold9 AUC 0.71 | 单折重跑（可选 P3） | 服务器 |

---

## 二、执行顺序（本周）

```mermaid
flowchart LR
  A[9E coldstart 协议修复] --> B[9F 显示名/TCM/Table5]
  B --> C[本地验证 + 报告更新]
  C --> D[9E+ GNN 冷启动 服务器]
  D --> E[9F1 predictor Table5 服务器]
```

| 步骤 | 动作 | 环境 |
|------|------|------|
| 1 | `inference/coldstart.py` + 重写 `run_coldstart_eval.py` | 本地 |
| 2 | `paper_herb_display` + `tcm_mapping` 扩展 + `run_case_zhishi` | 本地 |
| 3 | `run_table5_validation.py --use-predictor` | 服务器（需 checkpoint） |
| 4 | `run_coldstart_gnn.py` × GAT/HGT/Simple-HGN | 服务器 GPU |
| 5 | 同步结果 + 更新 `REPRODUCTION_REPORT.md` §12 | 本地 |

---

## 三、9E — Fig.5a 协议（关键修复）

**问题根因:** `run_coldstart_eval.py` 仅保留文献**正边**对 → 全为 y=1，无法算 AUC/Precision。

**正确协议（与 `analyze_stratified.py` 一致）:**

- 测试折子集 = **全部负样本** ∪ **文献来源正样本**（`edge_attr[:,2]==0`）
- 指标：Precision、MCC、AUC（阈值 0.5）
- 附加：文献正样本中 **训练图不可见 CMM** 比例（目标 ~96.5%）

**产物:** `results/coldstart_summary.json`（MSAT + 3 GNN）

---

## 四、9F — 下游解释

### 9F1 Table 5

- **OOF 模式（现有）:** 10 折最大分，适合归纳评估
- **Predictor 模式（新增）:** `MSATPredictor` + `best_model_for_prediction.pt` 对全 (CMM,ADR) 打分，排除监督正边 → 更接近论文「全局高置信新预测」

### 9F2 Table 6

- 扩展 `inference/tcm_mapping.py` PT_RULES / SOC_FALLBACK
- 验收：论文 Table 6 十五例中 Vomiting→Stomach、Tinnitus→Kidney、Dizziness→Liver 等

### 9F3 枳实案例

- `EntityNames.paper_herb_display()` 对 16 种子返回论文中文名
- `find_mechanistic_paths` 输出含 CID 72344 / ABCG2 可读标签（若有 compound_target 词表则接入）

---

## 五、验收标准（Phase 9 完成）

- [ ] `coldstart_summary.json` 含 MSAT + GAT/HGT/Simple-HGN 的 Precision/MCC/AUC
- [ ] MSAT 冷启动三项 **≥** 三个 GNN（趋势）
- [ ] `unseen_cmm_rate` 报告（目标 0.90–0.99）
- [ ] Table 5 `--use-predictor` 跑通；支持率 **提升**（不强制 13/15）
- [ ] 枳实案例 `herb_label` 含「枳实」
- [ ] Table 6 至少 5/15 行非默认 Qi-Blood-Fluid
- [ ] `REPRODUCTION_REPORT.md` §12 更新

---

## 六、命令速查

```bash
# 本地（无需 GPU）
cd MSAT
python scripts/run_coldstart_eval.py
python scripts/run_coldstart_eval.py --all-models   # MSAT only until GNN export

python scripts/run_case_zhishi.py
python scripts/run_table6_mapping.py

# 服务器（需 checkpoint）
python scripts/run_table5_validation.py --use-predictor
python scripts/run_coldstart_gnn.py --models gat hgt simple_hgn
```

---

**下一步:** 实现 `inference/coldstart.py` 并本地跑 MSAT 冷启动验证。
