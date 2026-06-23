# 论文协议代码审计（2026-06-22）

对照：`resource_副本/fphar-17-1774128.pdf` §3.5、`resource_副本/MSAT-main/` 官方最小仓库。

## ✅ 已对齐

| 论文条款 | 实现 | 文件 |
|----------|------|------|
| §3.5.1 归纳评估 | 每折仅从图中剔除 **test 正边**（双向） | `train.py`, `baselines/common.py` |
| §3.5.1 81:9:10 | 10 折 + dev 内 90/10 train/val，`RANDOM_STATE` 可复现 | `train.py`, `feature_extractor` |
| §3.5.1 1:1 负采样 | type-constrained，折内缓存 | `feature_extractor.py` |
| §3.5.2 MSAT 超参 | d=72, 8 heads, L=3, lr=4e-4, … | `config.py` |
| §3.5.2 ML 基线 | 节点特征 + **6 维 CMM–ADR 边特征** | `baselines/common.py` `pair_features` |
| §3.5.3 主实验阈值 | τ=0.5；1:10 用 val **τ\*** | `train.py` `USE_OPTIMAL_THRESHOLD` |
| §3.5.4 Fig.5a | FAERS-only 训练 → 文献 hold-out | `run_faers_only_coldstart_*.py` |
| §3.5.6 Table 5 | 全局 Top-15，排除 **全部 27062 监督正边**，OOF 打分 | `run_table5_validation.py` 默认 |
| §4.4.2 Table 6 | 优先 `paper_table6_reference.json` | `inference/paper_tables.py` |
| 模型结构 | ESA/HSP/HCI 全开 ≡ 官方 `model.py` | `model.py` |

## ⚠️ 与官方源码差异（更贴论文）

| 项 | 官方 `MSAT-main` | 当前 |
|----|------------------|------|
| 去边 | 剔除 test **全部样本对** | 仅 test **正边**（论文明文） |
| val 去边 | 不去 | 不去（已回改一致） |
| ablation 开关 | 无 | 有（服务 Table 3） |

## ❌ 仍未实现 / 非论文脚本

| 项 | 状态 |
|----|------|
| TCMDA 在线库验证 Table 5 | 无公开 API；**人工缓存** `data/tcmda_cache.json` + `inference/tcmda_validation.py` | 见下方接入路径 |
| GNN 基线超参 | 未读 Additional file 1；`GNN_HIDDEN=128,L=2` 为自设 |
| HetGNN 等实现 | 自写 `baselines/gnn_models.py`，非作者仓库 |
| `run_coldstart_eval.py` | legacy 10 折代理，**非 Fig.5a** |
| `run_table5_paper_compare.py` | 需 `--legacy`，非 §3.5.6 |
| `external_validation.py` | 论文 Table 5 手工表，**非 TCMDA 查询** |

## 待重训后验证

归纳去边 + ML 边特征变更后，Table 2/3/4/6 数值需以 `server_paper_retrain.sh` 新产出为准。

## TCMDA 接入路径（§3.5.6）

1. **注册** https://organchem.csdb.cn/（机构邮箱；联系 chemdatabase@mail.sioc.ac.cn 申请批量数据）
2. **人工查询**「中药成分毒副作用数据库」+「中药药材检索」，记录不良反应表型
3. **写入** `data/tcmda_cache.json`（或 `python scripts/import_tcmda_cache.py` 生成模板后填写）
4. **重跑** `run_table5_validation.py` → `database_verified` 来自缓存 + MedDRA 同义词匹配

**不推荐**：未授权爬虫（无 API、需登录、易违反 ToS）。

