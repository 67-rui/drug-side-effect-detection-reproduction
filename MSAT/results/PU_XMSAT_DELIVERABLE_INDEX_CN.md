# PU-XMSAT 当前交付物索引

**日期：** 2026-06-30
**分支：** `codex/pu-xmsat-implementation`
**用途：** 作为当前 PU-XMSAT 研究阶段的交付物入口。后续写论文、组会汇报、导师沟通或继续开发时，优先从本文件选择应打开的材料。

## 1. 一句话状态

当前项目已经完成 MSAT 主实验复现和协议审计，主实验结果可作为复现基线；Table 5/6 在公开材料下不能论文等价复现，应作为外部验证和解释性案例边界处理。在此基础上，PU-XMSAT 已完成 corrected random-cache、full-positive hybrid two-seed、hybrid-vs-random、PU 权重敏感性等关键实验，当前最稳妥的研究结论是：

> Full-positive hybrid PU-XMSAT 在两个 seed 下对 AUC、F1、MCC 表现出稳定提升，AUPRC 保持正向趋势但幅度较小；默认 `unlabeled_weight=0.2/reliable_negative_weight=0.8` 是当前较平衡的设置。

## 2. 按使用场景选择文件

| 场景 | 优先打开文件 | 用途 |
| --- | --- | --- |
| 快速了解当前项目状态 | `PROJECT_MEMORY.md`、`results/README.md` | 了解复现边界、当前分支、结果目录和不要重复做的实验 |
| 给导师发阶段进展 | `results/PU_XMSAT_MENTOR_PROGRESS_BRIEF_CN.md` | 中文阶段汇报，适合邮件、微信或组会前材料 |
| 3-5 分钟口头汇报 | `results/PU_XMSAT_ORAL_BRIEF_CN.md` | 可直接照着讲的口头稿 |
| 做组会或答辩 PPT | `results/PU_XMSAT_SLIDES_DRAFT_CN.pptx` | 12 页可编辑 PowerPoint 初稿 |
| 修改 PPT 内容结构 | `results/PU_XMSAT_SLIDES_OUTLINE_CN.md` | PPT 页级大纲，包含每页标题、核心信息、建议视觉和讲稿提示 |
| 写论文结果表 | `results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md` | PU-XMSAT 主结果表、paired statistics、seed robustness、weight sensitivity、案例证据边界和建议措辞 |
| 做投稿前总审阅 | `results/PU_XMSAT_NEXT_PUBLICATION_ACTION_REPORT.md` | 当前已完成内容、论文可写内容、解释性完成度、case-study 候选、投稿前 todo、等待原作者事项和提交/推送建议 |
| 检查投稿级主结果证据 | `results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md`、`results/pu_xmsat_publication_evidence_consolidation.json` | Package A：整合 baseline、hybrid two-seed、random comparator、seed robustness 和 weight sensitivity，作为正文数字核对入口 |
| 检查聚类留类泛化实验 | `results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`、`results/cluster_holdout_generalization_summary.json`、`results/pu_xmsat_cluster_holdout_hybrid_seed2026_10cluster_200e_66015p_valf1.json` | Package B：正式 10-cluster/10-fold/200-epoch cluster-heldout 已完成；all-fold 与 non-tiny robust summary 均已生成，用于写新中药簇泛化压力测试和 claim boundary |
| 写英文 Methods/Results/Discussion | `results/PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` | 英文正文段落草稿 |
| 检查 Overleaf 论文包 | `results/PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md`、`results/manuscript_package_audit.json`、`results/PU_XMSAT_MANUSCRIPT_CLAIM_AUDIT.md`、`../Template/PU-XMSAT-Overleaf/README.md` | 当前 ACM 模板稿件位置、上传 zip、模板验证状态、PDF/LaTeX/zip 审计、论文 claim boundary、占位项和打包规则 |
| 判断是否可以正式投稿 | `results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md`、`results/submission_readiness_audit.json` | 区分机器可验证 package 状态和必须由学生/导师确认的最终投稿 blockers |
| 写解释性/外部证据案例 | `results/PU_XMSAT_FINAL_CHECKPOINT_EXPORT_REPORT.md`、`results/PU_XMSAT_INTERPRETABILITY_GAP_AUDIT.md`、`results/PU_XMSAT_TOP_PREDICTIONS_TOP5000_EXPORT.md`、`results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`、`results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md`、`results/PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md`、`results/PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md`、`results/PU_XMSAT_ENTITY_MAPPING_AUDIT_AND_CANDIDATES.md`、`results/PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md`、`results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`、`results/PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`、`results/PU_XMSAT_TOP30_MANUAL_EVIDENCE_REVIEW.md`、`results/top30_manual_evidence_review.csv`、`results/PU_XMSAT_CASE_STUDY_TRIAGE_TABLE.md`、`results/PU_XMSAT_ORIGINAL_AUTHOR_MAPPING_REQUEST.md`、`results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md`、`results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md`、`results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE_TOP5000_RANDOM_CONTROLS.md` | final checkpoint export、top5000 top prediction、batch 机制解释、机制子图、成分/靶点/路径扰动贡献量化、random controls、实体映射缺口审计、target 候选名称、top20 外部证据 first-pass 复核、391 候选 evidence-aware 重排序、PubMed 信号筛查、top30 手工证据复核模板、case-study triage 表、原作者映射请求和方向三定向复核队列；当前没有强完整链外部验证案例 |
| 写因果/局限性边界 | `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` | 当前数据条件下的 DAG/混杂因素框架；说明哪些偏倚只能讨论、不能严格校正 |
| 判断计划是否闭环 | `results/PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md` | 把研究方案中的训练、解释、验证、因果边界逐项映射到当前证据 |
| 追溯完整实验过程 | `results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`、`results/PU_XMSAT_FULL_MSAT_PILOT_REPORT.md` | 记录 candidate cache 修正、budget scaling、10-fold pilot、two-seed 和 weight sensitivity |
| 检查复现状态是否干净 | `results/reproduction_state_audit.json` | 当前审计结果应保持 `issues: []` |

## 3. 当前最权威的统计源

写论文、汇报或 PPT 时，优先引用 tracked CSV/JSON，而不是手工从原始训练日志里摘数字。

| 统计问题 | 权威文件 |
| --- | --- |
| MSAT 主实验基线 | `results/summary.json` |
| random PU-XMSAT vs MSAT | `results/pu_xmsat_baseline_comparison.csv`、`results/pu_xmsat_seed2026_baseline_comparison.csv` |
| hybrid seed=2026 vs MSAT | `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv` |
| hybrid seed=1337 vs MSAT | `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv` |
| hybrid vs random | `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv` |
| hybrid two-seed robustness | `results/pu_xmsat_hybrid_seed_robustness_summary.csv` |
| PU 权重敏感性 | `results/pu_xmsat_hybrid_weight_sensitivity_summary.csv` |
| 投稿级主结果整合 | `results/pu_xmsat_publication_evidence_consolidation.json`、`results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md` |
| 投稿前推进与 case-study 候选 | `results/PU_XMSAT_NEXT_PUBLICATION_ACTION_REPORT.md` |
| cluster-heldout 正式泛化实验 | `results/pu_xmsat_cluster_holdout_hybrid_seed2026_10cluster_200e_66015p_valf1.json`、`results/cluster_holdout_generalization_summary.json`、`results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md` |
| cluster-heldout pilot | `results/cluster_holdout_pilot.json`、`results/cluster_holdout_pilot_summary.json`、`results/PU_XMSAT_CLUSTER_HOLDOUT_PILOT_SUMMARY.md` |
| 机制解释与证据分级案例 | `results/case_evidence_report.json`、`results/case_evidence_report.csv`、`results/PU_XMSAT_CASE_EVIDENCE_REPORT.md` |
| Grade C 人工核验证据 | `results/case_evidence_manual_review.json`、`results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md` |
| 案例是否可写成强验证 | `results/PU_XMSAT_CASE_SELECTION_DECISION.md` |
| 解释 checkpoint gap | `results/PU_XMSAT_INTERPRETABILITY_GAP_AUDIT.md` |
| Final checkpoint export 状态 | `results/PU_XMSAT_FINAL_CHECKPOINT_EXPORT_REPORT.md` |
| PU-XMSAT top predictions 正式 top5000 | `results/pu_xmsat_top_predictions_top5000.json`、`results/pu_xmsat_top_predictions_top5000.csv`、`results/PU_XMSAT_TOP_PREDICTIONS_TOP5000_EXPORT.md` |
| Batch 机制解释正式 top5000/random controls | `results/batch_mechanism_interpretability_top5000_random_controls.json`、`results/batch_mechanism_interpretability_top5000_random_controls.csv`、`results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md` |
| 关键机制子图与贡献量化正式 top5000/random controls | `results/contribution_quantification_top5000_random_controls.json`、`results/contribution_quantification_top5000_random_controls.csv`、`results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md` |
| 贡献量化聚合摘要正式 top5000/random controls | `results/contribution_aggregate_summary_top5000_random_controls.json`、`results/contribution_aggregate_summary_top5000_random_controls.csv`、`results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md` |
| 解释层正式总入口 | `results/mechanism_explanation_layer_top5000_random_controls.json`、`results/mechanism_explanation_layer_top5000_random_controls.csv`、`results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md` |
| 方向三定向证据复核队列正式 top5000/random controls | `results/direction3_targeted_review_queue_top5000_random_controls.json`、`results/direction3_targeted_review_queue_top5000_random_controls.csv`、`results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE_TOP5000_RANDOM_CONTROLS.md` |
| top20 实体映射队列 | `results/top20_entity_mapping_queue.json`、`results/top20_entity_mapping_queue.csv`、`results/PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md` |
| top20 target 候选名称 | `results/top20_target_name_candidates.json`、`results/top20_target_name_candidates.csv`、`results/PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md` |
| 实体映射审计与候选边界 | `results/PU_XMSAT_ENTITY_MAPPING_AUDIT_AND_CANDIDATES.md` |
| top20 外部证据 first-pass 复核 | `results/top20_external_evidence_review.json`、`results/PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md` |
| evidence-aware top30 复核队列 | `results/evidence_aware_mechanism_candidate_queue.json`、`results/evidence_aware_mechanism_candidate_queue.csv`、`results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md` |
| evidence-aware PubMed 信号筛查 | `results/evidence_aware_literature_candidates.json`、`results/evidence_aware_literature_candidates.csv`、`results/PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md` |
| top30 手工证据复核模板 | `results/PU_XMSAT_TOP30_MANUAL_EVIDENCE_REVIEW.md`、`results/top30_manual_evidence_review.csv` |
| 论文 case-study triage 表 | `results/PU_XMSAT_CASE_STUDY_TRIAGE_TABLE.md` |
| 原作者数据/脚本请求 | `results/PU_XMSAT_ORIGINAL_AUTHOR_MAPPING_REQUEST.md`、GitHub issue `BowenShiGDPU/MSAT#1`，已补充 Table 5/6 所需材料 |
| 因果偏倚框架 | `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` |
| 研究闭环审计 | `results/PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md` |
| Overleaf 论文包审计 | `results/manuscript_package_audit.json`、`results/PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md` |
| 投稿就绪审计 | `results/submission_readiness_audit.json`、`results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md` |

## 4. 当前可以说的结论

可以说：

1. MSAT 主实验与多数核心性能结果已经复现，当前审计结果为 `issues: []`。
2. Table 5/6 属于外部验证和解释性案例，不是主性能实验；公开材料下不能论文等价复现。
3. Random PU-XMSAT 达到 baseline-level，可作为 PU 学习可行性和消融对照。
4. Full-positive hybrid PU-XMSAT 是当前最强设置，在两个 seed 下对 AUC、F1、MCC 有稳定提升。
5. AUPRC 保持正向趋势，但提升幅度较小，其中一个 seed 相对 MSAT 的 AUPRC paired p 值为边界显著。
6. 权重敏感性支持 `u0.2/rn0.8` 作为当前默认设置。
7. 机制解释与外部证据分级已经形成正式 batch-level 解释闭环：final top5000 中显式机制路径覆盖为 391/5000（7.82%），其中 top-50/top-100/top-500/top-1000 覆盖为 1/50、8/100、31/500、64/1000；20 个 mechanism-supported candidates 已完成扰动量化和 random-control 对照；方向三复核队列中 Grade A/B 强外部证据仍为 0，`ready_strong_evidence_count=0`。
8. 解释层已经完成 formal checkpoint-aware top5000/random-control 重跑：seed=2026 full-positive hybrid PU-XMSAT 10-fold checkpoint export 完成，mean AUC/AUPRC/F1/MCC 为 0.980281/0.977907/0.934326/0.867061；top component 为 `compound:761`，top target 为 `target:15721`，top pathway 为 `target:15721`。后续新增 top20 实体映射审计显示 20 个 compound 和 39 个 target 均无 confirmed 本地真实名称映射；HGNC/BioBERT 只生成 target `candidate_only` 候选，不能伪装成已命名真实机制。可以写成 checkpoint-aware batch-level mechanism triage，不能写成广泛系统机制确认、因果效应、SHAP、临床验证或强外部证据。
9. Top20 外部证据 first-pass 复核已经完成：强完整链证据 0/20，中等间接支持 1/20，弱/边界支持 2/20。最适合论文讨论的是 `Polypodium glycyrrhiza` 胃肠方向 triage case；`Fragaria vesca L.` 更适合写成边界/负例，说明扰动敏感性不能替代外部验证。
10. Package A 已新增投稿级证据整合入口，避免主结果、ablation、seed robustness 和 weight sensitivity 数字漂移；Package B 已完成 10-cluster/10-fold/200-epoch cluster-heldout 正式实验，all-fold mean AUC/AUPRC/F1/MCC 为 0.8891/0.9032/0.1770/0.1919，排除少于 5 味中药 heldout clusters 后的 non-tiny robust mean 为 0.8433/0.8633/0.0743/0.1168，应写成新中药簇泛化压力测试而非简单胜利；Package C 已完成 top5000 coverage、20 个 mechanism-supported candidates、子图提取、贡献量化、random controls、fallback display/name_source、实体映射审计、target 候选名称、top20 evidence review、391 候选 evidence-aware top30 重排序和 case-study triage 表。PubMed exact-query first-pass 在 top30 中保留 2 条 `Marchantia polymorpha` -> liver injury 文本匹配，但方向更像护肝/损伤模型，不能升级为强外部验证；Marchantia liver injury 的 formal final targeted perturbation 仍需恢复对应 `.pt` 权重后再补。
11. 原始 compound/target 映射桥已确认是当前生物语义解释的硬短板：Zenodo API 显示公开 record 仅含 `complete_hetero_graph.pt`，GitHub API 显示公开仓库 `data/` 仅含 `10fold_cv_split.pkl`，图内部 compound/target 节点 store 只有 `x`。已向原作者提交 GitHub issue 请求 local row index 到 PubChem/SMILES/HGNC/UniProt/source ID 的映射表，并追加 Table 5 导出脚本/checkpoint/候选池定义/逐行证据记录与 Table 6 PT/SOC->TCM 系统映射规则请求：https://github.com/BowenShiGDPU/MSAT/issues/1。
12. 因果图方向已经完成当前阶段的边界化处理：当前只能建立 co-medication、indication、reporting bias、exposure population 等混杂因素的 DAG/偏倚框架，不能声称已经进行严格因果校正。
13. 研究方案已经形成最小论文闭环：训练层、解释层、验证层和因果边界都有对应产物；后续重点应转向论文整合和必要的定向补强，而不是盲目扩展。
14. Overleaf 论文工程已经整理到 `Template/PU-XMSAT-Overleaf`，上传包为 `Template/PU-XMSAT-Overleaf.zip`；`scripts/audit_manuscript_package.py` 当前审计结果为 `ok: true`、failed checks 0、warning checks 1；PDF 编译为 15 页 Letter 纸。投稿就绪审计显示 package OK 且 machine failures 0，但 ready for submission 仍为 no，因为作者、机构、目标 venue、CCS、基金、AI 声明、双盲策略和参考/图件范围仍需学生/导师确认。

不要说：

1. 不要说全文 100% 复现。
2. 不要说 Table 5/6 已经完整复现。
3. 不要说 PU-XMSAT 全面、绝对、无条件优于 MSAT。
4. 不要把旧 prefix-cache pilot 当作策略优劣证据。
5. 不要隐藏 AUPRC 的边界和较小提升。
6. 不要把自动检索到但未人工核验的文献记录当成 Grade B 强证据。
7. 不要把枳实案例写成“已证明导致水样腹泻”；当前外部证据更适合写成胃肠/转运体机制相关但方向未确认。
8. 不要把贡献量化中的 score drop 写成 SHAP 值、因果贡献或临床机制证明；它只是输入节点/路径置零后的局部扰动敏感性。
9. 不要把当前 batch candidates 写成 final PU-XMSAT top-ranking export；除非 `pu_xmsat_top_predictions.json` 明确来自 final checkpoint export 且 `is_final_10fold_export=true`，否则必须写成 transitional 或 nonfinal PU top export。
10. 不要写 PU-XMSAT 已控制合并用药、适应症偏倚、报告偏倚或暴露人群差异；当前只是明确这些偏倚的分析框架和限制。

## 5. 推荐下一步顺序

导师新增建议后，当前最合理的推进顺序是先补强解释层，再把“聚类留一类测试”作为独立泛化实验设计，二者不要混在同一段结果里：

1. **论文正文合并。** 将 Package A/B/C 与新增 top20 entity/evidence 审计写进 Overleaf：主性能作为核心贡献，cluster-heldout 作为严格泛化边界，top5000 解释作为机制 triage。
2. **解释性段落保守重写。** 不再追求“强解释性”措辞；改写成 key mechanism subgraph extraction + perturbation-based component/target/pathway sensitivity + evidence-aware candidate triage。
3. **更严格泛化补强。** 如果导师继续追问泛化，可考虑 cluster-balanced holdout 或重复不同聚类种子；当前 10-cluster all-fold 与 non-tiny robust summary 已足够说明 cold-cluster 明显更难。
4. **实体名映射长期补强。** 若能获得原作者节点字典或可复现 ccTCM/ETCM source-ID bridge，再把 candidate_only target/compound 升级为 confirmed mapping；在此之前不要人工猜名。

## 6. 每次修改结果后要跑的检查

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests -q
PYTHONPATH=. python scripts/build_case_evidence_report.py
PYTHONPATH=. python scripts/run_contribution_quantification.py --max-cases 2 --max-features 0 --device cpu
PYTHONPATH=. python scripts/run_batch_mechanism_interpretability.py
PYTHONPATH=. python scripts/summarize_contribution_quantification.py --input results/batch_mechanism_interpretability.json --output-json results/contribution_aggregate_summary.json --output-csv results/contribution_aggregate_summary.csv --output-md results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md --top-k 10
PYTHONPATH=. python scripts/build_mechanism_explanation_layer.py --input results/contribution_quantification.json --output-json results/mechanism_explanation_layer.json --output-csv results/mechanism_explanation_layer.csv --output-md results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER.md --top-k 10
PYTHONPATH=. python scripts/build_direction3_targeted_review_queue.py
PYTHONPATH=. python scripts/audit_manuscript_package.py --output-json results/manuscript_package_audit.json --output-md results/PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md
PYTHONPATH=. python scripts/audit_submission_readiness.py --manuscript-dir ../Template/PU-XMSAT-Overleaf --package-audit results/manuscript_package_audit.json --output-json results/submission_readiness_audit.json --output-md results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md
PYTHONPATH=. python scripts/verify_pu_xmsat_baseline.py
PYTHONPATH=. python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error
```

如果修改了 PPTX，应额外确认：

1. PPTX 可以正常打开或被 artifact-tool 反向导入；
2. 关键结果页没有表格换行、文字遮挡或图表坐标异常；
3. PPTX 内不包含服务器地址、SSH 密码、临时密钥路径或其他敏感信息。

## 7. 当前不建议重复的工作

不要重复以下已完成实验，除非发现代码或数据 bug：

1. 旧 prefix candidate cache 相关 pilot；
2. corrected 12,288-pair 10-fold pilot；
3. corrected 66,015-pair random seed=42 10-fold；
4. corrected random seed=2026 robustness run；
5. full-positive hybrid seed=2026/1337 comparator；
6. u0.1/u0.4 PU weight sensitivity。

后续如果新增实验，应优先围绕“外部证据、解释性、因果混杂或更严格可靠负样本策略”设计，而不是无目的延长训练。
