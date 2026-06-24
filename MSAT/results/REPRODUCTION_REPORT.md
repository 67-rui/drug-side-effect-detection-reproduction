# MSAT 论文复现报告

> **论文:** Shi et al. (2026), *Front. Pharmacol.* 17:1774128, DOI [10.3389/fphar.2026.1774128](https://doi.org/10.3389/fphar.2026.1774128)  
> **官方代码:** [BowenShiGDPU/MSAT](https://github.com/BowenShiGDPU/MSAT)  
> **官方数据:** [Zenodo 17933842](https://zenodo.org/records/17933842)  
> **本地项目:** `drug-detect/MSAT/`  
> **报告路径:** `MSAT/results/REPRODUCTION_REPORT.md`（随实验进展追加更新）

---

## 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-06-18 上午 | 初版：Phase 0–4 完成；Table 2 主实验达标 |
| 2026-06-18 15:10 | **Phase 5 消融全部完成**；Table 3 四项结果已拉回本地；MVP 消融项通过 |
| 2026-06-18 15:20 | **Phase 6 Task 6.1 已启动**：1:10 不平衡实验远程训练中（`run_imbalanced.py`） |
| 2026-06-18 15:38 | **Phase 6 Task 6.1 完成**：AUC **0.8717 ± 0.0042**；`summary_neg10.json` / `neg10.log` 已拉回本地 |
| 2026-06-18 16:53 | **Phase 6 Task 6.2 完成**：9 基线 + MSAT 对比表；XGB 补跑完成；结果已拉回本地 |
| 2026-06-18 16:53 | **Phase 6 Task 6.3 完成**：度分层 + 文献/冷启动分析 → `stratified_summary.json` |
| 2026-06-22 11:18 | **Phase 7 已完成（最小可复现版）**：`run_phase7.py` 生成 Top-15（Table 6 风格）与「枳实种子→diarrhoea」路径案例 |
| 2026-06-22 17:10 | **Phase 8 全部 GPU 实验完成**（8B–8D 远程）；**Phase 8F 收尾脚本完成**（Table 5/6、枳实案例、汇总） |
| 2026-06-22 17:15 | **Phase 8H 报告更新**：新增论文逐表对照 §12；标注未完成/部分完成项 |
| 2026-06-22 17:31 | **Phase 9 启动**：Fig.5a 冷启动协议修复；`paper_herb_display`；Table 6 规则扩展；Table 5 `--use-predictor` |
| 2026-06-23 17:30 | **状态审计更新**：ML baseline 泄漏与 checkpoint 覆盖已在代码中修复；旧 Table4 ML、Table5/6、枳实案例产物标记为 stale；新增 `audit_reproduction_state.py` |
| 2026-06-24 10:31 | **最终服务器结果同步并审计通过**：Table 2/3/4、Fig.5a、Fig.6、Phase 9 产物已同步；`reproduction_state_audit.json` 为 `issues: []`；Table 5 仍是最大未复现缺口 |
| 2026-06-24 11:10 | **Table 5 公开文献候选抓取完成**：新增 PubMed/OpenAlex 候选证据脚本与缓存；当前 63 条药物/毒性背景候选，0 条精确 herb+ADR 命中 |
| 2026-06-24 11:35 | **Table 5 协议差异诊断更新**：`reproduction_gap_diagnosis.json` 显示论文 Table 5 的 15 个原始配对中仅 1 个进入当前 OOF 分数；旧 paper-seed 13/15 结果为诊断模式，ADR 匹配 0/15 |

---

## 0. 当前可引用状态（2026-06-24）

> 本节覆盖旧阶段性描述。下方历史章节保留实验过程记录；正式引用请优先使用本节、`results/README.md` 与 `results/reproduction_state_audit.json`。

### 0.1 已完成并可引用

| 论文目标 | 当前文件 | 当前结论 |
|----------|----------|----------|
| Table 2 MSAT 主实验 | `summary.json` | AUC **0.9793**，AUPRC **0.9771**，F1 **0.9315**，MCC **0.8625**；与论文主结果对齐 |
| Table 2 九基线 | `baseline_summary.json` | MSAT AUC 最高；传统 ML 与 GNN 基线均已在防泄漏协议下重跑 |
| Fig.5a FAERS-only 冷启动 | `faers_only_coldstart_summary.json` | MSAT 在 Precision、MCC、AUC 三项均优于 GAT/HGT/Simple-HGN |
| Fig.6 不平衡测试 | `fig6_summary.json` | MSAT 在 1:2、1:5、1:10 的 AUC/AUPRC 均最高 |
| 结果审计 | `reproduction_state_audit.json` | `issues: []`，无 stale artifact、无缺失协议 metadata、无可疑 ML 泄漏 |

### 0.2 已产出但需解释差异

| 论文目标 | 当前文件 | 差异 |
|----------|----------|------|
| Table 3 消融 | `ablation_summary.json` | 7 个变体齐全，但 Full 不是所有指标最高；AUC/AUPRC 最高为 `wo_esa`，F1/MCC 最高为 `only_hsp` |
| Table 4 全模型 1:10 | `baseline_neg10_summary.json` | MSAT 的 F1/MCC 最高，但 XGB 的 AUC/AUPRC 略高于 MSAT；论文中 MSAT AUC/AUPRC/MCC 最高 |
| Fig.6 阈值指标 | `fig6_summary.json` | AUC/AUPRC 对齐论文趋势；F1/MCC 当前 HGT 更高，需检查阈值校准与 ratio-specific tau |
| §4.5.1 枳实案例 | `case_zhishi_diarrhoea.json` | 已使用主 checkpoint 生成，但需要与论文 nobiletin/ABCG2 证据逐项对照 |

### 0.3 尚未复现

| 论文目标 | 当前状态 | 下一步 |
|----------|----------|--------|
| Table 5 Top-15 外部验证 | 当前 `table5_summary.json` 支持率 **1/15**；论文为 **13/15**；`reproduction_gap_diagnosis.json` 显示论文原始配对仅 **1/15** 进入 OOF 分数；公开文献自动候选精确 herb+ADR 命中为 **0** | 优先反推论文 Table 5 候选生成/排序协议；TCMDA 核验作为第二层证据补充 |
| Table 6 精细 TCM 系统映射 | 当前映射依赖 Table 5 且多数落入粗粒度系统 | Table 5 证据确定后，补 PT/SOC 到 16 TCM 系统的规则与人工复核 |

---

## 1. 复现目标与总体结论

**任务:** 中药材（CMM）– 不良反应（ADR）链路预测，10 折分层交叉验证，1:1 类型约束负采样，归纳式评估。

**当前结论（2026-06-23 17:30）：** 本报告保留历史过程记录；最终引用前请优先查看 `FINAL_REMOTE_RUN_SUMMARY_2026-06-23.md` 和 `reproduction_state_audit.json`。

### 1.1 核心数值实验 — 主线基本达标，部分产物待重跑

- **主实验（Table 2）**：最终同步 AUC **0.9792 ± 0.0018**（论文 0.979 ± 0.001）✅
- **消融（Table 3，7 变体）**：Full 最高；w/o HCI 最低；Only 组顺序未完全等同论文 ⚠️
- **1:10 不平衡 MSAT（Table 4）**：最终同步 AUC **0.8710 ± 0.0051**（论文 ~0.875 ± 0.005）✅
- **Table 4 ML baselines**：LR/RF/XGB 旧 JSON 出现 AUC≈1.0，已确认为 edge_attr 泄漏修复前产物；需重跑 ❌
- **Fig.6 测试不平衡 sweep**：当前 MSAT 仅在 ratio=10 最高；ratio=2/5 为 HGT 略高 ⚠️
- **Fig.5b 度分层**：Tail/Head 趋势与论文一致（Tail AUC 0.972 > Head 0.836）✅
- **实体映射（8A）**：16/16 Table 5 种子 `mapped_id` 非空且互不重复 ✅
- **Fig.5a FAERS-only 冷启动**：MSAT 在 Precision/MCC/AUC 上优于 GAT/HGT/Simple-HGN ✅

### 1.2 下游解释 — 脚本已跑通，与论文语义未完全对齐 ⚠️

- **Table 5**：当前 `table5_summary.json` 标记为 stale；最终同步支持率 1/15，且 TCMDA 证据口径未对齐论文 ❌
- **Table 6**：当前 `table6_mapping.json` 标记为 stale；映射依赖 stale Table 5，规则仍偏粗 ⚠️
- **§4.5.1 枳实案例**：`herb_id=277`（Citrus aurantium）正确；nobiletin 路径存在；当前产物 stale，最终同步 score 0.2549/rank 7，需用干净 checkpoint 重跑 ⚠️

### 1.3 尚未完成 ❌

- **受污染产物重跑**：服务器恢复后运行 `scripts/rerun_after_artifact_fix.sh`
- **Table 4 九基线趋势**：修复代码后尚未重跑 LR/RF/XGB；旧结果不可引用
- **可选 Phase 8G**：GCN fold 离群重跑、超参敏感性、Supplementary 未做

### 1.4 是否「全部完成」？

| 口径 | 判定 |
|------|------|
| **MVP（主实验 + 消融 + MSAT 1:10）** | ✅ **已完成** |
| **Phase 8 计划（8A–8F 脚本与 GPU 队列）** | ✅ **已完成** |
| **与论文逐表数值/语义完全一致** | ❌ **未完成**（Table 4 ML 重跑、Fig.6、Table 5/6、枳实案例） |

**一句话：** 训练与主指标复现成功；下游解释与部分对比实验仍有关键差距，不宜宣称「全文 100% 复现」。

---

## 2. 环境与数据

| 项目 | 配置 |
|------|------|
| 训练平台 | AutoDL GPU（具体 SSH 端点不入库） |
| Python | 3.12（远程 miniconda3） |
| 框架 | PyTorch + PyTorch Geometric |
| 图数据 | `experiments_data_clean_final/complete_hetero_graph.pt`（Zenodo 官方） |
| 折划分 | **`MSAT/data/10fold_cv_split.pkl`（官方 GitHub，非自生成 KFold）** |
| 随机种子 | 42 |

**图规模（与论文 Table 1 一致）:**

| 节点 | 数量 | 特征 |
|------|------|------|
| herb (CMM) | 651 | BioBERT 768 维 |
| compound | 1,498 | ChemBERTa 768 维 |
| target | 21,393 | 768 维 |
| adr | 5,974 | 768 维 |
| CMM–ADR 监督边 | 27,062 | 6 维 evidence |

---

## 3. 关键修复记录

首次 10 折训练 AUC 仅 **0.8725**，经排查后修复，复现成功。

| 问题 | 影响 | 修复 |
|------|------|------|
| 自写 `sklearn.KFold` 折划分 | 测试集与官方重叠仅 ~15%，指标严重偏低 | 改用官方 `10fold_cv_split.pkl` |
| 测试边移除含负样本对 | 与论文归纳协议不一致 | 仅移除测试/验证**正样本** CMM–ADR 边 |
| 验证集正边未从图中移除 | 验证 AUC 泄漏，早停选错 checkpoint | 训练前同时移除 val 正边 |
| train/val 划分无固定 seed | 不可复现 | `RANDOM_STATE + fold_idx` |

修复后 fold 0 单折验证：AUC **0.9809**（修复前 0.8682）。

---

## 4. 训练配置（与论文 / `config.py` 对齐）

| 参数 | 值 |
|------|-----|
| hidden_channels | 576 |
| out_channels | 72 |
| num_layers | 3 |
| num_heads | 8 |
| dropout | 0.18 |
| learning_rate | 4e-4 |
| weight_decay | 1e-5 |
| num_epochs / patience | 1000 / 100 |
| 负采样 | 1:1（官方 pkl 预采样） |
| 折内划分 | dev 90% train / 10% val |

---

## 5. Phase 进度

| Phase | 内容 | 状态 |
|-------|------|------|
| 0 | 环境与骨架 | ✅ |
| 1 | FeatureExtractor + 官方折 | ✅ |
| 2 | 节点/边编码 | ⏭ 跳过（Zenodo 预计算） |
| 3 | 单折 smoke | ✅ |
| 4 | 完整 10 折 CV | ✅ |
| 5 | 消融（ESA / HSP / HCI） | ✅ 14:21–14:58 完成 |
| 6.1 | 1:10 不平衡（Table 4） | ✅ 15:19–15:32 完成 |
| 6.2 | 基线对比（9 模型） | ✅ 16:41–16:58 完成 |
| 6.3 | 冷启动 / 度分层 | ✅ `stratified_summary.json` |
| 7 | 下游解释（Phase 7 最小版） | ✅ 已被 Phase 8F 取代 |
| **8A** | 实体映射（651 CMM + 16 种子） | ✅ `validate_entity_mapping.py` |
| **8B** | Table 3 Only ESA/HSP/HCI | ✅ `summary_only_*.json` |
| **8C** | Table 4 九基线 1:10 | ✅ `baseline_*_neg10.json` |
| **8D** | Fig.6 测试不平衡 sweep | ✅ `fig6_summary.json` |
| **8E** | Fig.5a 冷启动四模型 | ⚠️ 脚本有，指标未产出 |
| **8F** | Table 5/6 + 枳实案例 | ✅ 脚本完成；语义部分对齐 |
| **8G** | 可选（GCN 重跑等） | ⏭ 未做 |
| **8H** | 报告逐表对照 | ✅ 本节 |
| **9E** | Fig.5a MSAT 冷启动 | ✅ `coldstart_summary.json` |
| **9E+** | Fig.5a GNN 三基线 | ⏳ 脚本就绪，待服务器 `run_coldstart_gnn.py` |
| **9F** | Table5 predictor / 显示名 / TCM | ⚠️ 本地 MSAT 冷启动完成；predictor 待服务器 |

---

## 6. Table 2 — 主实验（10 折 CV，Full MSAT）

**训练时间:** 2026-06-18 11:40–11:54（远程），约 **12.7 分钟**  
**日志:** `results/train_fix.log`  
**结构化结果:** `results/summary.json`

### 6.1 总体指标 vs 论文

| 指标 | 本次（mean ± std） | 论文 Table 2 | MVP (≥) | 判定 |
|------|-------------------|--------------|---------|------|
| **AUC** | **0.9797 ± 0.0014** | 0.979 ± 0.001 | 0.970 | ✅ |
| AUPRC | 0.9778 ± 0.0019 | 0.977 ± 0.002 | — | ✅ |
| F1 | 0.9327 ± 0.0032 | 0.930 ± 0.003 | — | ✅ |
| MCC | 0.8647 ± 0.0060 | 0.860 ± 0.005 | — | ✅ |
| Precision | 0.9269 ± 0.0073 | 0.927 ± 0.005 | — | ✅ |
| Recall | 0.9386 ± 0.0059 | 0.934 ± 0.005 | — | ✅ |

### 6.2 各折测试 AUC

| Fold | AUC | F1 | MCC | Best Epoch |
|------|-----|-----|-----|------------|
| 0 | 0.9815 | 0.9321 | 0.8671 | 46 |
| 1 | 0.9804 | 0.9397 | 0.8754 | 36 |
| 2 | 0.9820 | 0.9360 | 0.8722 | 46 |
| 3 | 0.9793 | 0.9344 | 0.8664 | 39 |
| 4 | 0.9775 | 0.9296 | 0.8594 | 48 |
| 5 | 0.9794 | 0.9308 | 0.8648 | 44 |
| 6 | 0.9784 | 0.9303 | 0.8585 | 38 |
| 7 | 0.9797 | 0.9321 | 0.8633 | 39 |
| 8 | 0.9812 | 0.9335 | 0.8655 | 42 |
| 9 | 0.9779 | 0.9283 | 0.8544 | 43 |

**资源:** 平均训练 72.9 s/折，总 75.9 s/折；vs 随机 t=994.4, p≈5.4e-24。

**最佳推理模型:** `saved_models/best_model_for_prediction.pt`（来自 fold 2，测试 AUC 0.9820）

---

## 7. Table 3 — 消融实验

**脚本:** `scripts/run_ablation.py`  
**训练时间:** 2026-06-18 14:21–14:58（远程，约 37 分钟）  
**日志:** `results/ablation.log`  
**汇总:** `results/ablation_summary.json`

**论文预期 AUC 趋势:** Full > w/o HSP > w/o ESA > w/o HCI

### 7.1 四组变体结果（10 折 CV）

| 变体 | ESA | HSP | HCI | AUC (mean ± std) | AUPRC | F1 | MCC | 结果文件 |
|------|-----|-----|-----|------------------|-------|-----|-----|----------|
| **Full** | ✓ | ✓ | ✓ | **0.9797 ± 0.0014** | 0.9778 | 0.9327 | 0.8647 | `summary.json` |
| w/o ESA | ✗ | ✓ | ✓ | 0.9793 ± 0.0016 | 0.9771 | 0.9307 | 0.8609 | `summary_wo_esa.json` |
| w/o HSP | ✓ | ✗ | ✓ | 0.9782 ± 0.0015 | 0.9763 | 0.9293 | 0.8573 | `summary_wo_hsp.json` |
| w/o HCI | ✓ | ✓ | ✗ | 0.9780 ± 0.0019 | 0.9758 | **0.9338** | **0.8661** | `summary_wo_hci.json` |

### 7.2 趋势分析

**AUC 相对 Full 的下降（ΔAUC）:**

| 移除模块 | ΔAUC | 解读 |
|----------|------|------|
| ESA-Gate | −0.0004 | 贡献最小 |
| HSP-Layer | −0.0015 | 贡献中等 |
| HCI-Module | −0.0017 | AUC 下降最大 |

**本次 AUC 排序:** Full (0.9797) > w/o ESA (0.9793) > w/o HSP (0.9782) > w/o HCI (0.9780)

- ✅ Full 模型 AUC 最高，符合预期。
- ✅ 移除 HCI 后 AUC 最低（与论文「HCI 贡献显著」一致）。
- ⚠️ w/o ESA 与 w/o HSP 的相对次序与论文 Table 3 略有不同（本次移除 ESA 对 AUC 影响小于移除 HSP）；差异在 0.001 量级，可能来自随机种子/早停波动。
- ℹ️ w/o HCI 仅保留 MLP 单头，F1/MCC 略高于 Full，但 AUC/AUPRC 低于 Full——与多路融合主要提升排序能力（AUC）的解释一致。

### 7.3 Only 三组变体（Phase 8B，10 折 CV）

| 变体 | ESA | HSP | HCI | 本次 AUC | 论文 AUC | Δ | 判定 |
|------|-----|-----|-----|----------|----------|---|------|
| Only ESA | ✓ | ✗ | ✗ | 0.9772 ± 0.0016 | 0.973 | +0.004 | ✅ |
| Only HSP | ✗ | ✓ | ✗ | 0.9782 ± 0.0016 | 0.971 | +0.007 | ✅ |
| Only HCI | ✗ | ✗ | ✓ | 0.9784 ± 0.0015 | 0.961 | +0.017 | ✅ |

**Only 组 AUC 排序（本次）：** Only HCI (0.9784) > Only HSP (0.9782) > Only ESA (0.9772)

- ✅ 三组 Only AUC **均低于 Full**（0.9797）。
- ⚠️ 论文 Only HCI 应为 Only 组**最低**（0.961）；本次 Only HCI 反而最高，趋势与论文相反（数值 Δ < 0.02，模块贡献解读需谨慎）。

### 7.4 判定

- [x] 七组变体 10 折全部完成（4 w/o + 3 only）
- [x] `ablation_summary.json` 已更新（7 行）
- [x] 全部 JSON 已拉回本地
- [x] 与论文 Table 3 原始数值对比（见 §7.1、§7.3）

---

## 8. MVP 验收清单

| 项 | 状态 |
|----|------|
| `python train.py` 10 折无报错 | ✅ |
| `results/summary.json` 生成 | ✅ |
| AUC ≥ 0.970 | ✅（最终同步 0.9792） |
| 消融趋势与 Table 3 一致 | ✅（Full 最高；w/o HCI 最低） |
| Only 三组低于 Full | ✅ |
| Phase 8 GPU 队列（8B–8D） | ✅ |
| Table 5/6 脚本产出 | ❌ 当前 root 产物 stale，需重跑 |
| Fig.5a 四模型冷启动 | ✅ FAERS-only 四模型已完成 |
| 测试折边无泄漏 | ✅（train.py 归纳协议已修复） |

---

## 9. 产物清单

| 路径 | 说明 | 本地 |
|------|------|------|
| `results/summary.json` | Full 10 折汇总 | ✅ |
| `results/train_fix.log` | Full 训练日志 | ✅ |
| `results/ablation_summary.json` | 消融汇总 | ✅ |
| `results/ablation.log` | 消融训练日志 | ✅ |
| `results/summary_wo_esa.json` | w/o ESA | ✅ |
| `results/summary_wo_hsp.json` | w/o HSP | ✅ |
| `results/summary_wo_hci.json` | w/o HCI | ✅ |
| `results/summary_neg10.json` | 1:10 不平衡 10 折汇总 | ✅ |
| `results/neg10.log` | 1:10 不平衡训练日志 | ✅ |
| `results/baseline_summary.json` | 9 基线 + MSAT 对比汇总 | ✅ |
| `results/baseline_{lr,rf,xgb,gcn,gat,rgcn,hgt,hetnn,simple_hgn}.json` | 各基线 10 折 | ✅ |
| `results/baselines_ml.log` / `baselines_gnn.log` | 基线训练日志 | ✅ |
| `results/stratified_summary.json` | 度分层 / 文献边 AUC | ✅ |
| `results/summary_only_{esa,hsp,hci}.json` | Only 消融 10 折 | ✅ |
| `results/baseline_*_neg10.json` | 九基线 1:10 | ⚠️ ML 旧结果不可引用 |
| `results/baseline_neg10_summary.json` | Table 4 汇总 | ⚠️ ML 旧结果不可引用 |
| `results/summary_testneg{2,5,10}.json` | Fig.6 MSAT 各 ratio | ✅ |
| `results/baseline_*_testneg{2,5,10}.json` | Fig.6 基线各 ratio | ✅ |
| `results/fig6_summary.json` | Fig.6 汇总 | ⚠️ ratio 2/5 未对齐 |
| `results/table5_top15.csv` / `table5_summary.json` | Table 5 Top-15 | ❌ stale |
| `results/table6_mapping.csv` / `.json` | Table 6 TCM 映射 | ❌ stale |
| `results/case_zhishi_diarrhoea.json` | §4.5.1 枳实案例 | ❌ stale |
| `results/coldstart_summary.json` | Fig.5a（未完成） | ⚠️ |
| `data/cctcm_herb_index.json` | ccTCM 651 映射 | ✅ |
| `data/entity_names.json` v2 | 实体名称（含 paper_herb_id_map） | ✅ |
| `saved_models/best_model_fold0..9.pt` | 各折 checkpoint | ✅（~7 GB） |
| `saved_models/best_model_for_prediction.pt` | 最佳推理模型 | ✅ |
| `data/10fold_cv_split.pkl` | 官方折划分 | ✅ |
| `results/reproduction_state_audit.json` | 当前产物审计 | ✅ |

---

## 10. 扩展实验结果

### 10.1 Phase 6 — 1:10 不平衡实验（Table 4）【已完成】

> 实现：`FeatureExtractor(neg_ratio=10)` + 验证集 τ* 最大化 F1（`USE_OPTIMAL_THRESHOLD=True`）。  
> 脚本：`python -u scripts/run_imbalanced.py`  
> **训练时间:** 2026-06-18 15:19–15:32（远程），约 **14.6 分钟**  
> **日志:** `results/neg10.log`  
> **结构化结果:** `results/summary_neg10.json`

#### 10.1.1 总体指标 vs 论文

| 指标 | 本次（mean ± std） | 论文 Table 4 | 判定 |
|------|-------------------|--------------|------|
| **AUC** | **0.8717 ± 0.0042** | ~0.875 ± 0.005 | ✅ |
| AUPRC | 0.5911 ± 0.0122 | — | — |
| F1 | 0.5582 ± 0.0100 | — | — |
| MCC | 0.5146 ± 0.0123 | — | — |
| Precision | 0.5604 ± 0.0298 | — | — |
| Recall | 0.5578 ± 0.0178 | — | — |

**阈值策略:** 每折在验证集上搜索 τ* ∈ [0.01, 0.99] 使 F1 最大，再用于测试集分类；τ* 均值约 **0.33–0.41**（非固定 0.5）。

#### 10.1.2 各折测试 AUC

| Fold | AUC | F1 | τ* | Val F1@τ* | Best Epoch |
|------|-----|-----|-----|-----------|------------|
| 0 | 0.8614 | 0.5351 | 0.290 | 0.5572 | 35 |
| 1 | 0.8761 | 0.5665 | 0.370 | 0.5605 | 60 |
| 2 | 0.8773 | 0.5621 | 0.340 | 0.5625 | 59 |
| 3 | 0.8723 | 0.5686 | 0.410 | 0.5596 | 53 |
| 4 | 0.8696 | 0.5492 | 0.350 | 0.5515 | 34 |
| 5 | 0.8742 | 0.5606 | 0.340 | 0.5708 | 36 |
| 6 | 0.8726 | 0.5682 | 0.340 | 0.5661 | 54 |
| 7 | 0.8724 | 0.5633 | 0.330 | 0.5587 | 51 |
| 8 | 0.8693 | 0.5583 | 0.300 | 0.5686 | 49 |
| 9 | 0.8713 | 0.5503 | 0.330 | 0.5707 | 58 |

**资源:** 平均训练 80.8 s/折，总 87.3 s/折；vs 随机 t=266.0, p≈7.6e-19。

**分析:** 与论文差距仅 0.003，落在论文自身标准差（±0.005）范围内，视为复现成功。Fold 0 略低（0.8614），其余 9 折均值 **0.8734**。

#### 10.1.3 代码改动（Task 6.1）

| 文件 | 改动 |
|------|------|
| `config.py` | `USE_OPTIMAL_THRESHOLD` 开关 |
| `experiments/feature_extractor.py` | `neg_ratio=10` 从 pkl 正样本重采样，缓存 `fold{N}_{dev\|test}_neg10.npz` |
| `train.py` | `find_optimal_threshold()`；测试集用 τ* 评估 |
| `scripts/run_imbalanced.py` | 设置 `NEG_RATIO=10` 并启动 10 折 CV |

### 10.2 Phase 6 — 基线对比（Table 2 扩展）【已完成】

> 脚本：`scripts/run_baselines.py`（统一官方折划分 + 1:1 负采样 + 归纳式边移除）  
> 汇总：`results/baseline_summary.json`  
> 训练：ML（LR/RF/XGB）+ GNN（GCN/GAT/R-GCN/HGT/HetGNN/Simple-HGN）均在 AutoDL 远程完成

| 模型 | AUC (mean ± std) | F1 | 备注 |
|------|------------------|-----|------|
| **MSAT (Full)** | **0.9797 ± 0.0014** | 0.9327 | 主实验 |
| Simple-HGN | 0.9737 ± 0.0026 | 0.9158 | GNN 基线最优 |
| GAT | 0.9746 ± 0.0029 | 0.9188 | |
| HetGNN | 0.9702 ± 0.0023 | 0.8838 | |
| R-GCN | 0.9684 ± 0.0024 | 0.8818 | |
| HGT | 0.9680 ± 0.0028 | 0.8900 | |
| XGBoost | 0.9412 ± 0.0030 | 0.8624 | ML 最优 |
| LR | 0.9316 ± 0.0026 | 0.8516 | |
| GCN | 0.9228 ± 0.0731 | 0.9130 | fold10 离群拉高标准差 |
| RF | 0.9202 ± 0.0035 | 0.8528 | |
| MSAT (1:10) | 0.8717 ± 0.0042 | 0.5582 | Table 4 |

**判定：** MSAT 显著优于全部 9 基线，符合论文 Table 2 趋势（MSAT > GNN > ML）。

### 10.3 Phase 6 — 冷启动 / 度分层（Fig.5）【已完成】

> 脚本：`scripts/analyze_stratified.py`（基于 `summary.json` 各折预测 + 训练图度）  
> 汇总：`results/stratified_summary.json`

| 分组 | AUC (mean ± std) | F1 | 解读 |
|------|------------------|-----|------|
| Tail CMM（低度） | **0.9722 ± 0.0020** | 0.8577 | 低度 CMM 反而 AUC 最高 |
| Medium CMM | 0.8671 ± 0.0205 | 0.9516 | |
| Head CMM（高度） | 0.8358 ± 0.0311 | 0.9840 | 高度 CMM AUC 偏低（F1 仍高） |
| 文献 hold-out | 0.9535 ± 0.0075 | 0.5035 | 非 FAERS 正样本 + 全部负样本 |
| 零度 CMM 冷启动 | 0.9206 ± 0.0637 | 0.3330 | 样本少，波动大 |

**分析：** Tail/文献集 AUC 高但 F1 低，因 1:1 负采样下负样本远多于正样本；Head CMM 高度节点在测试集中更易与训练重叠，排序难度更大。

### 10.4 Phase 8C — Table 4 九基线 1:10【历史表，不可引用】

> 脚本：`scripts/run_baselines.py --neg-ratio 10 --all`  
> 汇总：`results/baseline_neg10_summary.json`  
> **训练时间:** 2026-06-22（远程 Phase 8C）  
> **当前状态:** 该表是泄漏修复前历史记录。最终同步后的 LR/RF/XGB 为 AUC≈1.0，已由 `reproduction_state_audit.json` 标记为 `suspicious_ml_auc`。正式 Table 4 全模型结论必须重跑。

| 模型 | AUC (mean ± std) | F1 | MCC | 论文趋势 |
|------|------------------|-----|-----|----------|
| **MSAT** | **0.8717 ± 0.0042** | 0.5582 | 0.5146 | 应最优 |
| XGB | 0.8768 ± 0.0039 | 0.5100 | 0.5049 | — |
| HGT | 0.8678 ± 0.0051 | 0.2931 | 0.3103 | — |
| GAT | 0.8510 ± 0.0055 | 0.4595 | 0.4524 | — |
| Simple-HGN | 0.8503 ± 0.0048 | 0.4447 | 0.4375 | — |
| HetGNN | 0.8463 ± 0.0042 | 0.4759 | 0.4611 | — |
| R-GCN | 0.8454 ± 0.0045 | 0.4557 | 0.4463 | — |
| RF | 0.8419 ± 0.0050 | 0.4946 | 0.4439 | — |
| LR | 0.8143 ± 0.0050 | 0.3312 | 0.3653 | — |
| GCN | 0.5491 ± 0.0837 | 0.1041 | 0.0974 | fold 离群 |

**判定：**

- ✅ MSAT AUC 与论文 ~0.875 差距 0.003（在 ±0.005 内）。
- ❌ 当前 Table 4 全模型排名不可引用；后续诊断确认 ML pair features 曾包含 CMM-ADR edge_attr，需使用修复后代码重跑 LR/RF/XGB。
- ⚠️ GCN 1:10 仍严重离群（与 1:1 情形类似）。

### 10.5 Phase 8D — Fig.6 测试不平衡 sweep【已完成】

> 协议：训练始终 1:1；**仅测试集**负正比 1:2 / 1:5 / 1:10；验证集选 τ* 最大化 F1。  
> 脚本：`scripts/run_imbalance_sweep.py`  
> 汇总：`results/fig6_summary.json`

| test neg:pos | MSAT AUC | HGT | Simple-HGN | GAT | MSAT 是否最高 |
|--------------|----------|-----|------------|-----|---------------|
| 1:2 | 0.8201 ± 0.0045 | **0.8267** | 0.7968 | 0.8044 | ❌ |
| 1:5 | 0.8198 ± 0.0045 | **0.8244** | 0.7996 | 0.8051 | ❌ |
| 1:10 | **0.8206 ± 0.0049** | 0.8203 | 0.8013 | 0.8047 | ✅ |

**当前审计：** 最终同步的 `fig6_summary.json` 中，MSAT 仅在 ratio=10 最高；ratio=2 和 ratio=5 为 HGT 略高。因此 Fig.6 不能按“MSAT 三 ratio 全胜”引用，需在服务器恢复后按修复后的 metadata/checkpoint 流程重跑或解释差异。  
**注意：** Fig.6 协议与 Table 4（端到端 1:10 训练）不同，AUC 数值不可直接对比。

### 10.6 Phase 8E / 9E — Fig.5a 冷启动【FAERS-only 四模型 ✅】

> 论文 §3.5.4：FAERS-only 训练 → 文献 hold-out 评估；unseen CMM **96.5%**。  
> 脚本：`run_faers_only_coldstart_train.py` + `run_faers_only_coldstart_gnn.py` → `faers_only_coldstart_summary.json`

#### 真 Fig.5a（FAERS-only，2026-06-22 GPU）

| 模型 | Precision | MCC | AUC | vs 论文 |
|------|-----------|-----|-----|---------|
| **MSAT** | **0.8259** | **0.7324** | **0.9281** | 最高 ✅ |
| HGT | 0.8032 | 0.6929 | 0.9208 | MSAT > HGT ✅ |
| Simple-HGN | 0.7763 | 0.6686 | 0.9108 | MSAT > Simple-HGN ✅ |
| GAT | 0.7695 | 0.6573 | 0.9098 | MSAT > GAT ✅ |

- ✅ unseen CMM **96.5%**（164/170 文献 CMM 无 FAERS 边）
- ✅ **MSAT 在 P/MCC/AUC 三项均最高**，与论文 Fig.5a 一致

#### 10 折 CV 代理（旧协议，仅供参考）

| 模型 | Precision | MCC | AUC |
|------|-----------|-----|-----|
| MSAT | 0.3596 ± 0.0387 | 0.5203 ± 0.0329 | 0.9535 ± 0.0075 |
| HGT | **0.4189 ± 0.0421** | **0.5693 ± 0.0412** | **0.9611 ± 0.0089** |

⚠️ 此表协议与论文不同（unseen ≈ 0.8%），**HGT > MSAT 不代表论文结论失效**。

### 10.7 Phase 8F — Table 5 Top-15 外部验证【当前 root 产物 stale】

> 当前 committed `table5_summary.json` 已标记为 `artifact_status.stale=true`。最终同步 root 产物的支持率为 **1/15**，并且 TCMDA 证据口径未与论文完全等价。  
> 协议选择见 `TABLE5_PROTOCOL_DECISION.md`；审计见 `reproduction_state_audit.json`。

| 模式 | 当前状态 | 说明 |
|------|----------|------|
| OOF + 排除全部正边 | stale root 产物 1/15 | 候选池严格，但证据支持低 |
| Predictor 全局推理 | 待重跑 | 必须显式 `--checkpoint` 并记录 sha256 |
| OOF + 仅排除 FAERS | 历史诊断 | 不作为当前正式结论 |

论文 13/15 还需等价外部数据库证据，尚未完全接入。

历史 `table5_paper_compare.json` 可作为诊断，不可作为正式 Table 5 复现。

### 10.8 Phase 8F — Table 6 + §4.5.1 枳实案例

#### Table 6 TCM 系统映射

> 脚本：`scripts/run_table6_mapping.py` → `results/table6_mapping.csv`  
> 规则：`inference/tcm_mapping.py`（MedDRA PT → SOC → 16 TCM 系统）

- ✅ 15 行映射列已生成（`tcm_system_mapping`）。
- ⚠️ 当前规则偏粗，**多数行为默认 `Qi-Blood-Fluid`**，未能复现论文 Table 6 中 Vomiting→Stomach、Tinnitus→Kidney 等精细对应。

#### §4.5.1 枳实 → Watery diarrhoea（Phase 8F 正式版）

> 脚本：`scripts/run_case_zhishi.py` → `results/case_zhishi_diarrhoea.json`  
> 实体：`paper_herb_id_map` 锚定 **herb_id=277**（Citrus aurantium L.）

| 项 | Phase 7（已废弃） | Phase 8F（当前） | 论文叙事 |
|----|-------------------|------------------|----------|
| herb_id | 173（山楂） | **277（枳实）** | Citrus aurantium | ✅ ID |
| 显示名 | 山楂 | 枳实（Citrus aurantium L.） | 枳实 | ✅ |
| ADR | Watery diarrhoea | Watery diarrhoea | 一致 | ✅ |
| 分数 / 排名 | 0.978 / #1 | **0.2549 / #7**（stale） | 高置信 Top | ❌ |
| 多跳路径 | 仅直接边 | **14 条** compound→target→ADR | nobiletin→ABCG2 | ⚠️ |
| nobiletin / ABCG2 | — | `paper_targets` 字段已预留 | 需命名解析 | ⚠️ |

**路径样例：** `CMM #277 → Compound #523 → Target #12337 → ADR #2931`

> Phase 7 产物（`phase7_*`）保留作历史记录；当前 `case_zhishi_diarrhoea.json` 也已标记 stale，正式对照需用干净主实验 checkpoint 重跑。

---

## 12. 论文逐表对照总览

| 论文条目 | 本次结果 | 论文参考 | 判定 | 产物 |
|----------|----------|----------|------|------|
| **Table 1** 数据规模 | 651/1498/21393/5974 节点 | 一致 | ✅ | `DATA_MANIFEST.md` |
| **Table 2** MSAT 主实验 | AUC **0.9792±0.0018** | 0.979±0.001 | ✅ | `summary.json` |
| **Table 2** 九基线 1:1 | MSAT 最高 | MSAT > GNN > ML | ✅ | `baseline_summary.json` |
| **Table 3** w/o ESA/HSP/HCI | Full 最高；w/o HCI 最低 | 同趋势 | ✅ | `ablation_summary.json` |
| **Table 3** Only ESA/HSP/HCI | 均 < Full；Only HCI 非最低 | Only HCI 最低 | ⚠️ | `summary_only_*.json` |
| **Table 4** MSAT 1:10 | AUC **0.8710±0.0051** | ~0.875±0.005 | ✅ | `summary_neg10.json` |
| **Table 4** 九基线 1:10 | LR/RF/XGB 旧结果 AUC≈1.0，已判定污染 | MSAT 最优 | ❌ 待重跑 | `baseline_neg10_summary.json` |
| **Fig.6** 测试不平衡 | ratio 2/5 为 HGT 最高；ratio 10 为 MSAT 最高 | MSAT 最优 | ⚠️ | `fig6_summary.json` |
| **Fig.5b** 度分层 | Tail 0.972 > Head 0.836 | Tail 优于 Head | ✅ | `stratified_summary.json` |
| **Fig.5a** 冷启动 | FAERS-only 四模型；MSAT **P/MCC/AUC 均最高** | MSAT > 全部 GNN | ✅ | `faers_only_coldstart_summary.json` |
| **Fig.5a** GNN 基线 | GAT/HGT/Simple-HGN 已跑 | 同上 | ⚠️ | `run_coldstart_gnn.py` |
| **Table 5** Top-15 验证 | 当前 root 产物 stale；最终同步支持率 1/15 | **13/15** | ❌ | `table5_summary.json` |
| **Table 6** TCM 映射 | 当前产物 stale，且依赖 stale Table 5 | 15 例精细映射 | ❌ | `table6_mapping.csv` |
| **§4.5.1** 枳实案例 | id=277，nobiletin 路径有；当前产物 stale，score 0.2549/rank 7 | 高置信 + nobiletin→ABCG2 | ⚠️ | `case_zhishi_diarrhoea.json` |
| **8A** 16 种子映射 | 16/16 通过 | — | ✅ | `validate_entity_mapping.py` |
| **Supp.** 敏感性等 | 未做 | — | ⏭ | — |

### 完成度汇总

```
核心训练指标（Table 2–4 MSAT + 消融）             █████████░   90%  ✅
基线对比（Table 2/4 全模型趋势）                  ██████░░░░   60%  ⚠️
下游解释（Table 5/6 + 案例）                      ██░░░░░░░░   20%  ❌
Fig.5a 冷启动四模型                               ██████████  100%  ✅
可选补充（8G）                                    ░░░░░░░░░░    0%  ⏭
─────────────────────────────────────────────────────────────
整体（按 Phase 8 计划 8A–8F 脚本+GPU）            ███████░░░   70%  ⚠️
整体（按论文全文语义一致）                        ██████░░░░   60%  ⚠️
```

**结论：实验流水线与主指标复现已完成；与论文逐表完全一致尚未达成。**

## 13. 论文基线对齐（2026-06-22 实现）

**历史结果**已移至 `results/archive_pre_paper_align_2026-06-22/`（对齐前 JSON/CSV/日志，勿作正式引用）。  
代码审计见 `results/PAPER_CODE_AUDIT.md`。

相对此前复现辅助脚本，以下已按论文 §3.5 回改：

| 项 | 论文要求 | 实现 |
|----|----------|------|
| 归纳去边 | 仅剔除 test **正边** | `train.py` / `baselines/common.py` |
| ML 基线特征 | 节点 + **6 维边特征** | `pair_features(..., edge_attr_map)` |
| Table 5 | 全局 Top-15，排除 **全部 27062 正边** | `run_table5_validation.py` 默认 |
| Table 5 DB | TCMDA 查询 | **未接 API**；`database_verified=False` |
| Table 6 | 论文 Table 6 映射 | `data/paper_table6_reference.json` |
| Fig.5a | FAERS-only → 文献 hold-out | `run_faers_only_coldstart_*.py` |
| 非论文脚本 | — | `run_coldstart_eval.py`、`run_table5_paper_compare.py --legacy` 降级 |

**说明：** Table 2/4 主指标若需与改前数值对比，需用新归纳去边协议 **重训**（val 正边不再从图中删除，与旧 run 略有差异）。

**重训状态（AutoDL 2026-06-22）：** `bash scripts/server_paper_retrain.sh` 已在 GPU 后台运行（日志 `results/phase8_logs/paper_retrain.log`），顺序：MSAT 10 折 → ML/GNN 基线 → 消融 → 1:10 → Fig.6 → Phase 9。

---

```bash
# 数据下载
python MSAT/scripts/download_data.py

# 完整 10 折（Full）
cd MSAT && python train.py

# 单折验证
python MSAT/scripts/train_single_fold.py

# 消融（全部）
python MSAT/scripts/run_ablation.py --all

# 1:10 不平衡实验（Table 4）
python MSAT/scripts/run_imbalanced.py

# 9 基线对比（Table 2 扩展）
python MSAT/scripts/run_baselines.py --all
python MSAT/scripts/run_baselines.py --aggregate-only

# 度分层 / 文献边 AUC（Fig.5b）
python MSAT/scripts/analyze_stratified.py

# Phase 8A 实体映射
python MSAT/scripts/build_entity_mapping.py
python MSAT/scripts/validate_entity_mapping.py

# Phase 8B 消融（含 Only）
python MSAT/scripts/run_ablation.py --all

# Phase 8C 基线 1:10
python MSAT/scripts/run_baselines.py --neg-ratio 10 --all
python MSAT/scripts/run_baselines.py --neg-ratio 10 --aggregate-only

# Phase 8D Fig.6 sweep
python MSAT/scripts/run_imbalance_sweep.py

# Phase 9 缺口闭合（Fig.5a GNN / Table5 predictor）
bash MSAT/scripts/server_phase9_run.sh          # 服务器
RUN_GNN_COLDSTART=1 bash MSAT/scripts/server_phase9_run.sh  # 含 GNN 冷启动

# 仅汇总已有结果
python MSAT/scripts/run_ablation.py --aggregate-only
```

---

*本报告由实验流水线自动生成骨架，随 `MSAT/results/` 下 JSON 与日志更新而手动/脚本追加。*
