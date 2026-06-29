# MSAT 复现结果目录

更新时间：2026-06-29

## 目录说明

| 位置 | 说明 |
|------|------|
| `results/` 根目录 | 当前有效 JSON/CSV 结果与复现报告 |
| `results/phase8_logs/` | 服务器训练与 Phase 9 日志，本地默认不入 Git |
| `server_results_2026-06-24/` | 本地保存的服务器原始结果包，已被 `.gitignore` 忽略 |
| `archive_pre_paper_align_2026-06-22/` | 论文协议对齐前历史产物，勿作为正式复现结果引用 |

## 引用前审计

每次同步或修改结果后先运行：

```bash
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error
```

当前最新审计结果：`issues: []`。

## 当前复现状态

| 文件 | 论文对应 | 当前状态 |
|------|----------|----------|
| `summary.json` | Table 2 MSAT 主实验 1:1 | 可引用；AUC 0.9793，AUPRC 0.9771 |
| `baseline_summary.json` | Table 2 九基线 1:1 | 可引用；MSAT AUC 最高 |
| `ablation_summary.json` | Table 3 消融 | 产物齐全；Full 非所有指标最高，需作为趋势差异报告 |
| `summary_neg10.json` | Table 4 MSAT 1:10 | 可引用为 MSAT 单模型；AUC 0.8710 |
| `baseline_neg10_summary.json` | Table 4 全模型 1:10 | 产物可审计；XGB AUC/AUPRC 略高于 MSAT，未完全复现论文排名 |
| `fig6_summary.json` | Fig.6 测试集不平衡 sweep | AUC/AUPRC 中 MSAT 全胜；F1/MCC 中 HGT 更高 |
| `faers_only_coldstart_summary.json` | Fig.5a FAERS-only 冷启动 | 可引用；MSAT 在 Precision/MCC/AUC 均优于 GNN baselines |
| `reproduction_gap_diagnosis.json` | Fig.5a/Table5 差异诊断 | 可引用；Table5 论文配对 15 行中 14 行可映射，只有 1 行进入 OOF 分数；本地 checkpoint 与服务器 Table5 manifest 不一致，且当前结果包无法恢复目标 checkpoint |
| `table5_top15.csv` / `table5_summary.json` | Table 5 Top-15 外部验证 | 产物有效但未复现论文支持率；当前 1/15，TCMDA 证据待补 |
| `table5_literature_evidence_candidates.csv` / `.json` | Table 5 公开文献候选 | PubMed/OpenAlex 自动候选 63 条；精确 herb+ADR 命中 0 条，仅供人工复核 |
| `table6_mapping.csv` / `table6_mapping.json` | Table 6 TCM 系统映射 | 产物有效但依赖当前 Table 5；映射规则仍偏粗 |
| `case_zhishi_diarrhoea.json` | §4.5.1 枳实案例 | 可作为当前 checkpoint 下的案例产物引用；与论文高置信案例仍需逐项说明差异 |
| `PU_XMSAT_FULL_MSAT_PILOT_REPORT.md` | PU-XMSAT full-backend pilot | full MSAT PU 后端可运行；corrected random50k full-positive random/10-fold seed=42 达到 AUC 0.9796、AUPRC 0.9773、F1 0.9321、MCC 0.8625；seed=2026 random 达到 AUC 0.9797、AUPRC 0.9777、F1 0.9338、MCC 0.8661；full-positive hybrid 两个 seed 稳定在 AUC 0.9804、AUPRC 0.9780、F1 0.9348-0.9351、MCC 0.8683-0.8684；权重敏感性支持默认 u0.2/rn0.8 是平衡设置 |
| `PU_XMSAT_DELIVERABLE_INDEX_CN.md` | PU-XMSAT 交付物索引 | 当前阶段总入口；按导师沟通、口头汇报、PPT、论文写作、统计源和下一步任务说明应打开哪个文件 |
| `PU_XMSAT_RESEARCH_PROGRESS_REPORT.md` | 后续论文素材积累 | 记录 PU-XMSAT 研究动机、prefix-cache caveat、corrected random50k budget scaling、10-fold corrected hybrid/random/full-positive pilot、repeated-seed robustness、full-positive hybrid two-seed comparator、PU weight sensitivity 和下一步论文整理计划 |
| `PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md` | PU-XMSAT 论文结果草稿 | 论文可用结果表、paired statistics、seed robustness、weight sensitivity 和建议/禁用措辞；后续写正文优先引用 |
| `PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` | PU-XMSAT 正文段落草稿 | Methods、Results、Discussion 英文正文草稿；适合作为论文正文初稿继续润色 |
| `PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md` / `manuscript_package_audit.json` | Overleaf 论文包审计 | 由 `scripts/audit_manuscript_package.py` 生成；当前审计 `ok: true`、failed checks 0、warning checks 1，记录 `Template/PU-XMSAT-Overleaf` 源码、上传 zip、PDF 页数/纸张、LaTeX 日志、zip 必要/禁止条目和仍需导师确认的占位项 |
| `PU_XMSAT_MENTOR_PROGRESS_BRIEF_CN.md` | PU-XMSAT 中文阶段汇报 | 可直接用于导师沟通的中文汇报草稿；概括 MSAT 主实验复现、Table 5/6 边界、PU-XMSAT 动机、主要结果、结论边界和下一步建议 |
| `PU_XMSAT_ORAL_BRIEF_CN.md` | PU-XMSAT 口头汇报稿 | 3-5 分钟导师沟通或组会口头稿；按“开场、复现边界、方法动机、主要结果、下一步”组织 |
| `PU_XMSAT_SLIDES_OUTLINE_CN.md` | PU-XMSAT 组会/答辩 slides 大纲 | 10-12 页 PPT 结构草稿；逐页给出标题、核心信息、建议视觉和讲稿提示 |
| `PU_XMSAT_SLIDES_DRAFT_CN.pptx` | PU-XMSAT 组会/答辩 PPT 初稿 | 由 slides 大纲生成的 12 页可编辑 PowerPoint；已渲染检查主要表格/图表页，适合继续人工美化或直接用于组会初稿 |
| `PU_XMSAT_CASE_EVIDENCE_REPORT.md` / `case_evidence_report.json` / `.csv` | 机制解释与外部证据分级最小闭环 | 当前 16 行案例候选中 2 行有机制支持（Grade C）、14 行为预测候选（Grade D）；8 行有自动检索记录，但 0 行具备人工核验直接文献强证据 |
| `PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md` / `case_evidence_manual_review.json` | Grade C 人工证据核验 | 两个 Grade C 均不应升级：野草莓-意识状态改变外部证据不支持；枳实-水样腹泻有胃肠机制相关证据但方向冲突 |
| `PU_XMSAT_CASE_SELECTION_DECISION.md` | 案例选择决策 | 当前没有强外部验证正向案例；案例部分应写成保守筛选流程，而非确认性验证 |
| `PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md` / `contribution_quantification.json` / `.csv` | 关键机制子图与贡献量化 | 已完成 2 个机制案例的关键子图、节点置零和路径置零扰动评分；枳实案例子图含 11 个节点/8 条边，最高节点为 `target:3223`（drop 0.009835），最高路径为 `compound:523 -> target:3223`（drop 0.010074）；野草莓案例扰动下降接近 0；这是本地 predictor checkpoint 下的敏感性分析，不是因果效应，也不是最终 PU checkpoint 归因 |
| `PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md` / `contribution_aggregate_summary.json` / `.csv` | 贡献量化聚合摘要 | 已把 2 个机制案例的节点/路径扰动结果聚合成 top path 和 top node 表；当前共有 7 条正向 node 扰动、10 条正向 path 扰动，最强路径仍为 `compound:523;target:3223`（mean/max drop 0.010074），最强节点为 `target:3223`（drop 0.009835）；该聚合仍是本地 predictor checkpoint 下的 perturbation sensitivity，不是因果、SHAP 或外部验证 |
| `PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md` / `direction3_targeted_review_queue.json` / `.csv` | 方向三定向证据复核队列 | 已按方向二扰动敏感性排序当前 2 个机制案例：枳实-水样腹泻排第 1、野草莓-意识状态改变排第 2；两者均已人工核验且仍为 Grade C boundary cases，ready strong-evidence cases 为 0 |
| `PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` | 因果偏倚框架 | 已完成当前数据条件下的 DAG/混杂因素边界说明；用于讨论 co-medication、indication、reporting bias、exposure population 等不能由当前图数据严格校正的因素 |
| `PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md` | 研究闭环审计 | 将 `RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md` 的训练、解释、验证和因果边界要求逐项映射到当前产物；明确当前已形成最小论文闭环，但不能声称 Table 5/6 完整复现或因果效应 |
| `pu_xmsat_baseline_comparison.json` / `.csv` | PU-XMSAT vs MSAT paired fold comparison | 可引用；full-positive random 相对 MSAT 的 AUC/AUPRC/F1 均值略高，MCC 持平，paired t-test 均不显著 |
| `pu_xmsat_seed2026_baseline_comparison.json` / `.csv` | PU-XMSAT seed=2026 vs MSAT paired fold comparison | 可引用为稳健性复跑统计；AUC/AUPRC/F1/MCC 均值均略高于 MSAT，但 paired t-test 仍未过 0.05 |
| `pu_xmsat_hybrid_seed2026_baseline_comparison.json` / `.csv` | PU-XMSAT hybrid seed=2026 vs MSAT paired fold comparison | 可引用为当前最强比较；AUC/AUPRC/F1/MCC 均值均高于 MSAT，paired t-test 均过 0.05，但仍需额外稳健性支持最终 superiority claim |
| `pu_xmsat_hybrid_vs_random_seed2026_comparison.json` / `.csv` | PU-XMSAT hybrid vs random seed=2026 strategy comparison | 可引用为采样策略比较；hybrid 在 AUC/F1/MCC 上显著高于 random，AUPRC 略高但不显著 |
| `pu_xmsat_hybrid_seed1337_baseline_comparison.json` / `.csv` | PU-XMSAT hybrid seed=1337 vs MSAT paired fold comparison | 可引用为第二 seed 稳健性；AUC/F1/MCC 显著高于 MSAT，AUPRC 正向但 p=0.056 |
| `pu_xmsat_hybrid_seed_robustness_summary.json` / `.csv` | PU-XMSAT hybrid two-seed robustness summary | 可引用为稳健性汇总；两个 hybrid seed 的 AUC/AUPRC/F1/MCC 均值范围分别只有 0.000028/0.000054/0.000297/0.000078 |
| `pu_xmsat_hybrid_weight_sensitivity_summary.json` / `.csv` | PU-XMSAT hybrid PU weight sensitivity | 可引用为权重敏感性；u0.1 低于默认，u0.4 与默认接近但 F1/MCC 略低，支持默认 u0.2/rn0.8 |

## 下一步重点

1. Table 5 当前应报告为公开材料下不可复现；若要重开，需要补 sha256 为 `506e7fd3...` 的 predictor checkpoint、Table 5 导出脚本、候选池定义和逐行证据记录。
2. 对 Table 3、Table 4、Fig.6 做定点差异分析，不重跑完整流水线。
3. PU-XMSAT 下一步不要继续使用旧 prefix candidate cache，也不要重复已完成的 corrected 12,288-pair、66,015-pair `random` 10-fold 对照、seed=2026 repeated-seed run、full-positive `hybrid` seed=2026/1337 comparator 或 u0.1/u0.4 weight sensitivity；后续优先从 `PU_XMSAT_DELIVERABLE_INDEX_CN.md` 选择入口，再基于 `PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md`、`PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md`、`PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md`、`manuscript_package_audit.json`、`PU_XMSAT_MENTOR_PROGRESS_BRIEF_CN.md`、`PU_XMSAT_ORAL_BRIEF_CN.md`、`PU_XMSAT_SLIDES_OUTLINE_CN.md`、`PU_XMSAT_SLIDES_DRAFT_CN.pptx`、`PU_XMSAT_CASE_EVIDENCE_REPORT.md`、`PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md`、`PU_XMSAT_CASE_SELECTION_DECISION.md`、`PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`、`PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`、`PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md`、`PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` 和 `PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md` 润色论文正文、中文汇报、组会 slides、外部证据和解释层结果。
4. 更新正文报告时，以本文件、`PROJECT_MEMORY.md` 和 `reproduction_state_audit.json` 为准，旧摘要文件仅作历史记录。
