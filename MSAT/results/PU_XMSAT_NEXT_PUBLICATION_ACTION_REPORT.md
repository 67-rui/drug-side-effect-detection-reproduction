# PU-XMSAT 投稿前推进报告

**Generated:** 2026-06-29
**Scope:** 将当前 PU-XMSAT 项目从“已有实验与草稿”推进到“更接近可投稿论文包”的状态。
**Claim boundary:** 当前证据支持 incomplete-label mitigation、checkpoint-aware mechanism triage 和 evidence-aware candidate prioritization；不支持强因果、强机制确认、外部临床验证或 MSAT Table 5/6 等价复现声明。

## 1. 当前项目已经完成什么

当前已经完成三个主线层面的工作。

第一，预测主线已经具备论文主结果。MSAT 主实验复现可作为稳定 baseline；full-positive hybrid PU-XMSAT 在两个 seed 下复现出稳定提升。主结果应引用投稿级整合入口 `PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md`：baseline AUC/AUPRC/F1/MCC 为 0.979271/0.977095/0.931451/0.862520；hybrid seed 2026 为 0.980420/0.977929/0.935064/0.868409；hybrid seed 1337 为 0.980392/0.977983/0.934767/0.868331。

第二，泛化主线已经完成 cluster-held-out stress test。10 个 heldout herb/CMM clusters 的 all-fold mean AUC/AUPRC/F1/MCC 为 0.889069/0.903219/0.176976/0.191914；排除少于 5 味中药的 tiny clusters 后，non-tiny mean 为 0.843291/0.863329/0.074252/0.116753。该实验回应“先聚类，再把某个新类作为测试集”，但只能写成新中药簇泛化压力测试。

第三，解释主线已经从旧的案例展示升级为 final-checkpoint-aware mechanism triage。正式 seed 2026 full-positive hybrid checkpoint export 已完成；top5000 final predictions 中 391/5000 有显式机制路径；20 个 mechanism-supported candidates 完成关键机制子图提取、component/target/pathway 扰动贡献量化和 random controls；top20 entity mapping audit、top20 external evidence review、391 候选 evidence-aware top30 reranking 和 PubMed-only signal review 均已落地。

## 2. 哪些内容已经足够写进论文

可以作为正文结果写入的是：

- PU-XMSAT 的动机：未观测 CMM-ADR pair 不应直接视为真实负样本。
- Full-positive hybrid PU-XMSAT 的 two-seed 主结果和 paired comparison。
- PU weight sensitivity 对默认 `unlabeled_weight=0.2/reliable_negative_weight=0.8` 的支持。
- Cluster-held-out generalization 作为更严格的 cold-cluster stress test。
- Top5000 checkpoint-aware interpretability：391 个显式机制路径候选，20 个完成扰动量化。
- Random controls：真实机制路径/节点扰动与随机节点/路径对照分开报告。
- Entity-mapping audit：compound/target local IDs 当前无 confirmed mapping。
- External evidence boundary：top20 强完整链证据 0/20，top30 PubMed first-pass 也没有 strong validation。

建议论文主张写成：

> PU-XMSAT is a positive-unlabeled learning framework for incomplete CMM-ADR labels, with checkpoint-aware mechanism-path extraction and evidence-aware candidate prioritization.

## 3. 哪些内容只能作为限制或 future work

以下内容不能写成已完成贡献：

- 强机制证明：当前只能提取机制路径和局部扰动敏感性，不能证明真实生物机制链。
- 强外部验证：top20 strong complete-chain evidence 为 0/20；top30 PubMed 信号也不能升级为 Grade A/B。
- Compound/target 真实名称：公开 MSAT/Zenodo/GitHub/图文件缺 row index 到真实实体的映射桥。
- MSAT Table 5/6 等价复现：已请求原作者提供导出脚本、checkpoint、候选池定义、逐行证据和 PT/SOC 到 TCM system 映射规则，但当前不能声称复现。
- 因果结论：当前图数据没有 patient-level co-medication、indication、dose、exposure denominator、reporting propensity 等变量。

## 4. 解释性当前到底完成到什么程度

当前解释性达到的是 **mechanism triage**，不是 **strong mechanistic proof**。

已经完成：

- 从 final checkpoint top5000 predictions 中统计显式机制路径覆盖率。
- 对 20 个 mechanism-supported candidates 提取 key mechanism subgraph。
- 对 component、target、pathway 做输入置零扰动，计算 score drop。
- 加入 random node/path controls。
- 对 top20 的 compound/target local ID 做映射缺口审计。
- 对 top20 做外部证据 first-pass review。
- 从 391 个显式机制路径候选中构建 evidence-aware top30 review queue。
- 对 top30 做 PubMed-only signal screen。

当前不能完成：

- 将 `compound:761`、`target:15721` 等 local ID 确认为真实成分/真实靶点。
- 证明某个 herb 通过某个真实 compound 和 target 导致某个 ADR。
- 把扰动 score drop 写成 SHAP、因果贡献或临床机制。

## 5. 391 个机制路径候选和 20 个扰动候选如何服务论文

`391` 和 `20` 服务的是不同层次。

- 391/5000 是覆盖率和候选池结果，证明模型高分预测中有一批可解析显式机制路径，但覆盖并不密集。
- 20 是深度解释样本，证明机制路径可以进一步转化成子图、节点贡献、路径贡献和 random-control 对照。
- Evidence-aware top30 是论文案例筛选层，用来从 391 个候选中优先挑选更适合人工证据复核的候选，避免只展示模型分数最高但外部证据很弱的案例。

因此论文里应写成：top5000 coverage -> 391 explicit-path pool -> 20 perturbation-quantified candidates -> evidence-aware top30 manual-review queue。

## 6. Cluster-heldout 如何服务论文

Cluster-heldout 服务的是泛化边界，不是主性能胜利。

它可以写：

- PU-XMSAT 在新中药簇留出设置下仍保留 ranking signal。
- Cold-cluster CMM-ADR generalization 明显比官方随机 fold 更难。
- Thresholded F1/MCC 显著下降，说明不能把主实验性能直接外推到未见中药簇。

它不能写：

- 模型已经稳定泛化到所有新类中药。
- 这是外部临床验证。
- 这是因果 transportability 证明。

## 7. Case-study 候选表

建议论文使用三个角色不同的案例，而不是只挑“看起来最正向”的案例。

| 角色 | Candidate | Prediction rank / score | Explicit paths | Top contribution | Perturbation drop | External evidence status | Manuscript use |
| --- | --- | ---: | ---: | --- | ---: | --- | --- |
| Positive triage | `Polypodium glycyrrhiza -> Watery diarrhoea` | source rank 224 / 0.997507 | 7 | component `compound:761` drop 0.000310; target/path `target:15721` drop 0.001174 | 0.001174 | Moderate indirect GI-direction only; no confirmed compound/target identity | Best positive triage case, but not strong validation |
| Evidence-aware quantified queue | `Marchantia polymorpha -> Dry cough` | source rank 239 / 0.997471 | 8 | component `compound:480` drop 0.000041; target `target:11486` drop 0.0000049; path `compound:480;target:11486` drop 0.0000457 | 0.0000457 | No direct support in first-pass screen | Shows high-priority queue candidate can remain review-only |
| Boundary / negative case | `Fragaria vesca L. -> Altered state of consciousness` | source rank 2 / 0.998971 | 6 | component `compound:1073` drop 0.0000126; target `target:7213` drop 0.0000048; path `compound:1073;target:7213` drop 0.0000175 | 0.0000175 | Weak-to-negative boundary; EMA wild-strawberry leaf summary does not support notable adverse effects | Shows perturbation sensitivity is not external validation |

Additional review-only conflict candidate:

| Candidate | Why keep in review queue | Current boundary |
| --- | --- | --- |
| `Marchantia polymorpha -> Liver injury` | Evidence-aware top30 rank 6; source rank 414; score 0.997034; 8 explicit paths; PubMed-only first-pass retained two text-match records | PubMed records are hepatoprotective / chemically induced liver-injury model evidence, not adverse-reaction validation; this case still needs perturbation quantification before being used as a full interpretability case |

## 8. 投稿前还缺什么

根据 submission readiness audit，机器检查已通过，但投稿仍不是 ready。

Human blockers:

- 作者、单位、城市/国家、邮箱、通讯作者信息。
- 目标期刊/会议、venue metadata、日期、地点、DOI/ISBN/copyright。
- ACM CCS concepts 需要用目标 venue 和导师意见确认。
- Funding / acknowledgments 需要最终文本。
- AI assistance disclosure 需要按目标 venue policy 修订。
- Double-blind policy 需要确认；如双盲，需要匿名化 review 版。
- Reference、figure、table 编号和范围需要导师最终确认。
- 原作者 mapping / Table 5/6 materials 是否回复。
- 是否把主项目成果推送到 GitHub，以及是否同步 Overleaf Git 仓库。

## 9. 当前最值得继续推进的 3 件事

1. **论文整合审阅。** 以当前 `main.tex` 为中心，检查 abstract、RQ 表、Methods、Results、Discussion 是否一致写成 PU learning + mechanism triage，而不是强机制验证。
2. **Case-study 手工证据表。** 围绕 Polypodium、Marchantia、Fragaria 三类角色，继续补手工文献/数据库证据，但只升级证据等级，不硬凑强验证。
3. **原作者映射等待与备选计划。** 等待 GitHub issue / 邮件回复；若无回复，再决定是否投入 source-ID bridge 或 candidate-only mapping 的人工核查。

## 10. 当前不建议继续投入的方向

不建议优先做：

- 继续盲目长训，只为追求微小指标提升。
- 现在强行写 causal model 或 causal effect。
- 把 DeepSeek/LLM 标注作为核心验证证据。
- 大规模人工检索 391 条候选而没有 evidence-aware prioritization。
- 在没有映射表的情况下猜测 compound/target 真实名称。
- 把 cluster-heldout 包装成新类泛化成功。

## 11. 是否需要等待原作者

需要等待原作者的是强生物语义解释，不是整篇论文。

如果原作者提供 compound/target mapping、raw entity tables、Table 5/6 scripts 和 row-level evidence，解释层可以升级为更接近真实机制链的案例分析。若没有回复，论文仍可按保守路线成立，但必须把 local ID mapping 缺口写进 limitations 和 future work。

## 12. 是否建议提交/推送

建议先提交主项目当前成果，提交前必须通过：

- `PYTHONPATH=. pytest tests -q`
- `git diff --check`
- `latexmk -pdf -interaction=nonstopmode main.tex` 或等价 LaTeX 编译检查

本报告已随主项目成果提交到 `codex/pu-xmsat-implementation`。是否 push 到远端应由用户确认，因为主项目不是 Overleaf 论文仓库。

## 13. 当下 git 状态

最终验证后，当前分支为 `codex/pu-xmsat-implementation`，工作树干净，分支相对 `origin/codex/pu-xmsat-implementation` ahead 1。最新提交信息为：

`Integrate PU-XMSAT publication triage package`

该提交包含已对齐本阶段目标的成果，核心类别如下：

- Cluster-heldout robust summary: `PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`、`cluster_holdout_generalization_summary.json`、`summarize_cluster_holdout_generalization.py`、对应测试。
- Evidence-aware interpretability: `PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`、`PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`、`build_evidence_aware_candidate_queue.py`、对应测试和 literature cache。
- Entity/evidence boundary: `PU_XMSAT_ENTITY_MAPPING_AUDIT_AND_CANDIDATES.md`、`PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md`、`PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md`、`PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md`、相关脚本/测试。
- Original-author request: `PU_XMSAT_ORIGINAL_AUTHOR_MAPPING_REQUEST.md`。
- Paper integration: `Template/PU-XMSAT-Overleaf/main.tex`、`references.bib`。
- Project memory/index: `PROJECT_MEMORY.md`、`results/README.md`、`PU_XMSAT_DELIVERABLE_INDEX_CN.md`。
- This action report: `PU_XMSAT_NEXT_PUBLICATION_ACTION_REPORT.md`。

这些改动已作为“投稿前强化版整合”提交；当前只剩是否推送到远端需要用户确认。
