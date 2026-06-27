# PU-XMSAT 当前交付物索引

**日期：** 2026-06-27
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
| 写论文结果表 | `results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md` | PU-XMSAT 主结果表、paired statistics、seed robustness、weight sensitivity 和建议措辞 |
| 写英文 Methods/Results/Discussion | `results/PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` | 英文正文段落草稿 |
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

## 4. 当前可以说的结论

可以说：

1. MSAT 主实验与多数核心性能结果已经复现，当前审计结果为 `issues: []`。
2. Table 5/6 属于外部验证和解释性案例，不是主性能实验；公开材料下不能论文等价复现。
3. Random PU-XMSAT 达到 baseline-level，可作为 PU 学习可行性和消融对照。
4. Full-positive hybrid PU-XMSAT 是当前最强设置，在两个 seed 下对 AUC、F1、MCC 有稳定提升。
5. AUPRC 保持正向趋势，但提升幅度较小，其中一个 seed 相对 MSAT 的 AUPRC paired p 值为边界显著。
6. 权重敏感性支持 `u0.2/rn0.8` 作为当前默认设置。

不要说：

1. 不要说全文 100% 复现。
2. 不要说 Table 5/6 已经完整复现。
3. 不要说 PU-XMSAT 全面、绝对、无条件优于 MSAT。
4. 不要把旧 prefix-cache pilot 当作策略优劣证据。
5. 不要隐藏 AUPRC 的边界和较小提升。

## 5. 推荐下一步顺序

当前不建议继续重复长时间训练，除非发现新的代码或数据问题。更合理的推进顺序是：

1. **PPT 人工美化。** 以 `PU_XMSAT_SLIDES_DRAFT_CN.pptx` 为基础，补充学校/课题组模板、页脚、图例细节和口头节奏。
2. **论文正文整理。** 以 `PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md` 和 `PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` 为基础，形成正式论文 Methods/Results/Discussion。
3. **外部证据和案例分析。** 不再强行宣称 Table 5 等价复现，而是把 Table 5/6 作为外部验证难点和解释性分析入口。
4. **下一代模型方向。** 结合导师建议，继续调研因果混杂控制、关键子图解释、SHAP/注意力解释和更严格可靠负样本策略。

## 6. 每次修改结果后要跑的检查

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests -q
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
