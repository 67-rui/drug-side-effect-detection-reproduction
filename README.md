# 药物副作用检测复现

本仓库用于复现 Shi et al. (2026) Frontiers in Pharmacology 论文中的 MSAT 方法：

> MSAT: a FAERS-informed heterogeneous graph neural network for pharmacovigilance prediction of Chinese materia medica-associated adverse drug reactions.

核心实现位于 `MSAT/`，论文与官方源码副本位于 `resource_副本/`。

## 当前状态

- 主实验协议已按论文 §3.5 对齐：官方 10 折、Zenodo 异构图、test 正边归纳去边、1:1 主评估、1:10 压力测试。
- `MSAT/PROJECT_MEMORY.md` 记录当前项目记忆与最新远端续跑状态。
- `resource_副本/MSAT_SESSION_PROGRESS_2026-06-23.md` 记录 Cursor 汇总的远端 AutoDL 训练进度。
- 大模型 checkpoint、完整图数据和运行缓存未纳入 Git；请按项目脚本或远端训练记录恢复。

## 重要目录

| 路径 | 说明 |
| --- | --- |
| `MSAT/` | 当前复现代码、实验脚本、轻量结果与报告 |
| `MSAT/results/` | 当前轻量结果摘要与 living report |
| `docs/superpowers/plans/` | 阶段计划与复现补全方案 |
| `resource_副本/fphar-17-1774128.pdf` | 论文 PDF |
| `resource_副本/MSAT-main/` | 官方开源代码副本 |

## 不纳入 Git 的内容

- `experiments_data_clean_final/complete_hetero_graph.pt`
- `MSAT/saved_models/*.pt`
- 远端训练日志、大型历史归档、Python 缓存

这些文件体积较大，适合用数据盘、对象存储或 release artifact 管理，不适合直接提交到普通 Git 仓库。
