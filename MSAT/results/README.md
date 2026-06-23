# MSAT 复现结果目录

| 位置 | 说明 |
|------|------|
| **`results/` 根目录** | 当前有效结果 +  living 报告 |
| **`archive_pre_paper_align_2026-06-22/`** | 论文对齐**前**的历史 JSON/CSV/日志（勿引用为正式复现） |

## 当前可引用性

先运行审计：

```bash
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json
```

如果审计中出现 `stale_artifact`、`suspicious_ml_auc` 或 `missing_provenance`，对应结果不能作为最终复现结论引用。

## 结果状态（论文协议）

| 文件 | 论文对应 | 当前状态 |
|------|----------|----------|
| `summary.json` | Table 2（重训后） | 可引用 |
| `summary_neg10.json` | Table 4 MSAT 1:10 | 可引用为 MSAT 单模型结果 |
| `baseline_neg10_summary.json` | Table 4 全模型 | 不可引用；LR/RF/XGB 为泄漏修复前旧结果 |
| `fig6_summary.json` | Fig.6 | 部分不对齐；ratio 2/5 当前 HGT 高于 MSAT |
| `faers_only_coldstart_summary.json` | Fig.5a §3.5.4 | 可引用 |
| `table5_top15.csv` / `table5_summary.json` | Table 5 §3.5.6 | stale；需按 `TABLE5_PROTOCOL_DECISION.md` 重跑 |
| `table6_mapping.csv` / `.json` | Table 6 | stale；依赖 stale Table 5 |
| `case_zhishi_diarrhoea.json` | §4.5.1 案例 | stale；需按 `CHECKPOINT_RUNBOOK.md` 重跑 |

详见 `PAPER_CODE_AUDIT.md`、`FINAL_REMOTE_RUN_SUMMARY_2026-06-23.md`、`TABLE5_PROTOCOL_DECISION.md`。
