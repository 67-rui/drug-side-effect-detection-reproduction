# MSAT 项目外部记忆

**最后更新：** 2026-06-26
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

PU-XMSAT 当前实现进度（2026-06-26）：

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
- 2026-06-26 已新增论文素材进展报告：`MSAT/results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md`，用于记录研究动机、实现路径、pilot 结果、阶段性解释和下一步实验计划。
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

## 10. 当下近期计划

如果接下来用户说“开始进行”或“按照计划推进”，不要继续用同样 1,536-pair cap 反复重跑 10 折；应先扩大或解除 PU pair budget，再做 fold0 budget scaling。

当前最合理的近期实验：

1. 使用随机化后的 50k candidate cache 跑 `hybrid` fold0 budget scaling，优先比较 1,536 / 3,072 / 6,144 pairs，必要时再试 12,288。
2. 不要把旧 prefix-cache 10-fold 结果当作策略优劣最终证据；它们只能说明训练闭环、运行时间和指标记录流程已经可复现。
3. 如果 larger-budget fold0 的 AUC/AUPRC 明显提升，再跑 3 折确认稳定性；不要马上重跑 10 折。
4. 如果 10 折/多折仍全部选择 threshold `0.99`，把概率校准列为后续单独 ablation，而不是混入本轮 ranking 结论。
5. 写论文时保留当前 bounded 10-fold 作为诊断性结果：PU-XMSAT 训练闭环可复现，但 naive bounded PU 还不能直接超过 MSAT。

不要覆盖 baseline 产物；正式运行前必须先完成本地测试、服务器测试、输出命名核对和报告模板更新。

## 11. 后续回答注意事项

后续回答用户时要保持以下边界：

1. 不要说“全文 100% 复现”。正确说法是“主实验与多数核心指标已复现，Table 5/6 未论文等价复现”。
2. 不要说“Table 5 已经 13/15”。13/15 是 paper-seed diagnostic，不是 Table 5 reproduction。
3. 不要把 Table 5 和 Table 6 当作主实验。它们是外部验证/案例解释/辅助佐证。
4. 不要忽略 Table 3、Table 4、Fig.6 的差异；要用“差异可解释但不完全同序”描述。
5. 不要把大模型输出当标注。大模型只能做外部证据辅助。
6. 不要自动提交或推送未跟踪文件，尤其是 `CURRENT_MODEL_CAPABILITY_REPORT.md`，除非用户明确要求。
7. 不要在文档给导师时保留过多内部工程话，比如 checkpoint hash、git、产物污染、服务器密码等，除非是技术审计报告。
8. 服务器 SSH 和密码曾由用户提供，但不要写入仓库、报告或记忆文件。
9. 回答尽量用中文，并且对导师/科研方向问题保持正式口吻。

## 12. 快速状态句

如果需要一句话回答当前状态：

> 当前项目已经较好复现 MSAT 的主实验和多数核心性能结果，结果目录审计为 `issues: []`；但 Table 5/6 属于外部验证和下游解释，当前公开材料下不能论文等价复现。后续最有价值的研究方向是把复现中暴露出的“未观测不等于负样本”问题转化为可靠负样本选择与 PU Learning，并结合机制子图解释和外部证据分级形成改进模型。

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
