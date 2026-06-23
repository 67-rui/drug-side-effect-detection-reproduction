# 药物副作用检测复现

本仓库用于复现 Shi et al. (2026) Frontiers in Pharmacology 论文中的 MSAT 方法：

> MSAT: a FAERS-informed heterogeneous graph neural network for pharmacovigilance prediction of Chinese materia medica-associated adverse drug reactions.

核心实现位于 `MSAT/`，论文与官方源码副本位于 `resource_副本/`。

## 当前状态

- 主实验协议已按论文 §3.5 对齐：官方 10 折、Zenodo 异构图、test 正边归纳去边、1:1 主评估、1:10 压力测试。
- Table 2 主实验和 Fig.5a FAERS-only 冷启动已基本复现；Table 4 ML baseline、Fig.6、Table 5/6、枳实案例仍需修复后重跑或审计。
- `MSAT/PROJECT_MEMORY.md` 记录当前项目记忆、已知缺口和下一步。
- `MSAT/results/reproduction_state_audit.json` 记录当前产物审计结果；若存在 `stale_artifact` 或 `suspicious_ml_auc`，对应结果不能引用。
- `MSAT/results/TABLE5_PROTOCOL_DECISION.md` 和 `MSAT/results/CHECKPOINT_RUNBOOK.md` 固化 Table 5 与 checkpoint 防污染规则。
- 大模型 checkpoint、完整图数据和运行缓存未纳入 Git；请按项目脚本或远端训练记录恢复。

## 重要目录

| 路径 | 说明 |
| --- | --- |
| `MSAT/` | 当前复现代码、实验脚本、轻量结果与报告 |
| `MSAT/results/` | 当前轻量结果摘要与 living report |
| `MSAT/scripts/audit_reproduction_state.py` | 产物状态审计脚本 |
| `MSAT/scripts/rerun_after_artifact_fix.sh` | 服务器恢复后重跑受污染链路 |
| `docs/superpowers/plans/` | 阶段计划与复现补全方案 |
| `resource_副本/fphar-17-1774128.pdf` | 论文 PDF |
| `resource_副本/MSAT-main/` | 官方开源代码副本 |

## 不纳入 Git 的内容

- `experiments_data_clean_final/complete_hetero_graph.pt`
- `MSAT/saved_models/*.pt`
- 远端训练日志、大型历史归档、Python 缓存

这些文件体积较大，适合用数据盘、对象存储或 release artifact 管理，不适合直接提交到普通 Git 仓库。

## 服务器恢复后的最小重跑

```bash
cd /root/autodl-tmp/MSAT
git pull
PY=/root/miniconda3/bin/python bash scripts/rerun_after_artifact_fix.sh
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json
```
