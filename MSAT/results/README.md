# MSAT 复现结果目录

更新时间：2026-06-27

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
| `PU_XMSAT_FULL_MSAT_PILOT_REPORT.md` | PU-XMSAT full-backend pilot | full MSAT PU 后端可运行；corrected random50k full-positive random/10-fold 达到 AUC 0.9796、AUPRC 0.9773、F1 0.9321、MCC 0.8625，已达到 baseline-level，但提升很小且未达统计显著 |
| `PU_XMSAT_RESEARCH_PROGRESS_REPORT.md` | 后续论文素材积累 | 记录 PU-XMSAT 研究动机、prefix-cache caveat、corrected random50k budget scaling、10-fold corrected hybrid/random/full-positive pilot 和下一步稳健性计划 |

## 下一步重点

1. Table 5 当前应报告为公开材料下不可复现；若要重开，需要补 sha256 为 `506e7fd3...` 的 predictor checkpoint、Table 5 导出脚本、候选池定义和逐行证据记录。
2. 对 Table 3、Table 4、Fig.6 做定点差异分析，不重跑完整流水线。
3. PU-XMSAT 下一步不要继续使用旧 prefix candidate cache，也不要重复已完成的 corrected 12,288-pair 或 66,015-pair `random` 10-fold 对照；应优先补 paired fold/statistical note，再决定是否做 repeated seed、PU weight sensitivity 或 full-positive `hybrid` comparator。
4. 更新正文报告时，以本文件、`PROJECT_MEMORY.md` 和 `reproduction_state_audit.json` 为准，旧摘要文件仅作历史记录。
