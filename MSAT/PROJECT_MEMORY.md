# MSAT 项目外部记忆

**最后更新：** 2026-06-29
**用途：** 作为后续对话、上下文压缩、代码修改和实验判断的长期外部记忆。后续如果上下文被压缩，必须先读本文件，再回答项目状态、复现程度、下一步计划或代码方向问题。
**项目根目录：** `/Users/a67_2024/Desktop/drug-detect`
**核心实现目录：** `MSAT/`

## 0. 使用规则

后续接续本项目时，以本文件作为入口，但不要只依赖本文件。需要按以下顺序交叉核对：

1. `MSAT/results/README.md`：当前结果目录的引用规则和最新状态摘要。
2. `MSAT/results/reproduction_state_audit.json`：当前结果是否有 stale artifact、缺失 metadata、可疑 ML 泄漏等问题。
3. `MSAT/results/summary.json`、`baseline_summary.json`、`summary_neg10.json`、`baseline_neg10_summary.json`、`fig6_summary.json`、`faers_only_coldstart_summary.json`：当前可引用数值结果。
4. `MSAT/results/TABLE5_PROTOCOL_DECISION.md` 与 `MSAT/results/reproduction_gap_diagnosis.json`：Table 5 是否可复现的权威判断。
5. `MSAT/results/RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md` 与 `MSAT/results/RESEARCH_DIRECTION_IMPLEMENTATION_PLAN.md`：未来研究方向与实现计划。
6. `MSAT/results/REPRODUCTION_REPORT.md`、`VERIFICATION_FINDINGS.md`、`PAPER_CODE_AUDIT.md`：历史过程和辅助解释；如果与 2026-06-24 之后的结果目录摘要冲突，以 `results/README.md` 和审计 JSON 为准。

不要把早期会话、旧报告、旧 `PROJECT_MEMORY.md` 中的判断直接当作当前事实。尤其要注意：6 月 23 日前后的报告曾经记录“结果需重跑”或“产物 stale”，但 6 月 24 日已经同步了新服务器结果并通过结果审计。

## 1. 项目最初需求

本项目最初目标是复现论文：

- Shi et al. (2026), **“MSAT: a FAERS-informed heterogeneous graph neural network for pharmacovigilance prediction of Chinese materia medica-associated adverse drug reactions”**, *Frontiers in Pharmacology* 17:1774128.
- 本地论文 PDF：`resource_副本/fphar-17-1774128.pdf`
- 官方代码副本：`resource_副本/MSAT-main/`
- 本地扩展实现：`MSAT/`

最初需求不是简单运行作者代码，而是：

1. 对照论文、官方代码、官方数据和本地实现，判断是否真实复现论文结果。
2. 检查代码是否对齐论文协议和数据，尤其是官方 10 折、归纳式边隐藏、负采样比例、Table 2/3/4/Fig.5/Fig.6/Table 5/Table 6。
3. 修复代码中的协议偏差、泄漏、checkpoint 覆盖和产物污染问题。
4. 在服务器上完成必要长训，拉回结果并审计。
5. 判断当前复现完成度，明确哪些结果可引用、哪些不能引用。
6. 在复现基础上形成后续研究方向，回应导师提出的方向：因果图、可解释性、负采样、大模型/外部证据。

## 2. 仓库和资源状态

GitHub 仓库：

- Remote：`git@github.com:67-rui/drug-side-effect-detection-reproduction.git`
- 用户提供链接：`https://github.com/67-rui/drug-side-effect-detection-reproduction.git`
- 基线分支：`codex/fix-reproduction-protocol`
- 当前 PU-XMSAT 开发分支：`codex/pu-xmsat-implementation`

重要目录：

- `resource_副本/`：论文 PDF、官方最小代码、6 月 23 日 Cursor/会话进度摘要。
- `MSAT/`：当前真正使用的复现与扩展实现。
- `MSAT/results/`：当前结果、报告、审计和未来方案文档。
- `MSAT/data/`：官方 split、实体映射、Table 5/6 参考、TCMDA 缓存。
- `MSAT/saved_models/`：本地 checkpoint。注意：当前本地 `best_model_for_prediction.pt` 与服务器生成 Table 5 的 checkpoint sha 不一致。
- `MSAT/server_results_2026-06-24/`：服务器结果包，本地保存但默认不入 Git。
- `docs/superpowers/plans/`：阶段计划和修复计划，包括 6 月 18 日复现计划、6 月 22 日 Phase 8/9、6 月 23 日协议修复、6 月 24 日 Table 5 计划。

当前工作区注意事项：

- `MSAT/results/RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md` 已按用户要求调整成可直接发给导师的正式文档，并删除了“与老师建议的对应关系”，把长期阶段计划压缩为“一周内最小验证闭环”。这部分修改当前可能仍未提交，后续不要误以为文件还是最初版本。
- 当前重要基线已经提交并打 tag：
  - baseline branch：`codex/fix-reproduction-protocol`
  - baseline tag：`baseline/msat-reproduction-20260626`
  - baseline commit：`e2830f1`
- 后续 PU-XMSAT 开发应在 `codex/pu-xmsat-implementation` 分支进行。

PU-XMSAT 当前实现进度（2026-06-27）：

- 开发分支：`codex/pu-xmsat-implementation`
- 当前已完成第一轮本地最小闭环的代码与 smoke artifacts，最新阶段包括：
  - baseline lock 与 verifier；
  - pair/unobserved-pair/机制支持工具；
  - reliable negative candidate scoring；
  - PU dataset builder；
  - weighted PU BCE loss；
  - 不修改默认 `train.py` 的 PU training helper；
  - PU candidate cache、negative sampling ablation、PU smoke runner；
  - mechanism subgraph explainer、perturbation contribution scoring；
  - explanation case study workflow；
  - evidence screening table；
  - PU-XMSAT report summarizer；
  - server run/monitor scripts；
  - `full_msat_pu` 真实 MSAT GNN 后端与安全服务器 pilot 默认值。
- Task 15 本地 smoke artifacts 已生成并提交：
  - `MSAT/results/pu_candidate_scores.sample.jsonl`
  - `MSAT/results/pu_negative_sampling_summary.json`
  - `MSAT/results/pu_training_smoke_summary.json`
  - `MSAT/results/explanation_case_studies.json`
  - `MSAT/results/evidence_screening_summary.json`
  - `MSAT/results/evidence_screening_table.csv`
  - `MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md`
- 当前 PU smoke runner 已从配置型 smoke 升级为轻量真实训练 smoke：`pu_training_smoke_summary.json` 中 `training_executed: true`，使用 `weighted_embedding_smoke` 后端在 fold 0 上跑 2 个 epoch，验证 PU dataset、sample weights 和 weighted PU BCE 可以完成反向传播与 loss 下降。该结果仍不是 full MSAT GNN 训练，不能声称已完成真实多折 PU-XMSAT 服务器实验。
- 2026-06-26 已新增 `full_msat_pu` 后端：`MSAT/experiments/full_msat_pu_training.py` 使用 `MSATTCMFSFinal`、PU sample weights、validation/test positive edge hiding、best validation AUC 选择和独立 PU 输出；`run_pu_msat_experiment.py` 支持 `--backend weighted_embedding_smoke|full_msat_pu`；`server_pu_xmsat_run.sh` 默认改为 bounded full pilot（1 fold、5 epochs、384 pairs），避免误触发 10 折长训。
- AutoDL RTX 5090 上已完成 `full_msat_pu` pilot：1 fold、1 epoch、96 pairs，`runtime_seconds=3.9474`，`final_loss=0.4689035`，test AUC `0.6391`，AUPRC `0.5876`，F1 `0.6515`，MCC `0.2111`。该结果只证明真实 MSAT GNN PU 路径可运行，不能作为 PU-XMSAT 优于 MSAT 的实验结论。
- 2026-06-26 按用户授权继续在 AutoDL 跑 fold0 full MSAT PU pilot，结果记录于 `MSAT/results/PU_XMSAT_FULL_MSAT_PILOT_REPORT.md`：50e/384p AUC `0.8497` AUPRC `0.8402`；100e/768p AUC `0.8643` AUPRC `0.8511`；200e/1536p AUC `0.8855` AUPRC `0.8745`。三组 best epoch 均等于最大 epoch，说明尚未到明确平台期；但固定 0.5 阈值下 recall 近 1.0、MCC 较低。
- 2026-06-26 已实现 PU validation threshold calibration：`run_pu_msat_experiment.py` 支持 `--threshold-strategy fixed_0_5|val_f1`，`server_pu_xmsat_run.sh` 支持 `PU_XMSAT_THRESHOLD_STRATEGY`，报告脚本会记录阈值策略和每折 selected threshold。默认仍为 `fixed_0_5`，不改变旧 PU 产物解释。
- 2026-06-26 已完成 fold0 / 200 epochs / 1,536 pairs / `val_f1` 的三策略对比：`hybrid` AUC `0.8832` AUPRC `0.8706` F1 `0.6585` MCC `0.1037`；`low_score` AUC `0.8313` AUPRC `0.8079` F1 `0.7532` MCC `0.4665`；`random` AUC `0.9167` AUPRC `0.9175` F1 `0.6627` MCC `0.1417`。三者 selected threshold 均为 `0.99`，提示概率校准仍差；`random` 在 fold0 排序指标最好，`low_score` 阈值型指标最好，`hybrid` 未胜出。因此当前不能声称某一负采样策略已最终优越，下一步应做 bounded multi-fold pilot。
- 2026-06-26 已完成 bounded 3-fold / 200 epochs / 1,536 pairs / `val_f1` 的三策略对比：`hybrid` AUC `0.8696±0.0130` AUPRC `0.8583±0.0220` F1 `0.6953±0.0317` MCC `0.1984±0.1885`；`low_score` AUC `0.8722±0.0311` AUPRC `0.8658±0.0420` F1 `0.6821±0.0181` MCC `0.1644±0.1055`；`random` AUC `0.8852±0.0170` AUPRC `0.8805±0.0207` F1 `0.6739±0.0143` MCC `0.1251±0.0326`。结论：`random` 是当前正式 10 折 ranking 实验首选策略；`hybrid` 可作为阈值指标辅助比较；`low_score` 的 fold0 阈值优势不稳定。所有 3 折 selected threshold 仍为 `0.99`，概率校准问题未解决。
- 2026-06-26 已完成 bounded 10-fold / 200 epochs / 1,536 pairs / `val_f1` 的 `hybrid` 与 `random` 对比：`hybrid` AUC `0.8998±0.0116` AUPRC `0.8989±0.0147` F1 `0.6758±0.0105` MCC `0.1350±0.0480`；`random` AUC `0.8805±0.0246` AUPRC `0.8745±0.0279` F1 `0.6845±0.0162` MCC `0.1845±0.0803`。10 折后 `hybrid` 成为 ranking 指标更优策略，`random` 在 F1/MCC 更高；两者均低于原 MSAT 主实验基线，当前不能声称 PU-XMSAT 性能优于 MSAT。所有 10 折 selected threshold 仍为 `0.99`，概率校准问题持续存在。
- 2026-06-26 完成 candidate cache 审计并发现重要问题：原 tracked `pu_candidate_scores.sample.jsonl` 的 1000 行全部来自 `herb_id=0` 的前缀未观测 pair，因此上述 bounded fold0/3fold/10fold PU 结果应视为训练闭环和运行诊断，不应作为最终负采样策略优劣证据。已修复 `scripts/build_pu_candidate_cache.py`：bounded cache 默认改为 deterministic random sampling，`prefix` 仅作为显式兼容模式；tracked 1000-row sample 已刷新，覆盖 507 个 herbs；本地还生成了 ignored 的 `results/pu_candidate_scores.random50k.jsonl`，覆盖 651 个 herbs 和 5973 个 ADRs，用于下一轮 budget scaling。
- 2026-06-27 已完成 corrected random-cache `hybrid` budget scaling 与 10-fold pilot：使用 `results/pu_candidate_scores.random50k.jsonl`、200 epochs、`val_f1`。fold0 随 pair budget 提升明显：1536p AUC `0.9028`、3072p AUC `0.9319`、6144p AUC `0.9383`、12288p AUC `0.9563`。3-fold：6144p AUC `0.9446±0.0027` AUPRC `0.9338±0.0094`；12288p AUC `0.9564±0.0039` AUPRC `0.9468±0.0071`。10-fold 12288p：AUC `0.9547±0.0034`、AUPRC `0.9458±0.0066`、F1 `0.9035±0.0033`、MCC `0.8039±0.0049`，selected thresholds 为 `0.29-0.52`，best epochs `23-31`。该结果接近但仍低于原 MSAT 主实验基线（AUC `0.9793`、AUPRC `0.9771`、F1 `0.9315`、MCC `0.8625`），不能声称 PU-XMSAT 已优于 MSAT，但已经证明候选池修复和更大 pair budget 是有效方向。
- 2026-06-27 已完成 corrected random-cache `random` 10-fold pilot：使用 `results/pu_candidate_scores.random50k.jsonl`、200 epochs、12,288 pairs、`val_f1`、`full_msat_pu` 后端。结果为 AUC `0.9748±0.0016`、AUPRC `0.9719±0.0020`、F1 `0.9272±0.0039`、MCC `0.8521±0.0069`，selected thresholds `0.28-0.51`，best epochs `23-37`，runtime `643.8s`。这是当前最强 corrected PU-XMSAT 结果，已经非常接近但仍略低于原 MSAT 主实验基线（AUC `0.9793`、AUPRC `0.9771`、F1 `0.9315`、MCC `0.8625`）。报告中可以写“near-baseline corrected 10-fold PU-XMSAT pilot”，不能写“PU-XMSAT outperforms MSAT”。
- 2026-06-27 已完成 corrected random-cache `random` full-positive budget pilot：fold0 使用 66,015 pairs（22,005 positive/reliable negative/unlabeled），AUC `0.9804`、AUPRC `0.9774`、F1 `0.9290`、MCC `0.8602`，runtime `68.6s`；10-fold 使用同一 66,015-pair cap，AUC `0.9796±0.0015`、AUPRC `0.9773±0.0020`、F1 `0.9321±0.0042`、MCC `0.8625±0.0070`，thresholds `0.27-0.50`，best epochs `39-58`，runtime `737.0s`。相对 MSAT 主基线均值差：AUC `+0.00035`、AUPRC `+0.00018`、F1 `+0.00067`、MCC `-0.00001`；配对 t-test 不显著（AUC p=`0.324`、AUPRC p=`0.695`、F1 p=`0.565`、MCC p=`0.996`）。当前可以写“baseline-level corrected PU-XMSAT”，不要写“显著优于 MSAT”。
- 2026-06-27 修复 full MSAT PU fold 训练的随机种子控制：`experiments/full_msat_pu_training.py` 会在每折模型初始化前显式设置 NumPy 和 PyTorch seed，测试 `test_seed_fold_training_resets_numpy_and_torch_rng` 已覆盖。随后完成 corrected random-cache `random` full-positive seed=`2026` 10-fold 稳健性复跑：AUC `0.9797±0.0019`、AUPRC `0.9777±0.0024`、F1 `0.9338±0.0044`、MCC `0.8661±0.0080`，thresholds `0.32-0.51`，best epochs `36-55`，runtime `714.1s`。相对 MSAT 主基线均值差：AUC `+0.00046`、AUPRC `+0.00057`、F1 `+0.00233`、MCC `+0.00353`；配对 t-test 仍未过 0.05（AUC p=`0.247`、AUPRC p=`0.326`、F1 p=`0.066`、MCC p=`0.133`）。这支持“robust baseline-level”，仍不要写“显著优于 MSAT”。
- 2026-06-27 已完成 corrected random-cache `hybrid` full-positive seed=`2026` 10-fold comparator：AUC `0.9804±0.0017`、AUPRC `0.9779±0.0020`、F1 `0.9351±0.0042`、MCC `0.8684±0.0079`，thresholds `0.26-0.46`，best epochs `54-79`，runtime `821.6s`。相对 MSAT 主基线均值差：AUC `+0.00115`、AUPRC `+0.00083`、F1 `+0.00361`、MCC `+0.00589`，paired t-test 均过 0.05（AUC p=`0.0004`、AUPRC p=`0.0031`、F1 p=`0.0074`、MCC p=`0.0179`）。相对 seed=2026 `random`，`hybrid` 在 AUC/F1/MCC 上显著更高，AUPRC 略高但不显著。当前这是最强 PU-XMSAT 结果，可以写“promising statistically positive comparator”，但仍建议再做一个稳健性检查后再写“最终显著优于 MSAT”。
- 2026-06-27 已完成 corrected random-cache `hybrid` full-positive seed=`1337` 10-fold robustness run：AUC `0.9804±0.0015`、AUPRC `0.9780±0.0024`、F1 `0.9348±0.0035`、MCC `0.8683±0.0058`，thresholds `0.36-0.48`，best epochs `43-92`，runtime `809.6s`。相对 MSAT 主基线均值差：AUC `+0.00112`、AUPRC `+0.00089`、F1 `+0.00332`、MCC `+0.00581`；paired t-test：AUC p=`0.0016`、AUPRC p=`0.0563`、F1 p=`0.0087`、MCC p=`0.0153`。两个 hybrid seed 的均值范围很小：AUC `0.000028`、AUPRC `0.000054`、F1 `0.000297`、MCC `0.000078`。当前可以写“full-positive hybrid shows seed-robust gains on AUC/F1/MCC and stable positive AUPRC trend”，仍建议做 PU weight sensitivity 让最终 claim 更稳。
- 2026-06-27 已完成 corrected random-cache full-positive `hybrid` seed=`1337` PU weight sensitivity：默认 `unlabeled_weight=0.2/reliable_negative_weight=0.8` 为 AUC `0.980392`、AUPRC `0.977983`、F1 `0.934767`、MCC `0.868331`；降低到 `u0.1/rn0.8` 得到 AUC `0.979932`、AUPRC `0.977368`、F1 `0.933956`、MCC `0.866775`，相对默认 AUC/AUPRC 显著下降；升高到 `u0.4/rn0.8` 得到 AUC `0.980474`、AUPRC `0.977902`、F1 `0.934410`、MCC `0.867410`，与默认统计上接近但阈值指标略低。结论：hybrid 结果不脆弱，默认 `u0.2/rn0.8` 是 ranking 与 thresholded metrics 的平衡设置。
- 2026-06-27 已泛化 `MSAT/scripts/compare_pu_xmsat_to_baseline.py` 的 comparison label，并新增 `MSAT/scripts/summarize_pu_xmsat_seed_robustness.py` 和 `MSAT/scripts/summarize_pu_xmsat_weight_sensitivity.py`。当前 tracked 统计产物包括 `MSAT/results/pu_xmsat_baseline_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_seed2026_baseline_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_seed2026_baseline_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_vs_random_seed2026_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_seed1337_baseline_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_seed1337_vs_random_seed2026_comparison.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_seed_robustness_summary.json`、`.csv`、`MSAT/results/pu_xmsat_hybrid_weight_sensitivity_summary.json`、`.csv` 以及相关 weight-sensitivity paired comparison。后续论文表格或统计口径应优先引用这些产物，而不是手工重算。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_DELIVERABLE_INDEX_CN.md`，作为当前阶段交付物总入口。后续若用户问“现在该看什么/发导师什么/写论文引用什么/下一步怎么做”，应优先打开该文件，再按场景跳转到导师汇报、口头稿、PPT、论文草稿或统计源文件。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md`，把当前 PU-XMSAT 的主结果表、hybrid vs MSAT paired statistics、two-seed robustness、weight sensitivity、推荐论文措辞和禁用措辞整理成一份论文写作入口。后续写正文或答辩材料时优先从该文件提取结果表和 claim 边界。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md`，把 PU-XMSAT 的 Methods、Results、Discussion 写成英文正文草稿。该文件明确写入：full-positive hybrid two-seed result 是当前最强证据；AUPRC 是稳定正向但较小/边界显著；Table 5/6 不属于主性能实验。后续论文正文润色应从该文件继续。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_MENTOR_PROGRESS_BRIEF_CN.md`，作为可直接用于导师沟通的中文阶段汇报草稿。该文件整合了 MSAT 主实验复现完成度、Table 5/6 边界、PU-XMSAT 动机、hybrid two-seed 结果、PU 权重敏感性、结论边界和下一步建议；后续给导师汇报时优先从该文件继续润色。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_ORAL_BRIEF_CN.md`，作为 3-5 分钟导师沟通或组会口头稿。该文件压缩自中文阶段汇报，不新增实验结论，按开场、复现边界、PU-XMSAT 动机、主要结果、权重敏感性和下一步计划组织。
- 2026-06-27 已新增 `MSAT/results/PU_XMSAT_SLIDES_OUTLINE_CN.md`，作为 10-12 页组会/答辩 slides 大纲。该文件逐页给出标题、核心信息、建议视觉和讲稿提示，适合后续直接转成 PPT。
- 2026-06-27 已生成 `MSAT/results/PU_XMSAT_SLIDES_DRAFT_CN.pptx`，作为 12 页可编辑 PowerPoint 初稿。该 PPTX 由 artifact-tool 生成，采用白底黑灰和橙色强调的学术汇报风格，已渲染检查关键页并修正表格换行、图表坐标格式和协议日期换行问题；由于 `MSAT/results/*` 默认被忽略，提交时需 `git add -f` 该 PPTX。
- 2026-06-26 已新增论文素材进展报告：`MSAT/results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`，用于记录研究动机、实现路径、pilot 结果、阶段性解释和下一步实验计划。
- 2026-06-28 已新增 `MSAT/scripts/build_case_evidence_report.py` 和 `MSAT/results/PU_XMSAT_CASE_EVIDENCE_REPORT.md`，把现有 MSAT/Table 5 风格候选、枳实案例、机制路径/贡献度和文献候选缓存合并为论文可用的“机制解释 + 外部证据分级”最小闭环。当前 16 行案例候选中 2 行为 Grade C（有机制支持但无人工核验直接证据）、14 行为 Grade D；8 行存在自动检索记录，但 0 行具备 `verified_support=True` 的直接文献强证据。该产物只能作为解释/证据筛选 workflow，不是 Table 5/6 等价复现，也不是新的 PU-XMSAT top-ranking 导出。
- 2026-06-28 已新增 `MSAT/results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md` 和 `MSAT/results/case_evidence_manual_review.json`，对两条 Grade C 进行人工核验：`Fragaria vesca L. -> Altered state of consciousness` 外部证据不支持；`Citrus aurantium L. -> Watery diarrhoea` 有胃肠/ABCG2 机制相关证据，但方向更接近调节/缓解而非证明导致水样腹泻。因此两条都不能升级为 Grade B/A，论文中只能作为机制提取和证据筛选示例。
- 2026-06-28 已新增 `MSAT/results/PU_XMSAT_CASE_SELECTION_DECISION.md`，明确当前没有强外部验证正向案例；论文案例部分应写成“预测-机制-证据分级的保守筛选流程”，不要写成确认性验证。如果未来必须补强案例，应定向筛选“高分 + 明确机制路径 + 直接数据库/文献证据”的候选，而不是继续长训或扩大无目的检索。
- 2026-06-28/29 已完善 `MSAT/scripts/run_contribution_quantification.py`、`MSAT/scripts/run_batch_mechanism_interpretability.py`、`MSAT/scripts/summarize_contribution_quantification.py` 和 `MSAT/scripts/build_mechanism_explanation_layer.py`，完成解释层关键机制子图与贡献量化。方法是从 final PU-XMSAT top prediction 的显式机制路径抽取 compound/target 节点，形成机制子图，并分别进行节点置零与路径置零重评分；`--max-features 0` 表示不截断、量化完整解析节点。旧的本地 predictor 两案例和 top-50 解释只保留为历史/回退产物，不再作为当前论文主解释结果。
- 2026-06-29 已升级解释性产物为 checkpoint-aware、batch-level、evidence-linked 机制解释：正式 seed=2026 full-positive hybrid 10-fold checkpoint export 已完成，checkpoint prefix 为 `pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8`，mean AUC/AUPRC/F1/MCC 为 0.980281/0.977907/0.934326/0.867061。正式 top5000 解释产物已同步到本地：`PU_XMSAT_TOP_PREDICTIONS_TOP5000_EXPORT.md`、`PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md` 和 `PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE_TOP5000_RANDOM_CONTROLS.md`。
- 2026-06-29 正式 Package C 结果：final top5000 unobserved CMM-ADR predictions 中显式机制路径覆盖为 top-50 1/50、top-100 8/100、top-500 31/500、top-1000 64/1000、top-5000 391/5000（7.82%）；candidate pool 完整，`candidate_pool_missing_count=0`。batch 解释从完整 top5000 池中选择并扰动量化 20 个 mechanism-supported candidates；12/20 case-level sensitivity near-zero，0/20 negative score_drop。random perturbation controls 已完成：component/target/pathway control count 为 100/100/86，max score_drop 分别为 0.0000004768、0.0000010729、0.0000299215。
- 2026-06-29 正式 Package C 聚合口径：top component 为 `compound:761`（display `Compound #761`，`name_source=unmapped_graph_id`，mean drop 0.000309，3 cases），top target 为 `target:15721`（display `Target #15721`，mean drop 0.001174），top pathway 为 `target:15721`（display path `Target #15721`，mean drop 0.001174）。解释层总入口记录 20 个 case、20 个 subgraph case、all_subgraph_nodes_quantified=true，positive component/target/pathway count 为 2/2/11，near-zero component/target/pathway count 为 18/19/9。实体若缺真实映射，会保留 `Compound #id` / `Target #id` 和 `name_source=unmapped_graph_id`，不能伪装成真实生物名称。
- 2026-06-29 正式 Package C 证据队列：`direction3_targeted_review_queue_top5000_random_controls.json` 中 case_count=20，manual_reviewed_count=1，target_external_evidence_review_count=19，ready_strong_evidence_count=0，Grade A/B 强外部证据为 0。扰动高低不能自动升级 evidence grade，Grade C 不能写成外部验证，negative score_drop 不能解释成保护机制。
- 2026-06-29 已完成 top20 解释候选实体映射审计与 first-pass 外部证据复核：新增 `PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md`、`PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md`、`PU_XMSAT_ENTITY_MAPPING_AUDIT_AND_CANDIDATES.md`、`PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md` 和 `top20_external_evidence_review.json`。结论：top20 机制队列包含 20 个 compound 和 39 个 target，confirmed mapped_count=0、unmapped_count=59；公开 MSAT/Zenodo/GitHub/Frontiers 资源未提供 compound/target local ID 字典，ccTCM/ETCM/HGNC/ADReCS 只能用于候选或外部证据，不能证明本地 ID。HGNC/BioBERT 为 39 个 target 生成 `candidate_only` 名称候选，但不能写成确认映射。外部证据 first-pass 结果为强完整链证据 0/20、中等间接支持 1/20、弱/边界支持 2/20；最适合论文的是 `Polypodium glycyrrhiza` 胃肠方向 triage case 和 `Fragaria vesca L.` 边界案例。后续 Overleaf 解释性段落应写成机制 triage，不要写强解释性、完整机制验证或外部临床验证。
- `run_pu_msat_experiment.py` 现在暴露 `--save-checkpoints`、`--checkpoint-dir`、`--checkpoint-prefix` 和 `--overwrite-checkpoints`；默认 formal checkpoint prefix 包含 backend、strategy、seed、pair budget、threshold strategy、unlabeled weight 和 reliable-negative weight，文件名追加 fold。默认不覆盖同名 formal checkpoint 或 metadata，避免污染旧结果或 baseline checkpoint；只有显式 `--overwrite-checkpoints` 才允许 intentional rerun。
- 2026-06-29 已将英文 ACM 风格论文工程持久化到 `Template/PU-XMSAT-Overleaf/`，并保留上传包 `Template/PU-XMSAT-Overleaf.zip`。新增 `MSAT/scripts/audit_manuscript_package.py`、`MSAT/results/manuscript_package_audit.json` 和 `MSAT/results/PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md`，把论文包位置、模板合规、PDF 页数/纸张、LaTeX 日志、zip 必要/禁止条目和人工待确认项变成可重复审计。当前真实审计为 `ok: true`、failed checks `0`、warning checks `1`；warning 仅来自作者/机构/CCS/venue/funding/AI disclosure/double-blind policy 等提交前人工确认项。当前稿件编译为 12 页 Letter PDF；源码使用提供的 `acmart.cls`，zip 不包含 `main.pdf` 或 LaTeX 辅助产物。`.gitignore` 只忽略原始模板包 `Template/文件*`、本地预览 `Template/PU-XMSAT-Overleaf/main.pdf`、`.DS_Store` 和无关共享 zip，避免把用户提供的原始模板附件或本地编译产物混进提交。
- 2026-06-29 已新增 `MSAT/scripts/audit_submission_readiness.py`、`MSAT/results/submission_readiness_audit.json` 和 `MSAT/results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md`，把最终投稿状态拆成机器可验证项和学生/导师人工确认项。当前 package audit OK、machine failures 0，但 `ready_for_submission=false`，human blockers 7：author metadata、venue metadata、CCS confirmation、funding acknowledgments、AI disclosure policy、double-blind policy、reference/figure scope。该审计说明当前 Overleaf 包可以协作/预审，但不能声称最终可投稿。
- 2026-06-28 已新增 `MSAT/results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md`，把导师建议中的因果图方向落实为当前阶段可支撑的 DAG/混杂因素边界。当前可说：PU-XMSAT 缓解 incomplete-label bias；不能说：已经控制合并用药、适应症偏倚、报告偏倚、暴露人群差异、剂量或炮制质量。严格因果估计需要额外 patient-level exposure、co-medication、indication、onset time、dose 和 reporting propensity 数据。
- 2026-06-28 已新增 `MSAT/results/PU_XMSAT_RESEARCH_CLOSURE_AUDIT.md`，将 `RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md` 中的训练层、解释层、验证层和因果边界逐项映射到当前产物。结论：当前已经形成最小、保守、可写论文的研究闭环；剩余工作主要是论文整合、人工润色和未来数据/证据补强，不建议继续盲目长训。
- 用户已明确允许刷新 `MSAT/results/reproduction_state_audit.json`。Task 17 原始审计命令已执行，当前审计文件 `created_at` 为 2026-06-26 13:39:17，结果为 `issues: []`；刷新内容仅更新审计时间戳，summary 未出现异常。
- 后续若进入正式长训，仍需先做代码核对、服务器测试和输出命名检查，避免覆盖 baseline 或旧 PU 产物；用户已经允许使用服务器推进，但不要把服务器 SSH、密码或临时密钥写入仓库、报告或记忆文件。

## 3. 数据与论文协议锚点

官方数据和协议锚点：

- 官方图数据：`experiments_data_clean_final/complete_hetero_graph.pt`
- 官方 10 折：`MSAT/data/10fold_cv_split.pkl`
- 图节点：
  - CMM/herb：651，768 维特征
  - compound：1,498，768 维特征
  - target：21,393，768 维特征
  - ADR：5,974，768 维特征
- 监督 CMM-ADR 边：27,062，带 6 维 evidence feature
- 其中 FAERS 正边约 25,734，文献正边约 1,328。

当前协议版本：

- `MSAT/reproduction_protocol.py`
- `PROTOCOL_VERSION = "2026-06-23-val-test-edge-hidden"`
- 关键含义：validation 和 test 的正向 CMM-ADR 监督正边都应从 message-passing 图中隐藏。
- prediction checkpoint 按 `best_val_auc` 选择，不按 test AUC 选择。

论文主协议：

1. Table 2：1:1 负采样，10 折交叉验证。
2. Table 3：MSAT 模块消融，包括 ESA/HSP/HCI。
3. Table 4：1:10 不平衡训练/评价。
4. Fig.5a：FAERS-only 训练，文献 hold-out 冷启动评估，约 96.5% unseen CMM。
5. Fig.6：测试集负样本比例 1:2、1:5、1:10 的不平衡 sweep。
6. Table 5：Top-15 高置信未标注 CMM-ADR 预测，依赖 TCMDA/文献/机制证据，不只是训练指标。
7. Table 6：Table 5 下游的 TCM 功能系统映射。
8. §4.5.1：枳实 / Citrus aurantium L. 到 diarrhoea 的案例解释，涉及 nobiletin 和 ABCG2/BCRP 叙事。

## 4. 当前复现完成度总览

截至 2026-06-26，应这样概括项目状态：

**主实验复现已经成功，完整论文逐表复现尚未完成。**

可以较稳妥引用：

1. Table 2 MSAT 主实验：已对齐论文主性能。
2. Table 2 九基线：当前防泄漏协议下可引用，MSAT AUC 最高。
3. Fig.5a FAERS-only 冷启动：可引用，MSAT 在 Precision、MCC、AUC 上均优于 GAT/HGT/Simple-HGN。
4. Fig.6：AUC/AUPRC 趋势可引用，MSAT 在 1:2、1:5、1:10 的 AUC/AUPRC 均最高；F1/MCC 中 HGT 更高，需要解释阈值差异。
5. `reproduction_state_audit.json`：当前 `issues: []`。

需要解释差异：

1. Table 3 消融：7 个变体齐全，但 Full 不是所有指标最高；`wo_esa` 的 AUC/AUPRC 略高于 Full，`only_hsp` 的 F1/MCC 较高。可报告趋势差异，不要声称完全复刻。
2. Table 4 全模型 1:10：MSAT 的 F1/MCC 最高，但 XGB 的 AUC/AUPRC 略高于 MSAT；论文中 MSAT 在更多指标上第一。
3. Fig.6 阈值指标：AUC/AUPRC 对齐论文趋势，但 F1/MCC 当前 HGT 更高。
4. 枳实案例：当前 checkpoint 下可生成案例，score 0.6849，rank 1/5974，含 nobiletin 路径；但仍需要与论文 nobiletin/ABCG2 证据逐项说明差异。

不可声称已复现：

1. Table 5 Top-15 外部验证：当前支持率 1/15，不复现论文 13/15。
2. Table 6 精细 TCM 系统映射：已生成，但依赖当前 Table 5，规则仍粗。

## 5. 当前关键结果

### 5.1 Table 2 MSAT 主实验

文件：`MSAT/results/summary.json`

当前主实验指标：

| 指标 | mean |
| --- | ---: |
| Precision | 0.9286 |
| Recall | 0.9344 |
| F1 | 0.9315 |
| AUC | 0.9793 |
| AUPRC | 0.9771 |
| MCC | 0.8625 |

这已经接近论文主实验结果，可作为后续改进方法的稳定基线。

### 5.2 Table 2 基线

文件：`MSAT/results/baseline_summary.json`

当前 1:1 结果中，MSAT AUC 最高：

| 模型 | AUC | AUPRC | F1 | MCC |
| --- | ---: | ---: | ---: | ---: |
| MSAT | 0.9793 | 0.9771 | 0.9315 | 0.8625 |
| LR | 0.9316 | 0.9247 | 0.8515 | 0.6972 |
| RF | 0.9202 | 0.9018 | 0.8528 | 0.7021 |
| XGB | 0.9412 | 0.9364 | 0.8624 | 0.7210 |
| GCN | 0.9416 | 0.9137 | 0.9275 | 0.8527 |
| GAT | 0.9738 | 0.9706 | 0.9172 | 0.8348 |
| RGCN | 0.9694 | 0.9671 | 0.8827 | 0.7846 |
| HGT | 0.9680 | 0.9670 | 0.8807 | 0.7802 |
| HetNN | 0.9698 | 0.9668 | 0.8859 | 0.7889 |
| Simple-HGN | 0.9725 | 0.9691 | 0.9124 | 0.8274 |

### 5.3 Table 3 消融

文件：`MSAT/results/ablation_summary.json`

当前 7 个变体齐全：

| 变体 | AUC | AUPRC | F1 | MCC |
| --- | ---: | ---: | ---: | ---: |
| full | 0.9793 | 0.9771 | 0.9315 | 0.8625 |
| wo_esa | 0.9795 | 0.9774 | 0.9311 | 0.8618 |
| wo_hsp | 0.9781 | 0.9762 | 0.9288 | 0.8566 |
| wo_hci | 0.9777 | 0.9755 | 0.9331 | 0.8648 |
| only_esa | 0.9773 | 0.9752 | 0.9301 | 0.8591 |
| only_hsp | 0.9780 | 0.9758 | 0.9342 | 0.8670 |
| only_hci | 0.9780 | 0.9760 | 0.9285 | 0.8557 |

报告口径：消融实验完成，但不应写成“完全符合论文排序”。可以写为：Full 保持高性能，去除/仅保留模块的表现差异在 0.001 量级，说明模块贡献趋势存在但与论文表格不完全同序。

### 5.4 Table 4 1:10

MSAT 单模型文件：`MSAT/results/summary_neg10.json`

| 指标 | mean |
| --- | ---: |
| Precision | 0.5725 |
| Recall | 0.5506 |
| F1 | 0.5604 |
| AUC | 0.8710 |
| AUPRC | 0.5917 |
| MCC | 0.5180 |

全模型 1:10 文件：`MSAT/results/baseline_neg10_summary.json`

关键结论：

- MSAT F1/MCC 最高。
- XGB AUC 0.8768、AUPRC 0.5922，略高于 MSAT 的 AUC 0.8710、AUPRC 0.5917。
- GCN 1:10 近似随机，AUC 约 0.4999。

报告口径：Table 4 已生成且可审计，但全模型排名未完全复现论文。

### 5.5 Fig.5a FAERS-only 冷启动

文件：`MSAT/results/faers_only_coldstart_summary.json`

结论：

- 协议：`paper_3.5.4_faers_train_literature_eval`
- unseen CMM target：0.965
- `msat_beats_all_gnn: true`
- MSAT 在 Precision、MCC、AUC 三项均优于 GAT/HGT/Simple-HGN。

不要把早期 10 折 CV 代理冷启动结果与 FAERS-only 结果混读。论文 Fig.5a 对应 FAERS-only 训练和文献 hold-out 评估。

### 5.6 Fig.6 测试不平衡

文件：`MSAT/results/fig6_summary.json`

当前行包括 ratio 2、5、10 下的 MSAT、HGT、Simple-HGN、GAT：

- ratio=2：MSAT AUC 0.8182，AUPRC 0.7351；HGT F1/MCC 更高。
- ratio=5：MSAT AUC 0.8179，AUPRC 0.5683；HGT F1/MCC 更高。
- ratio=10：MSAT AUC 0.8172，AUPRC 0.4330；HGT F1/MCC 更高。

报告口径：AUC/AUPRC 复现论文趋势，阈值型指标需要解释校准差异。

### 5.7 Table 5

权威文件：

- `MSAT/results/TABLE5_PROTOCOL_DECISION.md`
- `MSAT/results/table5_summary.json`
- `MSAT/results/reproduction_gap_diagnosis.json`
- `MSAT/results/table5_literature_evidence_candidates.json`

当前结论：

- 当前 Table 5 产物有效且非 stale，但不复现论文支持率。
- 当前 `table5_summary.json`：
  - protocol：`paper_3.5.6_global_top15`
  - scoring_mode：`predictor`
  - candidate_pool：`exclude_all_graph_positives`
  - support_rate：1/15 = 0.0667
  - supported_count：1
  - checkpoint sha：`506e7fd3a1d81e1fd97651542494e51019be351fb39e73a3d8dd32c335283e95`
- 文献候选自动抓取：
  - PubMed/OpenAlex 候选 63 条。
  - 精确 herb+ADR 命中 0 条。
  - 全部仅供人工复核，不可默认作为 verified support。
- 论文 Table 5 参考配对诊断：
  - paper rows：15
  - mapped pairs：14
  - pairs in graph：1
  - pairs in OOF scores：1
- `paper_seed_top1_oof` 能得到 13/15 support，但这是诊断模式：
  - diagnostic_only：true
  - is_table5_reproduction_claim：false
  - adr_match_paper：0
  - 不能写成 Table 5 复现。

当前 Table 5 不可复现的核心原因：

1. 官方公开代码没有 Table 5 导出脚本或 notebook。
2. OOF fold predictions 无法重建论文 Table 5 候选空间。
3. 本地 `saved_models/best_model_for_prediction.pt` 与生成当前 Table 5 的服务器 checkpoint sha 不一致。
4. 服务器结果包没有包含目标 checkpoint，无法从当前本地状态恢复。
5. TCMDA 证据路径没有可公开 API；目前只能人工缓存或显式证据补充。

报告规则：

- 可以写“当前公开材料下 Table 5 无法纸面等价复现”。
- 不要写“Table 5 已复现 13/15”。
- 不要把 paper-seed diagnostic 或 mechanistic path 单独等同于 TCMDA 支持。

### 5.8 Table 6

文件：

- `MSAT/results/table6_mapping.csv`
- `MSAT/results/table6_mapping.json`

当前结论：

- Table 6 映射产物已生成。
- 但 Table 6 依赖 Table 5 候选和证据，因此当前只能作为下游 mapping workflow 产物，不能声称复现论文 Table 6。
- 映射规则仍粗，很多 PT/SOC 会落到泛化系统。

### 5.9 枳实案例

文件：`MSAT/results/case_zhishi_diarrhoea.json`

当前产物：

- artifact_status.stale：false
- herb_id：277
- herb_label：枳实（Citrus aurantium L.）
- adr_label：Watery diarrhoea
- score：0.6849409937858582
- rank：1/5974
- 路径含：nobiletin (CID 72344) 与多个 target id
- paper_targets：nobiletin_cid 72344；transporter ABCG2 (BCRP)

报告口径：当前 checkpoint 下可以作为案例产物引用，但若写论文式解释，需要补足 target id 到 ABCG2/BCRP 的逐项证据映射。

## 6. 当前实现结构

### 6.1 模型

文件：`MSAT/model.py`

主要类：

- `MSATEdgeEncoder`：处理 6 维 CMM-ADR edge_attr，把 evidence feature 注入 attention logit。
- `MSATOutputTransform`：输出/瓶颈变换，对应 HSP 风格。
- `LateFusionPredictor`：MLP、Bilinear、DistMult 三路融合预测，对应 HCI。
- `MultiTypeGraphAttention`：多类型图注意力。
- `MultiRelationAttentionLayer`：多关系异构图 message passing。
- `MSATTCMFSFinal`：最终 MSAT 模型。

### 6.2 训练

文件：`MSAT/train.py`

关键实现：

- 使用官方 `10fold_cv_split.pkl`。
- 每折将 validation 和 test 的正向 CMM-ADR 监督正边从图中隐藏，含反向边同步处理。
- 支持主实验和带 tag 的实验，避免 checkpoint 覆盖。
- 预测 checkpoint 按 `best_val_auc` 选择。
- summary 中写入协议 metadata、data/model/training config、fold metrics、checkpoint 信息。

### 6.3 数据加载

文件：`MSAT/experiments/feature_extractor.py`

关键实现：

- 读取 Zenodo `complete_hetero_graph.pt`。
- 支持官方 split、1:1、1:10、test-only imbalance。
- CMM-ADR edge_attr 应为 6 维。

### 6.4 基线

文件：

- `MSAT/baselines/common.py`
- `MSAT/baselines/ml_models.py`
- `MSAT/baselines/gnn_models.py`
- `MSAT/scripts/run_baselines.py`

关键实现：

- GNN baseline 使用与 MSAT 一致的 val/test 正边隐藏。
- ML baseline 的 `pair_features()` 默认 `include_edge_attr=False`，避免把 CMM-ADR label-carrying edge_attr 泄漏给 LR/RF/XGB。
- 旧的 ML baseline AUC≈1.0 是泄漏产物，已经修复并重跑；当前 `baseline_summary.json` 和 `baseline_neg10_summary.json` 可审计。

### 6.5 下游推理与验证

重要文件：

- `MSAT/inference/predictor.py`：加载模型 checkpoint，对 CMM-ADR pair 打分。
- `MSAT/inference/artifact_manifest.py`：记录文件 size、mtime、sha256，用于 provenance。
- `MSAT/inference/entity_mapping.py`：实体名称与 paper herb 显示。
- `MSAT/inference/graph_utils.py`：路径解释辅助。
- `MSAT/inference/tcmda_validation.py`：TCMDA 缓存证据匹配。
- `MSAT/inference/literature_evidence.py`：PubMed/OpenAlex/Crossref 证据抓取与解析。
- `MSAT/inference/tcm_mapping.py`、`paper_tables.py`：Table 6 相关映射。

重要脚本：

- `scripts/audit_reproduction_state.py`：当前最重要的产物审计。
- `scripts/run_table5_validation.py`：Table 5 候选生成与证据汇总。
- `scripts/diagnose_reproduction_gaps.py`：Table 5、checkpoint、coldstart 等复现差距诊断。
- `scripts/fetch_table5_literature_evidence.py`：公开文献候选抓取。
- `scripts/run_table6_mapping.py`：Table 6 映射。
- `scripts/run_case_zhishi.py`：枳实案例。
- `scripts/run_faers_only_coldstart_train.py` 与 `run_faers_only_coldstart_gnn.py`：Fig.5a。
- `scripts/run_imbalance_sweep.py`：Fig.6。

### 6.6 测试

测试目录：`MSAT/tests/`

关键测试：

- `test_protocol_edge_isolation.py`
- `test_baseline_leakage.py`
- `test_checkpoint_paths.py`
- `test_artifact_manifest.py`
- `test_threshold_protocol.py`
- `test_script_protocol_config.py`
- `test_audit_reproduction_state.py`
- `test_diagnose_reproduction_gaps.py`
- `test_fetch_table5_literature_evidence.py`
- `test_literature_evidence.py`

后续改代码时，至少运行相关测试；涉及复现实验状态时运行：

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error
```

如需完整测试，在当前机器通常使用：

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q
```

## 7. 已解决的问题

已经处理过的重要问题：

1. 官方 split 对齐：从自写 KFold 切换为官方 `10fold_cv_split.pkl`。
2. 归纳协议修复：validation/test 正边从 message-passing 图中隐藏。
3. ML baseline 泄漏修复：默认不使用 CMM-ADR edge_attr 作为 pair feature。
4. checkpoint 覆盖修复：带 tag 的实验写入独立 checkpoint，主 predictor checkpoint 不再被随意覆盖。
5. threshold 协议修复：1:10 等实验使用正确阈值配置。
6. artifact provenance：Table 5、Table 6、枳实案例等结果写入 checkpoint/input manifest。
7. 产物污染处理：stale 标记、审计脚本、结果目录 README、server result bundle ignore 等。
8. Table 5 误判修正：明确 13/15 paper-seed 结果只是诊断，不是复现。

## 8. 仍然存在的问题

1. Table 5 论文等价复现无法完成，除非补充作者未公开材料：
   - 原始 predictor checkpoint，sha256 为 `506e7fd3a1d81e1fd97651542494e51019be351fb39e73a3d8dd32c335283e95`
   - 作者 Table 5 导出脚本或 notebook
   - “not included among labeled positives”的精确定义
   - 每一行 TCMDA/文献证据记录
2. Table 6 仍依赖 Table 5，因此不能单独声称论文等价复现。
3. Table 3 与 Table 4 的部分排序和论文不完全一致，需要写成差异分析。
4. Fig.6 的 AUC/AUPRC 对齐，但 F1/MCC 需要阈值校准解释。
5. 枳实案例还需补 target 可读化和论文机制证据逐项对照。
6. 当前未来研究方向文档已经是导师可读版，但尚未把技术实现正式启动到代码层面。

## 9. 未来研究规划

用户已给出导师建议，经过讨论后确定后续研究方向不应继续死磕 Table 5 完全复刻，而应基于复现发现的问题提出模型改进。

当前正式方向：

**基于不完整标签学习与机制解释的中药不良反应预测模型改进研究。**

主线：

1. **可靠负样本选择与 PU Learning**
   解决“未观测不等于无关联”的核心问题。未观测药物-副作用 pair 不应简单当负样本。

2. **关键机制子图解释与贡献度量化**
   基于注意力权重、路径约束、扰动贡献或 SHAP-style 方法，解释单个药物-副作用预测由哪些成分、靶点和路径支持。

3. **外部证据辅助验证**
   使用 PubMed、SIDER、DrugBank、FAERS、说明书等来源构建证据分级。大模型或 DeepSeek 只能作为文献筛选/摘要/辅助判断工具，不能直接作为训练标签或金标准。

4. **因果图作为阶段性扩展**
   当前数据缺少个体级暴露、合并用药、适应症、人群统计等变量，因此严格因果推断不适合作为第一阶段核心方法。当前只做 DAG 和偏倚分析，后续有真实世界数据后再做因果校正。

当前导师版文档：

- `MSAT/results/RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md`

用户已明确要求：

- 文档要能直接发给导师。
- 删除“与老师建议的对应关系”部分。
- 不要写 8 到 10 周长期计划，改成一周内最小验证闭环。

当前实现计划：

- `MSAT/results/RESEARCH_DIRECTION_IMPLEMENTATION_PLAN.md`
- `docs/superpowers/plans/2026-06-26-pu-xmsat-implementation.md`

建议实现模块：

- `MSAT/experiments/reliable_negative_sampling.py`
- `MSAT/experiments/pu_dataset_builder.py`
- `MSAT/experiments/pu_loss.py`
- `MSAT/experiments/run_pu_msat_experiment.py`
- `MSAT/experiments/run_negative_sampling_ablation.py`
- `MSAT/inference/subgraph_explainer.py`
- `MSAT/inference/contribution_scoring.py`
- `MSAT/scripts/run_explanation_case_study.py`
- `MSAT/scripts/build_evidence_screening_table.py`
- `MSAT/scripts/summarize_pu_xmsat_results.py`
- `MSAT/scripts/compare_pu_xmsat_to_baseline.py`

## 10. 当下近期计划

如果接下来用户说“开始进行”或“按照计划推进”，不要继续用旧 prefix cache、1,536-pair cap、12,288-pair corrected 10-fold 设置、66,015-pair full-positive corrected `random` seed=42 设置、seed=2026 repeated-seed 设置、full-positive `hybrid` seed=2026/1337 comparator，或 u0.1/u0.4 weight-sensitivity 设置反复重跑；当前关键 corrected `random` 对照、一次 repeated-seed 稳健性实验、full-positive `hybrid` two-seed comparator 和 PU weight sensitivity 已经完成。

当前最合理的近期实验：

1. paired fold comparison / statistical note 已由 `scripts/compare_pu_xmsat_to_baseline.py` 生成；后续如果改结果，先重跑该脚本刷新 `pu_xmsat_baseline_comparison.json/.csv`。
2. 导师已明确要求补强解释层，并提供远程 GPU 训练资源；不要再用 fold0/pilot/minimal training 替代 final checkpoint。当前已完成 seed=2026 full-positive hybrid PU-XMSAT formal 10-fold checkpoint export：mean AUC/AUPRC/F1/MCC 为 0.980281/0.977907/0.934326/0.867061，10 个 checkpoint 与 10 个 metadata sidecar 写入远程 `saved_models/pu_xmsat_formal/`，本地同步了 metadata 和结构化结果。当前交付物总入口为 `MSAT/results/PU_XMSAT_DELIVERABLE_INDEX_CN.md`；final checkpoint 状态为 `MSAT/results/PU_XMSAT_FINAL_CHECKPOINT_EXPORT_REPORT.md`；解释 checkpoint gap 审计为 `MSAT/results/PU_XMSAT_INTERPRETABILITY_GAP_AUDIT.md`。正式 top5000/random-control 解释结果也已同步并审计：`PU_XMSAT_TOP_PREDICTIONS_TOP5000_EXPORT.md`、`PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md`、`PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE_TOP5000_RANDOM_CONTROLS.md`。final top5000 中显式机制路径覆盖为 391/5000（7.82%），20 个 mechanism-supported candidates 完成扰动量化和 random-control 对照，Grade A/B 强外部证据仍为 0。论文应写成 checkpoint-aware batch-level mechanism triage 和 evidence queue，不写成强解释性、SHAP、因果效应或外部验证。
3. 概率校准不再是第一阻塞点，因为 corrected 10-fold thresholds 已回到 `0.27-0.50`；后续可作为单独 calibration/PU weight ablation。
4. 不要把旧 prefix-cache 10-fold 结果当作策略优劣最终证据；它们只能说明训练闭环、运行时间和指标记录流程已经可复现。
5. 写论文时可报告 corrected random-cache full-positive `hybrid` two-seed + weight-sensitivity result 作为当前最强 PU-XMSAT 证据，并说明两 seed 在 AUC/F1/MCC 上稳定优于 MSAT，AUPRC 为稳定正向趋势；默认 `u0.2/rn0.8` 经权重敏感性验证为平衡设置。案例解释/外部证据只能报告为“最小筛选闭环”：2 行 Grade C、14 行 Grade D、0 行人工核验直接文献支持；两条 Grade C 经人工核验后均不能升级。
6. 导师提出的“先聚类，然后把聚类的某一个新类作为测试集试试”应作为独立的 cluster-held-out / cold-cluster generalization 实验处理；它不是解释层贡献量化本身。解释层当前优先级仍是提取关键机制子图并量化成分、靶点和路径贡献。
7. 2026-06-29 已按论文成果导向完成三包工作并形成当前正式证据链。Package A：`MSAT/scripts/consolidate_pu_xmsat_publication_evidence.py` 生成 `MSAT/results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md` / `pu_xmsat_publication_evidence_consolidation.json`，整合 reproduced baseline、hybrid two-seed、random comparator、seed robustness 和 weight sensitivity。Package B：`MSAT/experiments/cluster_holdout_generalization.py`、`--split-mode cluster_holdout`、`allowed_train_herbs` 防泄漏过滤与 `MSAT/scripts/summarize_cluster_holdout_generalization.py` 已支持并汇总正式 10-cluster/10-fold/200-epoch run；all-fold AUC/AUPRC/F1/MCC 为 0.8891/0.9032/0.1770/0.1919，排除少于 5 味中药 heldout clusters 后的 non-tiny robust mean 为 0.8433/0.8633/0.0743/0.1168，test-positive weighted mean 为 0.8162/0.8372/0.0821/0.1338，需说明 3 个 heldout clusters 少于 5 味中药且阈值型指标较弱。Package C：top5000 final interpretability + random controls 已同步，candidate pool 完整，显式路径覆盖 391/5000，20 个机制支持候选完成扰动量化，ready strong evidence 仍为 0。后续不要再把本地 pilot、本地 top-50-bounded coverage 或 missing random controls 写成论文最终结果。
8. 2026-06-29 已开始 391 显式路径候选的 evidence-aware 扩展：新增 `MSAT/scripts/build_evidence_aware_candidate_queue.py`、`MSAT/results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`、`evidence_aware_mechanism_candidate_queue.json/.csv`、`evidence_aware_literature_candidates.json/.csv` 和 `PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`。当前 top30 队列来自 391 个显式路径候选，覆盖 8 个 herbs；PubMed exact-query first-pass 缓存 30 个查询，保留 2 条 herb+ADR 文本匹配，均为 `Marchantia polymorpha` -> `Liver injury`，但文献方向更像 hepatoprotective/化学诱导肝损伤模型，不能写成不良反应强验证。下一步若继续提升解释性，应人工复核 evidence-aware top30，而不是只盯旧 top20。
9. 2026-06-29 已确认 compound/target 生物语义映射缺口并联系原作者：Zenodo API record `10.5281/zenodo.17933842` 只列出 `complete_hetero_graph.pt`；GitHub API for `BowenShiGDPU/MSAT` 显示仓库根目录只有代码/README/LICENSE，`data/` 仅有 `10fold_cv_split.pkl`；本地图文件 `experiments_data_clean_final/complete_hetero_graph.pt` 载入后 compound/target node stores 只有 `x`，无 name、SMILES、PubChem、HGNC、UniProt 或 source ID 字段。已生成 `MSAT/results/PU_XMSAT_ORIGINAL_AUTHOR_MAPPING_REQUEST.md`，并用 GitHub issue 联系原作者请求 local row index -> PubChem/SMILES/HGNC/UniProt/source ID 映射：https://github.com/BowenShiGDPU/MSAT/issues/1。随后已追加评论请求论文 Table 5 所需导出脚本/checkpoint/候选池定义/逐行 TCMDA/文献/机制证据记录，以及 Table 6 所需 Table 5 输入、MedDRA PT/SOC->TCM 系统映射规则、脚本和最终 row-level TCM system labels：https://github.com/BowenShiGDPU/MSAT/issues/1#issuecomment-4832635051。

不要覆盖 baseline 产物；正式运行前必须先完成本地测试、服务器测试、输出命名核对和报告模板更新。

## 11. 后续回答注意事项

后续回答用户时要保持以下边界：

1. 不要说“全文 100% 复现”。正确说法是“主实验与多数核心指标已复现，Table 5/6 未论文等价复现”。
2. 不要说“Table 5 已经 13/15”。13/15 是 paper-seed diagnostic，不是 Table 5 reproduction。
3. 不要把 Table 5 和 Table 6 当作主实验。它们是外部验证/案例解释/辅助佐证。
4. 不要忽略 Table 3、Table 4、Fig.6 的差异；要用“差异可解释但不完全同序”描述。
5. 不要把大模型输出当标注。大模型只能做外部证据辅助。
6. 不要把当前两条 Grade C 案例写成“外部验证成功”；野草莓案例不支持，枳实案例方向冲突。
7. 不要自动提交或推送未跟踪文件，尤其是 `CURRENT_MODEL_CAPABILITY_REPORT.md`，除非用户明确要求。
8. 不要在文档给导师时保留过多内部工程话，比如 checkpoint hash、git、产物污染、服务器密码等，除非是技术审计报告。
9. 服务器 SSH 和密码曾由用户提供，但不要写入仓库、报告或记忆文件。
10. 回答尽量用中文，并且对导师/科研方向问题保持正式口吻。

## 12. 快速状态句

如果需要一句话回答当前状态：

> 当前项目已经较好复现 MSAT 的主实验和多数核心性能结果，结果目录审计为 `issues: []`；Table 5/6 属于外部验证和下游解释，当前公开材料下不能论文等价复现。PU-XMSAT 已完成可靠负样本选择与 PU Learning 主实验，并已补上机制子图解释与外部证据分级的最小论文闭环；两条 Grade C 经人工核验后仍不能升级为强证据，后续若要增强论文案例部分，应寻找更合适的高置信候选。

## 13. 关键文件索引

项目记忆与报告：

- `MSAT/PROJECT_MEMORY.md`
- `MSAT/results/README.md`
- `MSAT/results/REPRODUCTION_REPORT.md`
- `MSAT/results/FINAL_REMOTE_RUN_SUMMARY_2026-06-23.md`
- `MSAT/results/TABLE5_PROTOCOL_DECISION.md`
- `MSAT/results/RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md`
- `MSAT/results/RESEARCH_DIRECTION_IMPLEMENTATION_PLAN.md`

结果：

- `MSAT/results/summary.json`
- `MSAT/results/baseline_summary.json`
- `MSAT/results/ablation_summary.json`
- `MSAT/results/summary_neg10.json`
- `MSAT/results/baseline_neg10_summary.json`
- `MSAT/results/fig6_summary.json`
- `MSAT/results/faers_only_coldstart_summary.json`
- `MSAT/results/table5_summary.json`
- `MSAT/results/reproduction_gap_diagnosis.json`
- `MSAT/results/reproduction_state_audit.json`

核心代码：

- `MSAT/model.py`
- `MSAT/train.py`
- `MSAT/reproduction_protocol.py`
- `MSAT/experiments/feature_extractor.py`
- `MSAT/baselines/common.py`
- `MSAT/scripts/audit_reproduction_state.py`
- `MSAT/scripts/run_table5_validation.py`
- `MSAT/scripts/diagnose_reproduction_gaps.py`

原始资源：

- `resource_副本/fphar-17-1774128.pdf`
- `resource_副本/MSAT-main/`
- `resource_副本/MSAT_SESSION_PROGRESS_2026-06-23.md`
