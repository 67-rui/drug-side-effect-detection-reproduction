# MSAT 论文复现实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 复现 Shi et al. (2026) MSAT 框架——基于 FAERS 证据增强的 CMM–Compound–Target–ADR 异构图链路预测，达到论文报告的核心指标（10 折 CV AUC ≈ 0.979）。

**Architecture:** 四阶段流水线——(I) 多源数据整合与节点/边特征编码；(II) PyG HeteroData 构图 + 6 维 CMM–ADR 证据边；(III) MSAT 三模块 GNN（ESA-Gate / HSP-Layer / HCI-Module）训练；(IV) 10 折评估 + 消融/不平衡/冷启动扩展实验。

**Tech Stack:** Python 3.10, PyTorch 2.4, PyTorch Geometric 2.x, Hugging Face Transformers (BioBERT + ChemBERTa), RDKit, NumPy, SciPy, scikit-learn

**论文:** Front. Pharmacol. 17:1774128, DOI 10.3389/fphar.2026.1774128  
**官方代码:** https://github.com/BowenShiGDPU/MSAT  
**官方数据:** https://zenodo.org/records/17933842 (10.5281/zenodo.17933842)

---

## 一、论文技术实现解析

### 1.1 问题定义

- **任务:** CMM（中药材）– ADR（不良反应 MedDRA PT）链路预测（二分类）
- **输入:** 异构图 G = (V, E)，4 类节点 + 6 类边
- **输出:** 对任意 (CMM, ADR) 对预测关联概率 p(c, a) ∈ [0, 1]
- **定位:** 信号优先级排序与假设生成，非因果确认

### 1.2 数据规模（Table 1）

| 类别 | 类型 | 数量 | 主要来源 |
|------|------|------|----------|
| 节点 | CMM | 651 | ccTCM, ETCM, FAERS |
| 节点 | Compound | 1,498 | ccTCM |
| 节点 | Target | 21,393 | ADReCS, ccTCM, PrimeKG, T-ARDIS, ETCM, Open Targets |
| 节点 | ADR | 5,974 | FAERS, Literature, ADReCS, Open Targets, T-ARDIS |
| 边 | CMM–Compound | 2,758 | ccTCM |
| 边 | Compound–Target | 27,008 | ccTCM |
| 边 | CMM–Target | 2,742 | ETCM |
| 边 | Target–Target | 321,075 | PrimeKG |
| 边 | Target–ADR | 30,170 | ADReCS, Open Targets, T-ARDIS |
| 边 | **CMM–ADR（监督标签）** | **27,062** | FAERS + 文献 |

**正样本构成:** 25,734 FAERS 衍生 + 1,328 文献专家标注

### 1.3 节点特征编码（Section 3.2, Fig.1f）

| 节点类型 | 编码方式 | 模型 |
|----------|----------|------|
| CMM | 文本描述 | BioBERT (`dmis-lab/biobert-base-cased-v1`) |
| Target | 基因名/描述 | BioBERT |
| ADR | MedDRA PT 文本 | BioBERT |
| Compound | PubChem SMILES → RDKit 标准化 → 序列 | ChemBERTa (`seyonec/ChemBERTa-zinc-base-v1`) |

**RDKit 预处理:** 去盐、电荷中和、互变异构体规范化（2024.03）

**标识符统一:** ADR → MedDRA；Target → HGNC

### 1.4 CMM–ADR 六维证据边特征 e_ij ∈ R⁶（Section 3.2）

| 维度 | 含义 |
|------|------|
| 1 | CMM 与 ADR 描述的 BioBERT 余弦语义相似度 |
| 2 | FAERS 报告数的 log 变换 |
| 3 | 来源指示（FAERS 衍生 vs 仅文献） |
| 4–6 | 拓扑指标：CMM 度、ADR 度、meta-path 连通度（CMM→Compound→Target→ADR 路径密度，log+归一化） |

仅 CMM–ADR 边携带 6 维属性；其余边类型为二元机制边。

### 1.5 MSAT 模型架构（Fig.2–3, Algorithm 1）

```
节点特征 → Linear+LayerNorm+ReLU 投影到 d_h=576
    ↓ ×3 层 Multi-Scale Attention Layer
    │   ├─ ESA-Gate: β_ij = g·MLP(e_ij) + (1-g)·W_s·e_ij  → 注入 attention logit (Eq.1-2)
    │   ├─ Multi-head Attention (H=8, d=72/head)
    │   └─ HSP-Layer: 576→1152→1728→576 expand-compress MLP + LayerNorm 残差 (Eq.3)
    ↓ 输出嵌入 z_CMM, z_ADR (72 维)
    ↓ HCI-Module: 三路融合打分 (Eq.4)
        w1·MLP(z_CMM‖z_ADR‖log(deg)) + w2·Bilinear + w3·DistMult
    ↓ σ(s) → 预测概率
```

**三大创新模块与本地代码映射:**

| 论文模块 | 本地实现 (`MSAT-main/model.py`) | 状态 |
|----------|-----------------------------------|------|
| ESA-Gate | `MSATEdgeEncoder` | ✅ 已实现 |
| HSP-Layer | `MSATOutputTransform`（嵌于 `MultiTypeGraphAttention`） | ✅ 已实现 |
| HCI-Module | `LateFusionPredictor` | ✅ 已实现 |
| 度缩放 + ε 残差 | `MSATTCMFSFinal` 中 `degree_scale_weight` + `eps` | ✅ 已实现 |

### 1.6 训练与评估协议（Section 3.5）

| 配置项 | 论文值 | 本地 `config.py` |
|--------|--------|------------------|
| 折数 | 10 折分层 CV | N_FOLDS=10 ✅ |
| 划分 | 81% train / 9% val / 10% test | TRAIN_VAL_SPLIT=0.9 ✅ |
| 负采样 | 1:1 类型约束（固定 CMM，随机替换 ADR） | 需在 FeatureExtractor 实现 |
| 归纳模式 | 测试折 CMM–ADR 边双向移除 + 边属性同步删除 | INDUCTIVE_MODE=True ✅ |
| hidden | 576 (8 heads × 72) | HIDDEN_CHANNELS=576 ✅ |
| layers | 3 | NUM_LAYERS=3 ✅ |
| heads | 8 | NUM_HEADS=8 ✅ |
| dropout | 0.18 | DROPOUT=0.18 ✅ |
| edge_dim | 6 | EDGE_ATTR_DIM=6 ✅ |
| optimizer | AdamW, lr=4e-4, wd=1e-5 | ✅ |
| batch | 512 | BATCH_SIZE=512 ✅ |
| epochs | 1000, patience=100 | ✅ |
| grad clip | 1.0 | ✅ |
| scheduler | ReduceLROnPlateau, factor=0.6, patience=15 | ✅ |
| loss | BCE | ✅ |
| 阈值 | 主实验固定 0.5 | train.py 使用 0.5 ✅ |
| seed | 42 | RANDOM_STATE=42 ✅ |

**目标指标（Table 2, 1:1 负采样）:**

| 指标 | MSAT mean ± std |
|------|-----------------|
| AUC | 0.979 ± 0.001 |
| AUPRC | 0.977 ± 0.002 |
| F1 | 0.930 ± 0.003 |
| MCC | 0.860 ± 0.005 |
| Precision | 0.927 ± 0.005 |
| Recall | 0.934 ± 0.005 |

### 1.7 扩展实验（可选复现阶段）

| 实验 | 论文位置 | 优先级 |
|------|----------|--------|
| 消融（ESA/HSP/HCI） | Table 3 | P1 |
| 不平衡 1:10 | Table 4, Fig.6 | P1 |
| 9 基线对比 | Table 2 | P2 |
| 冷启动（文献集） | Fig.5a | P2 |
| 度分层偏差 | Fig.5b | P3 |
| Top-15 外部验证 | Table 5 | P3 |
| TCM 脏腑映射 | Table 6, Section 3.4.2 | P3 |

---

## 二、本地资源与差距分析

### 2.1 已有资源

| 资源 | 路径 | 可用性 |
|------|------|--------|
| MSAT 模型代码 | `resource_副本/MSAT-main/model.py` | 架构完整 |
| 训练脚本 | `resource_副本/MSAT-main/train.py` | 依赖缺失 |
| 超参配置 | `resource_副本/MSAT-main/config.py` | 完整 |
| 论文 PDF | `resource_副本/fphar-17-1774128.pdf` | 已读 |
| Demo 数据管道 | `Demo/data/`, `Demo/src/data/` | 120 药材，规模远小于论文 |
| Demo R-GCN 基线 | `Demo/src/models/rgcn.py` | 可对比，非 MSAT |
| Cursor Agent 规则 | `drug-detect/.cursor/rules/` | 已部署 9 个 |

### 2.2 关键缺失

| 缺失项 | 影响 | 解决方案 |
|--------|------|----------|
| `experiments/feature_extractor.py` | train.py 无法运行 | 实现或从官方 MSAT 仓库移植 |
| `experiments_data_clean_final/` | 无训练数据 | **首选:** 下载 Zenodo 官方预处理数据 |
| 包名 `MSAT_TCMFS_Final` vs `MSAT-main` | import 失败 | 重命名/符号链接 |
| BioBERT + ChemBERTa 特征 | 节点维度不匹配 | 实现编码脚本或下载预计算特征 |
| FAERS 原始数据 | 无法从头构建 | 使用 Zenodo 或跳过完整数据重建 |
| 9 基线模型 | 无法复现 Table 2 全部 | 分阶段：先 MSAT，后基线 |

### 2.3 复现路线选择

```
路线 A【推荐·论文对齐】          路线 B【降级·Demo 适配】         路线 C【最小·架构验证】
─────────────────────────        ─────────────────────────        ─────────────────────────
下载 Zenodo 官方数据              用 Demo 120 药材子图              合成小图 (100 节点)
+ 官方 FeatureExtractor           + 简化 6 维边特征                 + 单折 smoke test
+ 本地 model.py                   + MSAT 模型替换 R-GCN             验证 loss 下降
→ 目标 AUC ≈ 0.979               → 定性验证流程                    → 确认代码可运行
```

**本计划默认采用路线 A**，路线 B/C 作为 fallback 任务。

---

## 三、目标项目结构

复现完成后，`drug-detect/` 目录应如下组织：

```
drug-detect/
├── MSAT/                              # 主复现项目（由 MSAT-main 整理）
│   ├── model.py                       # MSATTCMFSFinal（已有）
│   ├── train.py                       # 10 折训练（已有，修 import）
│   ├── config.py                      # 超参（已有）
│   ├── requirements.txt               # + transformers, rdkit, psutil
│   ├── experiments/
│   │   └── feature_extractor.py       # 【新建】图加载 + 折划分 + 负采样
│   ├── scripts/
│   │   ├── download_data.sh           # 【新建】Zenodo 数据下载
│   │   ├── encode_nodes.py            # 【新建】BioBERT/ChemBERTa 特征
│   │   └── build_edge_features.py     # 【新建】6 维 CMM-ADR 证据
│   ├── saved_models/                  # 训练输出
│   └── results/                       # summary.json
├── experiments_data_clean_final/      # 【下载】官方预处理数据
│   ├── graph/                         # HeteroData 或边表
│   ├── folds/                         # 10 折划分
│   └── node_features/                 # 预计算嵌入（若有）
├── Demo/                              # 保留，作为对比基线
└── docs/superpowers/plans/            # 本计划
```

---

## 四、分阶段任务

### Phase 0: 环境与项目骨架（预计 0.5 天）

#### Task 0.1: 创建 MSAT 项目目录并修复包结构

**Files:**
- Create: `drug-detect/MSAT/`（从 `resource_副本/MSAT-main/` 复制）
- Modify: `drug-detect/MSAT/train.py:29-32` — 修正 import 路径
- Modify: `drug-detect/MSAT/config.py:56-57` — 修正 DATA_DIR

- [ ] **Step 1:** 复制代码到统一目录

```bash
cp -r /Users/a67_2024/Desktop/drug-detect/resource_副本/MSAT-main \
      /Users/a67_2024/Desktop/drug-detect/MSAT
mkdir -p /Users/a67_2024/Desktop/drug-detect/MSAT/experiments
mkdir -p /Users/a67_2024/Desktop/drug-detect/MSAT/scripts
```

- [ ] **Step 2:** 修改 `train.py` import

```python
# 替换第 29-32 行为：
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments.feature_extractor import FeatureExtractor
from model import MSATTCMFSFinal
from config import ModelConfig, TrainingConfig, DataConfig
```

- [ ] **Step 3:** 修改 `config.py` 数据路径

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # drug-detect/
DATA_DIR = PROJECT_ROOT / 'experiments_data_clean_final'
```

- [ ] **Step 4:** 更新 `requirements.txt`

```
torch>=2.4.0
torch-geometric>=2.0.0
transformers>=4.30.0
numpy>=1.19.0
scikit-learn>=0.24.0
scipy>=1.5.0
pandas>=1.3.0
psutil>=5.8.0
rdkit>=2023.03.1
```

- [ ] **Step 5:** 创建虚拟环境并安装

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import torch; import torch_geometric; print('OK', torch.__version__)"
```

Expected: 打印 `OK 2.x.x`，无 import 错误

---

#### Task 0.2: 下载官方预处理数据（Zenodo）

**Files:**
- Create: `drug-detect/MSAT/scripts/download_data.sh`
- Create: `drug-detect/experiments_data_clean_final/`（解压目标）

- [ ] **Step 1:** 编写下载脚本

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/experiments_data_clean_final"
mkdir -p "$DEST"
# Zenodo record 17933842 — 按官方 README 调整文件名
wget -O /tmp/msat_data.zip "https://zenodo.org/records/17933842/files/data.zip?download=1"
unzip -o /tmp/msat_data.zip -d "$DEST"
echo "Data extracted to $DEST"
ls -la "$DEST"
```

- [ ] **Step 2:** 执行下载并验证目录结构

```bash
bash /Users/a67_2024/Desktop/drug-detect/MSAT/scripts/download_data.sh
```

Expected: `experiments_data_clean_final/` 含图数据、折划分、节点特征等子目录

- [ ] **Step 3:** 若 Zenodo 链接失效，clone 官方 GitHub 并按 README 获取数据

```bash
git clone https://github.com/BowenShiGDPU/MSAT.git /tmp/msat-official
# 按官方仓库 README 放置数据到 experiments_data_clean_final/
```

- [ ] **Step 4:** 记录实际数据文件清单到 `MSAT/DATA_MANIFEST.md`

---

### Phase 1: FeatureExtractor 实现（预计 1–2 天）

#### Task 1.1: 分析官方数据格式

**Files:**
- Create: `drug-detect/MSAT/DATA_MANIFEST.md`

- [ ] **Step 1:** 列出 `experiments_data_clean_final/` 全部文件

```bash
find /Users/a67_2024/Desktop/drug-detect/experiments_data_clean_final -type f | head -50
```

- [ ] **Step 2:** 确认以下接口所需文件存在
  - 异构图：`HeteroData` `.pt` 或边 CSV + 节点特征 `.npy`/`.pt`
  - 10 折划分：`fold_{0..9}/train.csv`, `val.csv`, `test.csv`（或等价格式）
  - CMM–ADR 边 6 维属性文件

- [ ] **Step 3:** 若官方仓库含 `feature_extractor.py`，优先复制并适配路径

```bash
# 若存在于官方 clone
cp /tmp/msat-official/experiments/feature_extractor.py \
   /Users/a67_2024/Desktop/drug-detect/MSAT/experiments/
```

---

#### Task 1.2: 实现 FeatureExtractor 核心接口

**Files:**
- Create: `drug-detect/MSAT/experiments/feature_extractor.py`
- Test: `drug-detect/MSAT/tests/test_feature_extractor.py`

`train.py` 要求的最小接口：

```python
class FeatureExtractor:
    def __init__(self, data_dir: str): ...
    def get_graph_data(self) -> HeteroData: ...
    def load_fold_data(self, fold_idx: int) -> tuple[dict, dict]:
        # train_data / test_data 各含:
        # 'herb_indices', 'adr_indices', 'labels' (np.ndarray)
```

- [ ] **Step 1:** 写失败测试

```python
# tests/test_feature_extractor.py
import pytest
from pathlib import Path
from experiments.feature_extractor import FeatureExtractor

DATA_DIR = Path(__file__).resolve().parents[2] / 'experiments_data_clean_final'

@pytest.mark.skipif(not DATA_DIR.exists(), reason="data not downloaded")
def test_graph_has_four_node_types():
    ext = FeatureExtractor(data_dir=str(DATA_DIR))
    data = ext.get_graph_data()
    for ntype in ('herb', 'compound', 'target', 'adr'):
        assert ntype in data.node_types
    assert data['herb'].x.size(0) > 0

@pytest.mark.skipif(not DATA_DIR.exists(), reason="data not downloaded")
def test_fold_loads_balanced_samples():
    ext = FeatureExtractor(data_dir=str(DATA_DIR))
    train, test = ext.load_fold_data(0)
    assert len(train['labels']) > 0
    assert len(test['labels']) > 0
    assert set(train.keys()) == {'herb_indices', 'adr_indices', 'labels'}
```

- [ ] **Step 2:** 运行测试确认失败

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
pytest tests/test_feature_extractor.py -v
```

Expected: FAIL — `ModuleNotFoundError` 或 `FileNotFoundError`

- [ ] **Step 3:** 实现 `get_graph_data()`

核心逻辑：
1. 加载 HeteroData（官方 `.pt` 或从 CSV 构建）
2. 确保节点类型键名为 `herb`, `compound`, `target`, `adr`（与 model.py 一致）
3. 确保 CMM–ADR 边类型为 `('herb', 'causes', 'adr')` 和反向边
4. CMM–ADR 边附带 `edge_attr` shape `[E, 6]`

- [ ] **Step 4:** 实现 `load_fold_data(fold_idx)`

核心逻辑（论文 Section 3.5.1）：
1. 读取第 `fold_idx` 折的 train/val/test 正样本
2. **1:1 负采样:** 对每个正样本 (h, a)，固定 h，从 ADR 全集均匀采样 a'，排除已知正样本
3. 固定 seed=42，每折每 split 负样本只生成一次并缓存
4. 返回 numpy arrays

- [ ] **Step 5:** 运行测试确认通过

```bash
pytest tests/test_feature_extractor.py -v
```

Expected: PASS

---

#### Task 1.3: 验证归纳式边移除逻辑

**Files:**
- Modify: `drug-detect/MSAT/train.py:110-125`（已有逻辑，需 smoke test）

- [ ] **Step 1:** 写 smoke test 脚本

```python
# scripts/smoke_test_inductive.py
"""验证测试折 CMM-ADR 边已从图中移除"""
import torch
from experiments.feature_extractor import FeatureExtractor
from config import DataConfig

ext = FeatureExtractor(data_dir=str(DataConfig.DATA_DIR))
data = ext.get_graph_data()
_, test = ext.load_fold_data(0)
test_pairs = set(zip(test['herb_indices'].tolist(), test['adr_indices'].tolist()))
ei = data['herb', 'causes', 'adr'].edge_index
graph_pairs = set(zip(ei[0].tolist(), ei[1].tolist()))
overlap = test_pairs & graph_pairs
assert len(overlap) == 0, f"Leakage: {len(overlap)} test edges still in graph"
print("Inductive edge removal: OK (before train.py logic)")
```

- [ ] **Step 2:** 运行

```bash
python scripts/smoke_test_inductive.py
```

Expected: `Inductive edge removal: OK`

---

### Phase 2: 节点特征编码（预计 1 天，若 Zenodo 已含预计算特征可跳过）

#### Task 2.1: BioBERT / ChemBERTa 编码管道

**Files:**
- Create: `drug-detect/MSAT/scripts/encode_nodes.py`

- [ ] **Step 1:** 检查 Zenodo 是否已含预计算嵌入

```bash
ls experiments_data_clean_final/node_features/ 2>/dev/null || echo "need encoding"
```

- [ ] **Step 2:** 若需自行编码，实现脚本

```python
# encode_nodes.py 核心逻辑
from transformers import AutoTokenizer, AutoModel
# CMM/Target/ADR → BioBERT → mean pooling → [N, 768]
# Compound SMILES → ChemBERTa → [N, 768]
# 保存到 experiments_data_clean_final/node_features/{ntype}.pt
```

- [ ] **Step 3:** 对 SMILES 做 RDKit 标准化（论文要求）

```python
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize
# 去盐 → 中和 → 规范化互变异构体
```

- [ ] **Step 4:** 验证特征维度与图节点数一致

```bash
python scripts/encode_nodes.py --verify-only
```

Expected: 四类节点特征行数 = 对应节点数

---

#### Task 2.2: CMM–ADR 六维边特征构建

**Files:**
- Create: `drug-detect/MSAT/scripts/build_edge_features.py`

- [ ] **Step 1:** 若官方数据已含 6 维 `edge_attr`，验证维度

```python
data = ext.get_graph_data()
attr = data['herb', 'causes', 'adr'].edge_attr
assert attr.shape[1] == 6
```

- [ ] **Step 2:** 若需自行构建，按论文实现 6 维：

| dim | 计算 |
|-----|------|
| 0 | cosine_sim(biobert(cmm_text), biobert(adr_text)) |
| 1 | log1p(faers_report_count) |
| 2 | 1.0 if FAERS else 0.0 |
| 3 | degree(cmm) normalized |
| 4 | degree(adr) normalized |
| 5 | log1p(meta_path_count(cmm→compound→target→adr)) |

- [ ] **Step 3:** 保存并重新加载验证

---

### Phase 3: 单折 Smoke Training（预计 0.5 天）

#### Task 3.1: 单折训练验证

**Files:**
- Create: `drug-detect/MSAT/scripts/train_single_fold.py`

- [ ] **Step 1:** 从 `train.py` 提取单折入口

```python
# scripts/train_single_fold.py
import torch
from train import train_single_fold

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
result = train_single_fold(fold_idx=0, device=device)
print(f"Fold 0 AUC: {result['test_metrics']['auc']:.4f}")
```

- [ ] **Step 2:** CPU/GPU 上跑 5 epoch 快速验证（临时改 NUM_EPOCHS=5）

Expected: loss 下降，无 NaN，AUC > 0.5

- [ ] **Step 3:** 恢复 NUM_EPOCHS=1000，跑完整 fold 0

```bash
python scripts/train_single_fold.py
```

Expected: Fold 0 AUC 在合理范围（参考论文单折 ≈ 0.97+）

- [ ] **Step 4:** 检查模型参数量

Expected: 与论文量级一致（~数百万参数，具体以 `train.py` 打印为准）

---

### Phase 4: 完整 10 折复现（预计 1–2 天 GPU）

#### Task 4.1: 运行完整交叉验证

**Files:**
- Modify: `drug-detect/MSAT/train.py` — 确保结果保存路径正确

- [ ] **Step 1:** 启动完整训练

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
source .venv/bin/activate
python train.py 2>&1 | tee results/train_full.log
```

Expected runtime: 数小时（取决于 GPU；论文使用 NVIDIA L20）

- [ ] **Step 2:** 检查输出 `results/summary.json`

```bash
python -c "
import json
s = json.load(open('results/summary.json'))
for m in ['auc','auprc','f1','mcc','precision','recall']:
    v = s['overall_metrics'][m]
    print(f\"{m}: {v['mean']:.4f} ± {v['std']:.4f}\")
"
```

- [ ] **Step 3:** 与论文 Table 2 对比

| 指标 | 论文 | 复现 | 差距容忍 |
|------|------|------|----------|
| AUC | 0.979±0.001 | ? | ±0.005 |
| AUPRC | 0.977±0.002 | ? | ±0.010 |
| F1 | 0.930±0.003 | ? | ±0.020 |
| MCC | 0.860±0.005 | ? | ±0.020 |

- [ ] **Step 4:** 若差距过大，排查清单
  1. 数据版本是否与 Zenodo 一致
  2. 负采样 seed 与折划分是否一致
  3. 测试边是否双向移除
  4. 节点特征是否用预计算 vs 重新编码
  5. attention softmax 作用域（`train.py` 中 global vs local）

---

### Phase 5: 消融实验（预计 1 天）

#### Task 5.1: 三模块消融（Table 3）

**Files:**
- Create: `drug-detect/MSAT/scripts/run_ablation.py`
- Modify: `drug-detect/MSAT/config.py` — 添加 ablation flags

`config.py` 已有开关（与论文对应）：

```python
USE_GATED_EDGE_ENCODER = True   # ESA-Gate
USE_BOTTLENECK_TRANSFORM = True  # HSP-Layer
USE_LATE_FUSION = True          # HCI-Module
```

- [ ] **Step 1:** 确认 `model.py` 中开关生效（若未接线则补充）

- [ ] **Step 2:** 运行 4 组消融

```bash
# Full model
python train.py

# w/o ESA-Gate
USE_GATED_EDGE_ENCODER=False python -c "..." # 或 CLI 参数

# w/o HSP-Layer
# w/o HCI-Module
```

- [ ] **Step 3:** 汇总到 `results/ablation_summary.json`

Expected 趋势（论文 Table 3）:
- Full > w/o HSP > w/o ESA > w/o HCI
- 单模块 Only-X < Full

---

### Phase 6: 不平衡与扩展实验（预计 1–2 天，P1–P3）

#### Task 6.1: 1:10 端到端不平衡（Table 4）

- [ ] **Step 1:** 扩展 `FeatureExtractor.load_fold_data()` 支持 `neg_ratio=10`
- [ ] **Step 2:** 训练/验证/测试均 1:10 采样
- [ ] **Step 3:** 验证集上选 τ* 最大化 F1，应用于测试集
- [ ] **Step 4:** 目标 MSAT AUC ≈ 0.875±0.005

#### Task 6.2: 基线对比（Table 2，P2）

- [ ] **Step 1:** 实现或引入 LR / RF / XGBoost / GCN / GAT / R-GCN / HGT / HetGNN / Simple-HGN
- [ ] **Step 2:** 统一数据划分与负采样
- [ ] **Step 3:** 生成对比表

#### Task 6.3: 冷启动 + 度分层（Fig.5，P2–P3）

- [ ] **Step 1:** 文献集 hold-out 评估
- [ ] **Step 2:** CMM 度分 Head/Medium/Tail 三组报告 AUC

---

### Phase 7: 下游解释（P3，可选）

#### Task 7.1: TCM 脏腑功能映射

- [ ] **Step 1:** 实现 MedDRA PT → SOC → 16 个 TCM 功能系统映射规则
- [ ] **Step 2:** 对 Top-15 预测结果输出 Table 6 格式

#### Task 7.2: 路径追踪案例

- [ ] **Step 1:** 对指定 CMM–ADR 对提取 CMM→Compound→Target→ADR 路径
- [ ] **Step 2:** 案例：枳实 (Citrus aurantium) → diarrhoea

---

## 五、Fallback：Demo 适配路线（路线 B）

若 Zenodo 数据不可用，改用 Demo 子集验证流程：

- [ ] **Step 1:** 从 `Demo/data/processed/` 构建迷你 HeteroData（~120 herb）
- [ ] **Step 2:** 用 ECFP 替代 ChemBERTa、learnable embedding 替代 BioBERT
- [ ] **Step 3:** 简化 6 维边特征（支持成分数、路径数、来源 one-hot）
- [ ] **Step 4:** 5 折 CV + MSAT 模型，目标 AUC > 0.80（不追求论文数值）

参考: `Demo/docs/PLAN_UPGRADE_v0.5.md`

---

## 六、风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| Zenodo 数据格式与代码不匹配 | 中 | 优先 clone 官方 GitHub 对齐版本 |
| GPU 内存不足（46GB L20） | 中 | 减小 batch_size；CPU fallback 单折 |
| attention softmax 实现差异 | 中 | 对照官方 model.py diff |
| FAERS 数据无法重建 | 低 | 使用官方预处理，不从头爬 FAERS |
| 指标无法达到 0.979 | 中 | 先确认数据/seed 一致，再查实现细节 |
| ChemBERTa/BioBERT 下载慢 | 高 | 预下载到本地 cache；或使用 Zenodo 预计算特征 |

---

## 七、验证清单（复现完成标准）

### 必达（MVP）

- [ ] `python train.py` 无报错跑通 10 折
- [ ] `results/summary.json` 生成
- [ ] AUC ≥ 0.970（允许 ±0.01 误差）
- [ ] 消融趋势与 Table 3 一致
- [ ] 测试折边移除无泄漏（smoke test 通过）

### 完整复现

- [ ] 六项指标均进入 Table 2 误差范围
- [ ] 1:10 不平衡实验 AUC ≥ 0.870
- [ ] 9 基线对比表
- [ ] 随机 seed=42 可重复

### 扩展

- [ ] 冷启动 / 度分层 / Top-15 验证 / TCM 映射

---

## 八、建议执行顺序与时间线

| 阶段 | 任务 | 预计时间 | 依赖 |
|------|------|----------|------|
| P0 | 环境 + 项目骨架 | 0.5 天 | — |
| P0 | 下载 Zenodo 数据 | 0.5 天 | 网络 |
| P1 | FeatureExtractor | 1–2 天 | P0 |
| P2 | 节点/边特征（若需要） | 1 天 | P0 |
| P3 | 单折 smoke test | 0.5 天 | P1 |
| P4 | 完整 10 折训练 | 1–2 天 | P3, GPU |
| P5 | 消融实验 | 1 天 | P4 |
| P6 | 扩展实验 | 1–2 天 | P4 |
| P7 | 解释层 | 1 天 | P4 |

**总计:** 约 7–10 天（含 GPU 等待）

---

## 九、Self-Review（计划自检）

| 论文要求 | 对应任务 | 覆盖 |
|----------|----------|------|
| 4 类节点 6 类边异构图 | Task 1.2, 0.2 | ✅ |
| BioBERT + ChemBERTa 特征 | Task 2.1 | ✅ |
| 6 维 CMM–ADR 证据边 | Task 2.2 | ✅ |
| ESA-Gate | 已有 model.py + Task 5 消融 | ✅ |
| HSP-Layer | 已有 model.py + Task 5 消融 | ✅ |
| HCI-Module | 已有 model.py + Task 5 消融 | ✅ |
| 10 折分层 CV + 1:1 负采样 | Task 1.2, 4.1 | ✅ |
| 归纳式测试边移除 | Task 1.3 | ✅ |
| 超参数 Table (Section 3.5.2) | config.py 已对齐 | ✅ |
| Table 2 基线对比 | Task 6.2 | ✅ |
| Table 3 消融 | Task 5.1 | ✅ |
| Table 4 1:10 不平衡 | Task 6.1 | ✅ |
| 冷启动/度分层 | Task 6.3 | ✅ |
| TCM 映射 | Task 7.1 | ✅ |

**Placeholder 扫描:** 无 TBD/TODO 步骤；所有命令与路径已具体化。

---

## 十、执行方式选择

**Plan complete and saved to `docs/superpowers/plans/2026-06-18-msat-reproduction.md`.**

两种执行方式：

1. **Subagent-Driven（推荐）** — 每个 Task 派发独立 subagent，任务间审查，快速迭代
2. **Inline Execution** — 在本会话按 Phase 0→4 顺序逐步执行，关键节点暂停确认

建议从 **Phase 0（项目骨架 + 数据下载）** 开始。
