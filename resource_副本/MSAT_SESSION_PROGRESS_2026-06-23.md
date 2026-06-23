# MSAT 复现进度与聊天上下文备忘

**更新时刻：** 2026-06-23 11:45 CST  
**工作目录：** `/Users/a67_2024/Desktop/drug-detect`  
**实现代码：** `MSAT/`  
**论文 PDF：** `resource_副本/fphar-17-1774128.pdf`  
**官方源码对照：** `resource_副本/MSAT-main/`

---

## 1. 会话目标（聊天上下文摘要）

本会话围绕 **Shi et al. 2026 Front. Pharmacol. MSAT 论文复现** 展开，目标演进如下：

1. 对照论文与本地结果，在 **AutoDL GPU** 上完成 Phase 8/9。
2. 按论文 §3.5 **回改代码协议**（非自扩实验），归档旧结果。
3. 闭合 Fig.5a、Table 5、Table 6、96.5% unseen CMM 等差距。
4. 探索 **TCMDA**（organchem.csdb.cn）接入 Table 5 `database_verified`。
5. 远端训练中途 **暂停**，次日用续跑脚本恢复。

**核心原则：** 以论文协议为准；旧 `results/` 中论文对齐前产物已归档，不得作为正式结论引用。

---

## 2. 论文对齐代码变更（2026-06-22）

| 变更 | 文件 |
|------|------|
| 归纳去边：仅剔除 test **正边**（§3.5.1） | `train.py`, `baselines/common.py`, `coldstart.py` 等 |
| ML 基线：节点 + **6 维边特征**（§3.5.2） | `baselines/common.py` |
| Table 5 默认：全局 Top-15，排除全部 27062 正边，OOF | `scripts/run_table5_validation.py` |
| Table 6：论文 Table 6 映射表 | `data/paper_table6_reference.json` |
| Fig.5a 真协议：FAERS-only → 文献 hold-out | `run_faers_only_coldstart_*.py` |
| TCMDA 缓存查库 | `inference/tcmda_validation.py`, `data/tcmda_cache.json` |
| 非论文脚本降级 | `run_coldstart_eval.py`, `run_table5_paper_compare.py --legacy` |

审计详见：`MSAT/results/PAPER_CODE_AUDIT.md`  
Living 报告：`MSAT/results/REPRODUCTION_REPORT.md`, `VERIFICATION_FINDINGS.md`

---

## 3. 远端环境（AutoDL）

| 项 | 值 |
|----|-----|
| SSH | `[redacted AutoDL SSH endpoint]` |
| 项目路径 | `/root/autodl-tmp/MSAT` |
| Python | `/root/miniconda3/bin/python` |
| 图数据 | `/root/autodl-tmp/experiments_data_clean_final/complete_hetero_graph.pt` |
| 主训练日志（昨晚） | `results/phase8_logs/paper_retrain.log` |
| **续跑日志（当前）** | `results/phase8_logs/paper_retrain_resume.log` |

> 远端登录凭据不写入仓库。

---

## 4. 实验时间线

| 时间 | 事件 |
|------|------|
| 2026-06-22 22:12 | 启动 `scripts/server_paper_retrain.sh`（论文对齐全量重训） |
| 2026-06-22 22:26 | MSAT 10 折完成，`summary.json` AUC **0.9792** |
| 2026-06-22 22:44 | MSAT 1:10 完成，`summary_neg10.json` AUC **0.871** |
| 2026-06-22 23:42 | 并行 CPU：Case study、Table 5、Table 6（未占 GPU） |
| 2026-06-23 00:29 | Table 4 基线：GAT 1:10 完成；RGCN 第 10/10 折进行中 |
| 2026-06-23 00:58 | **用户请求暂停**；kill 训练进程；上传 `server_paper_retrain_resume.sh` |
| 2026-06-23 10:34 | **续跑启动** `server_paper_retrain_resume.sh` |
| 2026-06-23 11:06 | 续跑完成 **RGCN 1:10** |
| 2026-06-23 11:45 | 续跑进行中：**HGT 1:10 第 5/10 折** |

---

## 5. 当下进度快照（2026-06-23 11:45 CST）

### 5.1 运行状态

- **状态：** `server_paper_retrain_resume.sh` **运行中**
- **当前进程：** `run_baselines.py --neg-ratio 10 --model hgt`
- **GPU：** ~29%，显存 ~5.2 GB

### 5.2 流水线完成度

| 阶段 | 状态 | 关键结果 |
|------|------|----------|
| Table 2 · MSAT 10 折 (1:1) | ✅ | AUC **0.9792**（论文 ≈0.979） |
| Table 2 · ML 基线 (1:1) | ✅ | lr / rf / xgb |
| Table 2 · GNN 基线 (1:1) | ✅ | gcn / gat / rgcn / hgt / hetnn / simple_hgn |
| Table 3 · 消融 | ✅ | `ablation_summary.json` |
| Table 4 · MSAT 1:10 | ✅ | AUC **0.871** |
| Table 4 · 1:10 基线 | 🔄 | lr/rf/xgb/gcn/gat/**rgcn** ✅；**hgt** 进行中 |
| Table 4 · 待跑 GNN | ⏳ | hetnn, simple_hgn |
| Fig.6 sweep | ⏳ | |
| Phase 9 | ⏳ | Table 5/6 等；FAERS-only 将跳过（已有有效结果） |

### 5.3 已保留的有效结果（勿归档）

| 产物 | 说明 |
|------|------|
| `faers_only_coldstart_summary.json` | Fig.5a FAERS→文献；unseen CMM **96.5%**；MSAT > GAT/HGT/Simple-HGN |
| `summary.json` | 新协议 MSAT Table 2 |
| `summary_neg10.json` | 新协议 MSAT Table 4 |
| `case_zhishi_diarrhoea.json` | 枳实/腹泻 case；score ≈ 0.963 |
| `table5_top15.csv`, `table5_summary.json` | 并行 CPU 生成（全局 Top-15；支持率 1/15 mechanistic） |
| `table6_mapping.csv` | Table 6 映射 |

### 5.4 归档

- 论文对齐前历史：`MSAT/results/archive_pre_paper_align_2026-06-22/`
- 暂停时移除的旧 neg10 GNN：`MSAT/results/archive_pre_retrain_pause_2026-06-23/`（远端）

---

## 6. TCMDA 接入状态

- **网站：** https://organchem.csdb.cn/scdb/main/tcm_introduce.asp
- **无公开 API**；论文 §3.5.6 为人工查库 + MedDRA 同义词匹配
- **尝试：** 账号 `Qirui_Liu` 多次 `requests` 登录失败（返回登录页，可能未注册/未审核）
- **当前方案：** `data/tcmda_cache.json` 由 `scripts/seed_tcmda_from_paper.py` 按论文 Table 5 的 11/15 `database_verified` 标注填充（`live_tcmda_login: false`）
- **待做：** 浏览器确认登录后运行 `TCMDA_USER=... TCMDA_PASS=... python scripts/fetch_tcmda.py --write-cache`
- **查库清单：** `MSAT/data/tcmda_lookup_checklist.md`

---

## 7. 已知问题与差距

| 项 | 状态 |
|----|------|
| GCN 1:10 AUC ≈ 0.50 | 接近随机，实现/设定待查 |
| Table 5 全局 Top-15 ≠ 论文 15 味 CMM | 预期；论文对照用 `paper_table5_reference.json` |
| Table 5 支持率 1/15（当前 OOF 全局 Top-15） | mechanistic 弱；TCMDA 缓存与 Top-15 无交集 |
| TCMDA 实时查库 | 未成功登录 |
| GNN 超参 vs Additional file 1 | 近似，非逐字复现 |
| `REPRODUCTION_REPORT.md` 部分段落 | 与最新 `case_zhishi` / Table 5 有漂移，重训后需更新 |

---

## 8. 续跑与运维命令

### 查看进度

```bash
ssh -p <port> root@<autodl-host>
tail -f /root/autodl-tmp/MSAT/results/phase8_logs/paper_retrain_resume.log
```

### 启动续跑（若已停）

```bash
cd /root/autodl-tmp/MSAT
nohup bash scripts/server_paper_retrain_resume.sh \
  > results/phase8_logs/paper_retrain_resume_nohup.log 2>&1 &
```

### 暂停

```bash
pkill -f 'run_baselines.py --neg-ratio 10'
pkill -f server_paper_retrain_resume.sh
```

**勿**重跑 `server_paper_retrain.sh`（会从 MSAT 10 折重头训练）。

### 并行 CPU（不占 GPU）

```bash
bash scripts/run_parallel_cpu.sh
```

---

## 9. 关键脚本索引

| 脚本 | 用途 |
|------|------|
| `scripts/server_paper_retrain.sh` | 全量论文对齐重训（一次性） |
| `scripts/server_paper_retrain_resume.sh` | 断点续跑（跳过已有 json） |
| `scripts/run_parallel_cpu.sh` | Table 5/6 + case study（CPU） |
| `scripts/fetch_tcmda.py` | TCMDA 登录查库（需有效账号） |
| `scripts/seed_tcmda_from_paper.py` | 从论文 Table 5 标注填充缓存 |
| `scripts/server_phase9_run.sh` | Phase 9 下游（续跑末尾调用） |

---

## 10. 下一步（优先级）

1. **等待续跑完成**：hgt → hetnn → simple_hgn → Fig.6 → Phase 9
2. **拉回本地**：新 `summary.json`、全部 baseline、Fig.6、Phase 9 产物
3. **更新** `REPRODUCTION_REPORT.md` §13 与 Table 2/4 数字
4. **TCMDA**：确认账号后实时查库，或维持论文标注缓存并注明来源
5. **Table 5 论文对照**：对论文 15 味 CMM 单独跑 `paper_table5_reference` 诊断（非全局 Top-15）
6. **Phase 9**：`RUN_FAERS_ONLY_TRAIN=0` 跳过已有效的 Fig.5a

---

## 11. 相关文档路径

```
MSAT/PROJECT_MEMORY.md
MSAT/results/PAPER_CODE_AUDIT.md
MSAT/results/REPRODUCTION_REPORT.md
MSAT/results/VERIFICATION_FINDINGS.md
MSAT/results/README.md
docs/superpowers/plans/2026-06-22-msat-completion-plan.md
docs/superpowers/plans/2026-06-18-msat-reproduction.md
resource_副本/fphar-17-1774128.pdf
resource_副本/MSAT-main/
```

---

*本文件由 Agent 根据 2026-06-22～06-23 会话自动生成，供后续对话与人工接续使用。*
