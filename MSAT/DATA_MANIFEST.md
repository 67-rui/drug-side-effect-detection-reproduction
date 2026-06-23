# MSAT 官方数据清单（Route A）

来源: [Zenodo 10.5281/zenodo.17933842](https://zenodo.org/records/17933842)

## 文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `complete_hetero_graph.pt` | ~100 MB | PyG HeteroData，含预计算节点特征 |

## 图结构（已验证 2026-06-18）

| 节点类型 | 数量 | 特征维度 |
|----------|------|----------|
| herb (CMM) | 651 | 768 (BioBERT) |
| compound | 1,498 | 768 (ChemBERTa) |
| target | 21,393 | 768 (BioBERT) |
| adr | 5,974 | 768 (BioBERT) |

| 边类型 | 数量 | edge_attr |
|--------|------|-----------|
| herb → causes → adr | 27,062 | 6 维 |
| herb → contains → compound | 2,758 | — |
| herb → targets → target | 2,742 | — |
| target → binds → compound | 27,008 | — |
| adr → causes → target | 30,170 | — |
| target → interacts → target | 321,075 | — |
| + 反向边 | 同上 | CMM–ADR 反向边含 6 维 attr |

## 本地生成文件

| 路径 | 说明 |
|------|------|
| `MSAT/data/10fold_cv_split.pkl` | 官方 10 折划分（GitHub 上游） |
| `MSAT/data/entity_names.json` | BioBERT + ccTCM 实体名称映射（v2，含 `paper_herb_id_map`） |
| `MSAT/data/cctcm_herb_index.json` | ccTCM 651 药材索引 |
| `MSAT/saved_models/best_model_*.pt` | 训练 checkpoint |
| `MSAT/results/*.json` | 10 折 CV、基线、消融、分层、Phase 8 实验结果 |
| `MSAT/results/table5_top15.csv` | Table 5 Top-15 预测 |
| `MSAT/results/table6_mapping.csv` | Table 6 TCM 系统映射（当前依赖 stale Table 5，需重跑） |
| `MSAT/results/case_zhishi_diarrhoea.json` | §4.5.1 枳实案例（当前 stale，需 checkpoint provenance） |
| `MSAT/results/fig6_summary.json` | Fig.6 不平衡 sweep |
| `MSAT/results/baseline_neg10_summary.json` | Table 4 九基线 1:10 汇总（ML baseline 旧结果不可引用） |
| `MSAT/results/reproduction_state_audit.json` | 当前轻量产物审计 |
| `MSAT/results/TABLE5_PROTOCOL_DECISION.md` | Table 5 协议选择 |
| `MSAT/results/CHECKPOINT_RUNBOOK.md` | checkpoint 恢复与引用规则 |
| `MSAT/results/REPRODUCTION_REPORT.md` | 复现报告（含论文逐表对照 §12） |
| `experiments_data_clean_final/folds/` | 折内 dev/test npz（本地生成） |

## 实体名称词表（`MSAT/data/raw/`）

仅用于 **ID→可读名称** 对齐，**不参与** 图构建或模型训练。

| 文件 | 来源 | 用途 |
|------|------|------|
| `meddra_all_se.tsv` | SIDER 附带 MedDRA 术语表（公开） | ADR 节点名称 |
| `itcm/herb_detail.txt` | ITCM 药材详情（公开） | CMM 节点名称候选 |
| `etcm_herb_detail.txt` | ETCM（可选扩展） | 备用词表 |
| `tcmbank_herbs.xlsx` | TCMBank（可选扩展） | 备用词表 |

构建映射：

```bash
cd MSAT && python scripts/build_entity_mapping.py
```

## 折数据（历史路径说明）

| 路径 | 说明 |
|------|------|
| `folds/fold{N}_dev_neg1.npz` | 开发集（9 折正样本 + 1:1 负采样） |
| `folds/fold{N}_test_neg1.npz` | 测试集（1 折正样本 + 1:1 负采样） |
| `folds/fold{N}_meta.json` | 折元数据 |

## 下载

```bash
python3 MSAT/scripts/download_data.py
```
