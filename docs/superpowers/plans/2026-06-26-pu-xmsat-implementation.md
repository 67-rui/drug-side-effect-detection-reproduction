# PU-XMSAT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在已复现 MSAT 主实验的基础上，实现可靠负样本选择、PU Learning 训练、机制子图解释和外部证据分级，形成一个可验证、可消融、可向导师汇报的 PU-XMSAT 改进闭环。

**Architecture:** 保留原始 MSAT 复现基线不变，把新研究作为独立实验层添加到 `MSAT/experiments/`、`MSAT/inference/`、`MSAT/scripts/` 和 `MSAT/tests/`。第一轮只做一周内最小闭环：可靠负样本、Weighted PU BCE、小规模训练 smoke test、少量解释案例和证据分级；完整多 seed 服务器训练在本地测试通过后再启动。

**Tech Stack:** Python 3.12, PyTorch, PyTorch Geometric, NumPy, pandas, scikit-learn, pytest, existing MSAT training/data/inference utilities.

---

## Branch And Baseline Contract

Current reproduction baseline is preserved before this plan:

```text
Baseline branch: codex/fix-reproduction-protocol
Baseline tag: baseline/msat-reproduction-20260626
Baseline commit: e2830f1
Development branch: codex/pu-xmsat-implementation
```

Development must happen on:

```bash
git switch codex/pu-xmsat-implementation
```

Do not rewrite or force-push the baseline tag. If a later experiment invalidates a claim, add a new report or a new tag; do not move `baseline/msat-reproduction-20260626`.

## Current Research Contract

The future direction is:

```text
基于不完整标签学习与机制解释的中药不良反应预测模型改进研究
```

The core scientific problem is:

```text
未观测 CMM-ADR pair 不等于真实负样本。
```

The first implementation must answer:

1. Can reliable negative sampling produce a cleaner negative set than random sampling?
2. Can Weighted PU BCE train stably without breaking the original MSAT protocol?
3. Does PU-XMSAT preserve the original Table 2 baseline level in small-scale smoke tests?
4. Can the model output at least a small number of interpretable CMM-compound-target-ADR paths?
5. Can high-confidence predictions be assigned evidence grades without treating LLM output as ground-truth labels?

## File Structure

Create or modify the following files.

| Path | Responsibility |
| --- | --- |
| `MSAT/results/PU_XMSAT_BASELINE_LOCK.md` | Human-readable frozen baseline, branch/tag, metrics, and allowed-change contract |
| `MSAT/scripts/verify_pu_xmsat_baseline.py` | Machine check that baseline artifacts exist and match expected protocol fields |
| `MSAT/experiments/pu_data_utils.py` | Shared positive-pair, unobserved-pair, graph support, and JSONL helpers |
| `MSAT/experiments/reliable_negative_sampling.py` | Candidate scoring and reliable negative selection |
| `MSAT/experiments/pu_dataset_builder.py` | Fold-level PU training pair construction and sample weights |
| `MSAT/experiments/pu_loss.py` | Weighted PU BCE and optional non-negative PU risk helpers |
| `MSAT/experiments/pu_training.py` | Weighted training/evaluation helpers that do not alter `train.py` default behavior |
| `MSAT/experiments/run_negative_sampling_ablation.py` | Strategy comparison without full model retraining where possible |
| `MSAT/experiments/run_pu_msat_experiment.py` | PU-XMSAT smoke/full experiment runner |
| `MSAT/inference/subgraph_explainer.py` | Mechanism subgraph and path-template extraction |
| `MSAT/inference/contribution_scoring.py` | Perturbation-based contribution scoring |
| `MSAT/scripts/run_explanation_case_study.py` | Top-K prediction explanation script |
| `MSAT/scripts/build_evidence_screening_table.py` | Evidence grading table from predictions, mechanisms, and literature/cache evidence |
| `MSAT/scripts/summarize_pu_xmsat_results.py` | Final summary report generator |
| `MSAT/tests/test_pu_data_utils.py` | Tests for pair utilities and support counts |
| `MSAT/tests/test_reliable_negative_sampling.py` | Tests for candidate scoring and deterministic selection |
| `MSAT/tests/test_pu_dataset_builder.py` | Tests for labels, weights, and fold construction |
| `MSAT/tests/test_pu_loss.py` | Tests for weighted loss and gradient behavior |
| `MSAT/tests/test_pu_training_contract.py` | Tests that PU training does not mutate default MSAT behavior |
| `MSAT/tests/test_subgraph_explainer.py` | Tests for path extraction |
| `MSAT/tests/test_contribution_scoring.py` | Tests for perturbation ranking |
| `MSAT/tests/test_evidence_screening_table.py` | Tests for evidence grading output |

Avoid modifying `MSAT/train.py` in the first implementation round. If training integration requires shared logic, add it to `MSAT/experiments/pu_training.py` and call existing public helpers from `train.py`.

## Task 1: Freeze The PU-XMSAT Baseline

**Files:**
- Create: `MSAT/results/PU_XMSAT_BASELINE_LOCK.md`
- Create: `MSAT/scripts/verify_pu_xmsat_baseline.py`
- Test: `MSAT/tests/test_verify_pu_xmsat_baseline.py`

- [ ] **Step 1: Write the baseline lock document**

Create `MSAT/results/PU_XMSAT_BASELINE_LOCK.md` with this content:

```markdown
# PU-XMSAT Baseline Lock

**Locked date:** 2026-06-26
**Baseline branch:** `codex/fix-reproduction-protocol`
**Baseline tag:** `baseline/msat-reproduction-20260626`
**Development branch:** `codex/pu-xmsat-implementation`

## Baseline Metrics

| File | Meaning | Key result |
| --- | --- | --- |
| `results/summary.json` | Table 2 MSAT 1:1 | AUC 0.9793, AUPRC 0.9771, F1 0.9315, MCC 0.8625 |
| `results/baseline_summary.json` | Table 2 baselines | MSAT AUC highest |
| `results/summary_neg10.json` | Table 4 MSAT 1:10 | AUC 0.8710, F1 0.5604, MCC 0.5180 |
| `results/faers_only_coldstart_summary.json` | Fig.5a | MSAT beats GAT/HGT/Simple-HGN on Precision, MCC, AUC |
| `results/table5_summary.json` | Table 5 candidate validation | Current support 1/15; not paper-equivalent reproduction |

## Allowed Changes

New PU-XMSAT work may add files under `experiments/`, `inference/`, `scripts/`, `tests/`, and `results/`.

The first implementation round must not change the default behavior of:

- `train.py`
- `model.py`
- `experiments/feature_extractor.py`
- existing result JSON files used as the baseline

## Reporting Rule

The original MSAT baseline remains the comparison anchor. PU-XMSAT results must be written to new files whose names begin with `pu_` or `PU_XMSAT_`.
```

- [ ] **Step 2: Write the failing baseline verification test**

Create `MSAT/tests/test_verify_pu_xmsat_baseline.py`:

```python
from pathlib import Path

from scripts.verify_pu_xmsat_baseline import verify_baseline


def test_verify_baseline_accepts_current_results():
    root = Path(__file__).resolve().parents[1]
    result = verify_baseline(root)
    assert result["ok"] is True
    assert result["summary_auc"] > 0.97
    assert result["table5_supported_count"] == 1
```

- [ ] **Step 3: Run the failing test**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_verify_pu_xmsat_baseline.py -q
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'scripts.verify_pu_xmsat_baseline'
```

- [ ] **Step 4: Implement the baseline verifier**

Create `MSAT/scripts/verify_pu_xmsat_baseline.py`:

```python
from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = [
    "results/summary.json",
    "results/baseline_summary.json",
    "results/summary_neg10.json",
    "results/faers_only_coldstart_summary.json",
    "results/table5_summary.json",
    "results/reproduction_state_audit.json",
    "results/TABLE5_PROTOCOL_DECISION.md",
    "results/PU_XMSAT_BASELINE_LOCK.md",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def verify_baseline(root: Path) -> dict:
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        return {"ok": False, "missing": missing}

    summary = _load_json(root / "results/summary.json")
    table5 = _load_json(root / "results/table5_summary.json")
    audit = _load_json(root / "results/reproduction_state_audit.json")

    protocol = summary.get("protocol", {})
    metrics = summary["overall_metrics"]

    checks = {
        "summary_auc": metrics["auc"]["mean"],
        "summary_auprc": metrics["auprc"]["mean"],
        "summary_f1": metrics["f1"]["mean"],
        "summary_mcc": metrics["mcc"]["mean"],
        "table5_supported_count": table5["supported_count"],
        "table5_support_rate": table5["support_rate"],
        "audit_issue_count": len(audit.get("issues", [])),
        "protocol_version": protocol.get("version"),
    }

    ok = (
        checks["summary_auc"] > 0.97
        and checks["summary_auprc"] > 0.97
        and checks["table5_supported_count"] == 1
        and checks["audit_issue_count"] == 0
        and protocol.get("validation_and_test_positive_edges_hidden") is True
    )
    return {"ok": ok, "missing": [], **checks}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    result = verify_baseline(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Verify the test passes**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_verify_pu_xmsat_baseline.py -q
/Users/a67_2024/opt/anaconda3/bin/python scripts/verify_pu_xmsat_baseline.py
```

Expected:

```text
1 passed
"ok": true
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/results/PU_XMSAT_BASELINE_LOCK.md MSAT/scripts/verify_pu_xmsat_baseline.py MSAT/tests/test_verify_pu_xmsat_baseline.py
git commit -m "test: lock PU-XMSAT baseline"
```

## Task 2: Add Pair And Graph Utility Layer

**Files:**
- Create: `MSAT/experiments/pu_data_utils.py`
- Test: `MSAT/tests/test_pu_data_utils.py`

- [ ] **Step 1: Write pair utility tests**

Create `MSAT/tests/test_pu_data_utils.py`:

```python
import torch
from torch_geometric.data import HeteroData

from experiments.pu_data_utils import (
    build_positive_pair_set,
    build_unobserved_pairs,
    count_mechanistic_support,
)


def toy_graph():
    data = HeteroData()
    data["herb"].x = torch.randn(3, 4)
    data["adr"].x = torch.randn(3, 4)
    data["target"].x = torch.randn(4, 4)
    data["compound"].x = torch.randn(2, 4)
    data["herb", "causes", "adr"].edge_index = torch.tensor([[0, 1], [1, 2]])
    data["herb", "causes", "adr"].edge_attr = torch.ones(2, 6)
    data["adr", "rev_causes", "herb"].edge_index = torch.tensor([[1, 2], [0, 1]])
    data["adr", "rev_causes", "herb"].edge_attr = torch.ones(2, 6)
    data["herb", "targets", "target"].edge_index = torch.tensor([[0, 2], [0, 3]])
    data["adr", "causes", "target"].edge_index = torch.tensor([[1, 2], [0, 3]])
    data["herb", "contains", "compound"].edge_index = torch.tensor([[0], [0]])
    data["target", "binds", "compound"].edge_index = torch.tensor([[2], [0]])
    return data


def test_positive_pair_set_uses_forward_cmm_adr_edges():
    pairs = build_positive_pair_set(toy_graph())
    assert pairs == {(0, 1), (1, 2)}


def test_unobserved_pairs_exclude_positives():
    pairs = build_unobserved_pairs(num_herbs=3, num_adrs=3, positive_pairs={(0, 1), (1, 2)})
    assert (0, 1) not in pairs
    assert (1, 2) not in pairs
    assert (2, 2) in pairs
    assert len(pairs) == 7


def test_mechanistic_support_counts_direct_and_compound_target_overlap():
    support = count_mechanistic_support(toy_graph(), herb_id=0, adr_id=1)
    assert support["direct_target_overlap"] == 1
    assert support["compound_target_overlap"] == 1
    assert support["total"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_data_utils.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.pu_data_utils'
```

- [ ] **Step 3: Implement `pu_data_utils.py`**

Create `MSAT/experiments/pu_data_utils.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import torch


Pair = tuple[int, int]


def build_positive_pair_set(data) -> set[Pair]:
    edge_index = data["herb", "causes", "adr"].edge_index
    return {
        (int(edge_index[0, i]), int(edge_index[1, i]))
        for i in range(edge_index.size(1))
    }


def build_unobserved_pairs(
    num_herbs: int,
    num_adrs: int,
    positive_pairs: set[Pair],
) -> list[Pair]:
    return [
        (herb_id, adr_id)
        for herb_id in range(num_herbs)
        for adr_id in range(num_adrs)
        if (herb_id, adr_id) not in positive_pairs
    ]


def _neighbors(data, edge_type: tuple[str, str, str], source_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[0] == int(source_id)
    return {int(v) for v in edge_index[1, mask].tolist()}


def _reverse_neighbors(data, edge_type: tuple[str, str, str], target_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[1] == int(target_id)
    return {int(v) for v in edge_index[0, mask].tolist()}


def herb_target_set(data, herb_id: int) -> set[int]:
    direct = _neighbors(data, ("herb", "targets", "target"), herb_id)
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)
    via_compound: set[int] = set()
    for compound_id in compounds:
        via_compound.update(
            _reverse_neighbors(data, ("target", "binds", "compound"), compound_id)
        )
    return direct | via_compound


def adr_target_set(data, adr_id: int) -> set[int]:
    return _neighbors(data, ("adr", "causes", "target"), adr_id)


def count_mechanistic_support(data, herb_id: int, adr_id: int) -> dict:
    direct_targets = _neighbors(data, ("herb", "targets", "target"), herb_id)
    adr_targets = adr_target_set(data, adr_id)
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)

    compound_targets: set[int] = set()
    for compound_id in compounds:
        compound_targets.update(
            _reverse_neighbors(data, ("target", "binds", "compound"), compound_id)
        )

    direct_overlap = direct_targets & adr_targets
    compound_overlap = compound_targets & adr_targets
    total = len(direct_overlap) + len(compound_overlap)
    return {
        "direct_target_overlap": len(direct_overlap),
        "compound_target_overlap": len(compound_overlap),
        "total": total,
    }


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open() as fh:
        return [json.loads(line) for line in fh if line.strip()]
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_data_utils.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_data_utils.py MSAT/tests/test_pu_data_utils.py
git commit -m "feat: add PU pair data utilities"
```

## Task 3: Implement Reliable Negative Sampling

**Files:**
- Create: `MSAT/experiments/reliable_negative_sampling.py`
- Test: `MSAT/tests/test_reliable_negative_sampling.py`

- [ ] **Step 1: Write reliable negative sampling tests**

Create `MSAT/tests/test_reliable_negative_sampling.py`:

```python
from experiments.reliable_negative_sampling import (
    CandidateScore,
    normalize_scores,
    score_reliable_negative_candidates,
    select_reliable_negatives,
)


def test_normalize_scores_handles_constant_values():
    assert normalize_scores([3.0, 3.0, 3.0]) == [0.0, 0.0, 0.0]


def test_reliable_negative_score_prefers_low_baseline_and_low_support():
    rows = score_reliable_negative_candidates(
        unobserved_pairs=[(0, 0), (0, 1), (1, 0)],
        baseline_scores={(0, 0): 0.90, (0, 1): 0.10, (1, 0): 0.20},
        structural_support={(0, 0): 5, (0, 1): 0, (1, 0): 1},
        similar_positive_support={(0, 0): 2, (0, 1): 0, (1, 0): 0},
        adr_frequency={0: 20, 1: 1},
    )
    best = max(rows, key=lambda row: row.reliability_score)
    assert best.herb_id == 0
    assert best.adr_id == 1
    assert "low_model_score" in best.reason_flags
    assert "low_structural_support" in best.reason_flags


def test_select_reliable_negatives_is_deterministic_for_ties():
    candidates = [
        CandidateScore(herb_id=2, adr_id=1, reliability_score=0.8),
        CandidateScore(herb_id=0, adr_id=1, reliability_score=0.8),
        CandidateScore(herb_id=1, adr_id=1, reliability_score=0.9),
    ]
    selected = select_reliable_negatives(candidates, count=2, seed=42)
    assert [(x.herb_id, x.adr_id) for x in selected] == [(1, 1), (0, 1)]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_reliable_negative_sampling.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.reliable_negative_sampling'
```

- [ ] **Step 3: Implement scoring**

Create `MSAT/experiments/reliable_negative_sampling.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field


Pair = tuple[int, int]


@dataclass(frozen=True)
class CandidateScore:
    herb_id: int
    adr_id: int
    reliability_score: float
    baseline_score: float | None = None
    structural_support: int | None = None
    similar_positive_support: int | None = None
    adr_frequency: int | None = None
    reason_flags: tuple[str, ...] = field(default_factory=tuple)


def normalize_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(value - lo) / (hi - lo) for value in values]


def score_reliable_negative_candidates(
    unobserved_pairs: list[Pair],
    baseline_scores: dict[Pair, float] | None = None,
    structural_support: dict[Pair, int] | None = None,
    similar_positive_support: dict[Pair, int] | None = None,
    adr_frequency: dict[int, int] | None = None,
) -> list[CandidateScore]:
    baseline_scores = baseline_scores or {}
    structural_support = structural_support or {}
    similar_positive_support = similar_positive_support or {}
    adr_frequency = adr_frequency or {}

    baseline_values = [baseline_scores.get(pair, 0.5) for pair in unobserved_pairs]
    structural_values = [float(structural_support.get(pair, 0)) for pair in unobserved_pairs]
    similar_values = [float(similar_positive_support.get(pair, 0)) for pair in unobserved_pairs]
    adr_freq_values = [float(adr_frequency.get(pair[1], 0)) for pair in unobserved_pairs]

    baseline_norm = normalize_scores(baseline_values)
    structural_norm = normalize_scores(structural_values)
    similar_norm = normalize_scores(similar_values)
    adr_freq_norm = normalize_scores(adr_freq_values)

    rows: list[CandidateScore] = []
    for idx, pair in enumerate(unobserved_pairs):
        low_model = 1.0 - baseline_norm[idx]
        low_structure = 1.0 - structural_norm[idx]
        low_similar_positive = 1.0 - similar_norm[idx]
        frequency_penalty = adr_freq_norm[idx]

        score = (
            0.45 * low_model
            + 0.30 * low_structure
            + 0.20 * low_similar_positive
            + 0.05 * frequency_penalty
        )

        flags: list[str] = []
        if low_model >= 0.70:
            flags.append("low_model_score")
        if low_structure >= 0.70:
            flags.append("low_structural_support")
        if low_similar_positive >= 0.70:
            flags.append("low_similar_positive_support")

        rows.append(
            CandidateScore(
                herb_id=pair[0],
                adr_id=pair[1],
                reliability_score=float(score),
                baseline_score=baseline_scores.get(pair),
                structural_support=structural_support.get(pair),
                similar_positive_support=similar_positive_support.get(pair),
                adr_frequency=adr_frequency.get(pair[1]),
                reason_flags=tuple(flags),
            )
        )
    return rows


def select_reliable_negatives(
    candidates: list[CandidateScore],
    count: int,
    seed: int,
) -> list[CandidateScore]:
    del seed
    ordered = sorted(
        candidates,
        key=lambda row: (-row.reliability_score, row.herb_id, row.adr_id),
    )
    return ordered[:count]
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_reliable_negative_sampling.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/reliable_negative_sampling.py MSAT/tests/test_reliable_negative_sampling.py
git commit -m "feat: add reliable negative sampling"
```

## Task 4: Build PU Dataset Constructor

**Files:**
- Create: `MSAT/experiments/pu_dataset_builder.py`
- Test: `MSAT/tests/test_pu_dataset_builder.py`

- [ ] **Step 1: Write PU dataset tests**

Create `MSAT/tests/test_pu_dataset_builder.py`:

```python
import numpy as np

from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.reliable_negative_sampling import CandidateScore


def test_build_pu_training_arrays_marks_positive_reliable_negative_and_unlabeled():
    arrays = build_pu_training_arrays(
        positive_pairs=[(0, 1), (1, 2)],
        reliable_negatives=[
            CandidateScore(herb_id=2, adr_id=2, reliability_score=0.9),
        ],
        unlabeled_pairs=[(0, 0), (2, 1)],
        unlabeled_weight=0.20,
        reliable_negative_weight=0.80,
    )
    assert arrays["herb_idx"].tolist() == [0, 1, 2, 0, 2]
    assert arrays["adr_idx"].tolist() == [1, 2, 2, 0, 1]
    assert arrays["label"].tolist() == [1, 1, 0, 0, 0]
    assert arrays["pair_type"].tolist() == ["positive", "positive", "reliable_negative", "unlabeled", "unlabeled"]
    np.testing.assert_allclose(arrays["sample_weight"], [1.0, 1.0, 0.8, 0.2, 0.2])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_dataset_builder.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.pu_dataset_builder'
```

- [ ] **Step 3: Implement PU arrays**

Create `MSAT/experiments/pu_dataset_builder.py`:

```python
from __future__ import annotations

from pathlib import Path

import numpy as np

from experiments.reliable_negative_sampling import CandidateScore


Pair = tuple[int, int]


def build_pu_training_arrays(
    positive_pairs: list[Pair],
    reliable_negatives: list[CandidateScore],
    unlabeled_pairs: list[Pair],
    unlabeled_weight: float = 0.20,
    reliable_negative_weight: float = 0.80,
) -> dict[str, np.ndarray]:
    herbs: list[int] = []
    adrs: list[int] = []
    labels: list[int] = []
    weights: list[float] = []
    pair_types: list[str] = []

    for herb_id, adr_id in positive_pairs:
        herbs.append(int(herb_id))
        adrs.append(int(adr_id))
        labels.append(1)
        weights.append(1.0)
        pair_types.append("positive")

    for row in reliable_negatives:
        herbs.append(int(row.herb_id))
        adrs.append(int(row.adr_id))
        labels.append(0)
        weights.append(float(reliable_negative_weight))
        pair_types.append("reliable_negative")

    for herb_id, adr_id in unlabeled_pairs:
        herbs.append(int(herb_id))
        adrs.append(int(adr_id))
        labels.append(0)
        weights.append(float(unlabeled_weight))
        pair_types.append("unlabeled")

    return {
        "herb_idx": np.asarray(herbs, dtype=np.int64),
        "adr_idx": np.asarray(adrs, dtype=np.int64),
        "label": np.asarray(labels, dtype=np.int64),
        "sample_weight": np.asarray(weights, dtype=np.float32),
        "pair_type": np.asarray(pair_types, dtype=object),
    }


def save_pu_arrays(path: str | Path, arrays: dict[str, np.ndarray]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **arrays)


def load_pu_arrays(path: str | Path) -> dict[str, np.ndarray]:
    loaded = np.load(Path(path), allow_pickle=True)
    return {key: loaded[key] for key in loaded.files}
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_dataset_builder.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_dataset_builder.py MSAT/tests/test_pu_dataset_builder.py
git commit -m "feat: add PU dataset builder"
```

## Task 5: Add Weighted PU Loss

**Files:**
- Create: `MSAT/experiments/pu_loss.py`
- Test: `MSAT/tests/test_pu_loss.py`

- [ ] **Step 1: Write loss tests**

Create `MSAT/tests/test_pu_loss.py`:

```python
import torch

from experiments.pu_loss import weighted_pu_bce_loss


def test_weighted_pu_bce_loss_backpropagates():
    logits = torch.tensor([2.0, -1.0, 0.5], requires_grad=True)
    labels = torch.tensor([1.0, 0.0, 0.0])
    weights = torch.tensor([1.0, 0.8, 0.2])
    loss = weighted_pu_bce_loss(logits, labels, weights)
    loss.backward()
    assert loss.item() > 0
    assert logits.grad is not None
    assert logits.grad.shape == logits.shape


def test_lower_unlabeled_weight_reduces_loss_contribution():
    logits = torch.tensor([2.0, 2.0])
    labels = torch.tensor([0.0, 0.0])
    high = weighted_pu_bce_loss(logits, labels, torch.tensor([1.0, 1.0]))
    low = weighted_pu_bce_loss(logits, labels, torch.tensor([0.1, 0.1]))
    assert low.item() < high.item()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_loss.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.pu_loss'
```

- [ ] **Step 3: Implement loss**

Create `MSAT/experiments/pu_loss.py`:

```python
from __future__ import annotations

import torch
import torch.nn.functional as F


def weighted_pu_bce_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
) -> torch.Tensor:
    per_sample = F.binary_cross_entropy_with_logits(
        logits,
        labels.float(),
        reduction="none",
    )
    weights = sample_weights.float().to(per_sample.device)
    return (per_sample * weights).sum() / weights.clamp_min(1e-8).sum()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_loss.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_loss.py MSAT/tests/test_pu_loss.py
git commit -m "feat: add weighted PU loss"
```

## Task 6: Add PU Training Helpers Without Changing Default MSAT

**Files:**
- Create: `MSAT/experiments/pu_training.py`
- Test: `MSAT/tests/test_pu_training_contract.py`

- [ ] **Step 1: Write training contract tests**

Create `MSAT/tests/test_pu_training_contract.py`:

```python
import inspect

import train
from experiments.pu_training import make_weighted_batch_tensors


def test_default_train_one_epoch_signature_is_unchanged():
    params = list(inspect.signature(train.train_one_epoch).parameters)
    assert params == ["model", "data", "optimizer", "train_edges", "train_labels", "device"]


def test_make_weighted_batch_tensors_shapes():
    batch = make_weighted_batch_tensors(
        herb_idx=[0, 1],
        adr_idx=[2, 3],
        labels=[1, 0],
        weights=[1.0, 0.2],
        device="cpu",
    )
    assert batch["edges"].shape == (2, 2)
    assert batch["labels"].tolist() == [1.0, 0.0]
    assert batch["weights"].tolist() == [1.0, 0.2]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_training_contract.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.pu_training'
```

- [ ] **Step 3: Implement PU training helper**

Create `MSAT/experiments/pu_training.py`:

```python
from __future__ import annotations

from collections.abc import Sequence

import torch

from experiments.pu_loss import weighted_pu_bce_loss


def make_weighted_batch_tensors(
    herb_idx: Sequence[int],
    adr_idx: Sequence[int],
    labels: Sequence[int],
    weights: Sequence[float],
    device,
) -> dict[str, torch.Tensor]:
    edges = torch.tensor([herb_idx, adr_idx], dtype=torch.long, device=device)
    return {
        "edges": edges,
        "labels": torch.tensor(labels, dtype=torch.float32, device=device),
        "weights": torch.tensor(weights, dtype=torch.float32, device=device),
    }


def train_one_epoch_weighted(
    model,
    data,
    optimizer,
    train_edges: torch.Tensor,
    train_labels: torch.Tensor,
    sample_weights: torch.Tensor,
    device,
) -> float:
    model.train()
    optimizer.zero_grad()
    logits = model(
        data.x_dict,
        data.edge_index_dict,
        data.edge_attr_dict,
        train_edges[0].to(device),
        train_edges[1].to(device),
    )
    loss = weighted_pu_bce_loss(
        logits,
        train_labels.float().to(device),
        sample_weights.float().to(device),
    )
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    return float(loss.item())
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_training_contract.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_training.py MSAT/tests/test_pu_training_contract.py
git commit -m "feat: add PU training helpers"
```

## Task 7: Add Candidate Score Cache Script

**Files:**
- Create: `MSAT/scripts/build_pu_candidate_cache.py`
- Test: `MSAT/tests/test_pu_candidate_cache.py`

- [ ] **Step 1: Write cache-row test**

Create `MSAT/tests/test_pu_candidate_cache.py`:

```python
from scripts.build_pu_candidate_cache import row_from_candidate
from experiments.reliable_negative_sampling import CandidateScore


def test_row_from_candidate_is_json_serializable():
    row = row_from_candidate(
        CandidateScore(
            herb_id=1,
            adr_id=2,
            reliability_score=0.75,
            baseline_score=0.10,
            structural_support=0,
            similar_positive_support=0,
            adr_frequency=3,
            reason_flags=("low_model_score",),
        )
    )
    assert row["herb_id"] == 1
    assert row["adr_id"] == 2
    assert row["reason_flags"] == ["low_model_score"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_candidate_cache.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'scripts.build_pu_candidate_cache'
```

- [ ] **Step 3: Implement cache script**

Create `MSAT/scripts/build_pu_candidate_cache.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from experiments.pu_data_utils import write_jsonl
from experiments.reliable_negative_sampling import CandidateScore


def row_from_candidate(candidate: CandidateScore) -> dict:
    return {
        "herb_id": candidate.herb_id,
        "adr_id": candidate.adr_id,
        "reliability_score": candidate.reliability_score,
        "baseline_score": candidate.baseline_score,
        "structural_support": candidate.structural_support,
        "similar_positive_support": candidate.similar_positive_support,
        "adr_frequency": candidate.adr_frequency,
        "reason_flags": list(candidate.reason_flags),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/pu_candidate_scores.jsonl")
    args = parser.parse_args()

    example = CandidateScore(herb_id=0, adr_id=0, reliability_score=0.0)
    write_jsonl(Path(args.output), [row_from_candidate(example)])
    print(f"Wrote example cache to {args.output}")


if __name__ == "__main__":
    main()
```

The first script version writes an example row only. Full graph scoring is added after Task 3 and Task 4 are passing, because reliable scoring depends on graph utilities and candidate construction.

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_candidate_cache.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Extend script to use actual graph**

Modify `MSAT/scripts/build_pu_candidate_cache.py` so `main()`:

1. Loads graph with `FeatureExtractor().load_graph()`.
2. Builds positive pairs with `build_positive_pair_set(data)`.
3. Builds all unobserved pairs with `build_unobserved_pairs`.
4. Computes `structural_support` using `count_mechanistic_support`.
5. Scores candidates using `score_reliable_negative_candidates`.
6. Writes JSONL rows.

Use this command:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/build_pu_candidate_cache.py \
  --output results/pu_candidate_scores.sample.jsonl
```

Expected:

```text
Wrote
```

and the output file contains JSON lines with `herb_id`, `adr_id`, and `reliability_score`.

- [ ] **Step 6: Commit**

```bash
git add MSAT/scripts/build_pu_candidate_cache.py MSAT/tests/test_pu_candidate_cache.py
git commit -m "feat: add PU candidate cache script"
```

## Task 8: Add Negative Sampling Ablation Runner

**Files:**
- Create: `MSAT/experiments/run_negative_sampling_ablation.py`
- Test: `MSAT/tests/test_negative_sampling_ablation.py`

- [ ] **Step 1: Write summary aggregation test**

Create `MSAT/tests/test_negative_sampling_ablation.py`:

```python
from experiments.run_negative_sampling_ablation import summarize_strategy_counts


def test_summarize_strategy_counts_counts_pair_types():
    rows = [
        {"strategy": "random", "pair_type": "negative"},
        {"strategy": "hybrid", "pair_type": "reliable_negative"},
        {"strategy": "hybrid", "pair_type": "reliable_negative"},
    ]
    summary = summarize_strategy_counts(rows)
    assert summary["random"]["negative"] == 1
    assert summary["hybrid"]["reliable_negative"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_negative_sampling_ablation.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.run_negative_sampling_ablation'
```

- [ ] **Step 3: Implement ablation summary helper and script skeleton**

Create `MSAT/experiments/run_negative_sampling_ablation.py`:

```python
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def summarize_strategy_counts(rows: list[dict]) -> dict:
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        out[row["strategy"]][row["pair_type"]] += 1
    return {strategy: dict(counts) for strategy, counts in out.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/pu_negative_sampling_summary.json")
    args = parser.parse_args()

    rows = [
        {"strategy": "random", "pair_type": "negative"},
        {"strategy": "hybrid", "pair_type": "reliable_negative"},
    ]
    payload = {
        "experiment": "negative_sampling_ablation",
        "summary": summarize_strategy_counts(rows),
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_negative_sampling_ablation.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Extend runner to use candidate cache**

Modify `main()` to read `results/pu_candidate_scores.jsonl` with `read_jsonl`, compare strategies `random`, `low_score`, and `hybrid`, and write:

```json
{
  "experiment": "negative_sampling_ablation",
  "strategies": ["random", "low_score", "hybrid"],
  "selection_counts": {},
  "output_files": {}
}
```

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python experiments/run_negative_sampling_ablation.py \
  --output results/pu_negative_sampling_summary.json
```

Expected:

```text
Wrote results/pu_negative_sampling_summary.json
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/experiments/run_negative_sampling_ablation.py MSAT/tests/test_negative_sampling_ablation.py
git commit -m "feat: add negative sampling ablation runner"
```

## Task 9: Add PU-XMSAT Smoke Experiment Runner

**Files:**
- Create: `MSAT/experiments/run_pu_msat_experiment.py`
- Test: `MSAT/tests/test_run_pu_msat_experiment.py`

- [ ] **Step 1: Write configuration parsing test**

Create `MSAT/tests/test_run_pu_msat_experiment.py`:

```python
from experiments.run_pu_msat_experiment import build_experiment_config


def test_build_experiment_config_records_protocol():
    cfg = build_experiment_config(
        sampling_strategy="hybrid",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        max_folds=1,
        max_epochs=2,
    )
    assert cfg["experiment"] == "pu_xmsat"
    assert cfg["sampling_strategy"] == "hybrid"
    assert cfg["loss"] == "weighted_pu_bce"
    assert cfg["max_folds"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'experiments.run_pu_msat_experiment'
```

- [ ] **Step 3: Implement config and smoke script**

Create `MSAT/experiments/run_pu_msat_experiment.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_experiment_config(
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    max_folds: int,
    max_epochs: int,
) -> dict:
    return {
        "experiment": "pu_xmsat",
        "sampling_strategy": sampling_strategy,
        "loss": "weighted_pu_bce",
        "unlabeled_weight": unlabeled_weight,
        "reliable_negative_weight": reliable_negative_weight,
        "max_folds": max_folds,
        "max_epochs": max_epochs,
        "baseline": "baseline/msat-reproduction-20260626",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampling-strategy", default="hybrid")
    parser.add_argument("--unlabeled-weight", type=float, default=0.2)
    parser.add_argument("--reliable-negative-weight", type=float, default=0.8)
    parser.add_argument("--max-folds", type=int, default=1)
    parser.add_argument("--max-epochs", type=int, default=2)
    parser.add_argument("--output", default="results/pu_training_smoke_summary.json")
    args = parser.parse_args()

    payload = build_experiment_config(
        sampling_strategy=args.sampling_strategy,
        unlabeled_weight=args.unlabeled_weight,
        reliable_negative_weight=args.reliable_negative_weight,
        max_folds=args.max_folds,
        max_epochs=args.max_epochs,
    )
    payload["status"] = "configured"

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Extend runner to train one fold**

Extend the runner to:

1. Load fold 0 with existing `FeatureExtractor`.
2. Hide validation/test positives using the same protocol as `train.py`.
3. Build a small PU dataset from fold positives, reliable negatives, and unlabeled pairs.
4. Train for `--max-epochs`.
5. Write `results/pu_training_smoke_summary.json` with metrics and runtime.

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --max-folds 1 \
  --max-epochs 2 \
  --output results/pu_training_smoke_summary.json
```

Expected:

```text
Wrote results/pu_training_smoke_summary.json
```

The JSON must include:

```json
{
  "experiment": "pu_xmsat",
  "status": "completed",
  "fold_results": [],
  "mean_metrics": {}
}
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/experiments/run_pu_msat_experiment.py MSAT/tests/test_run_pu_msat_experiment.py MSAT/results/pu_training_smoke_summary.json
git commit -m "feat: add PU-XMSAT smoke runner"
```

## Task 10: Add Mechanism Subgraph Explainer

**Files:**
- Create: `MSAT/inference/subgraph_explainer.py`
- Test: `MSAT/tests/test_subgraph_explainer.py`

- [ ] **Step 1: Write path extraction tests**

Create `MSAT/tests/test_subgraph_explainer.py`:

```python
import torch
from torch_geometric.data import HeteroData

from inference.subgraph_explainer import extract_path_templates


def toy_graph():
    data = HeteroData()
    data["herb"].x = torch.randn(1, 4)
    data["compound"].x = torch.randn(1, 4)
    data["target"].x = torch.randn(1, 4)
    data["adr"].x = torch.randn(1, 4)
    data["herb", "contains", "compound"].edge_index = torch.tensor([[0], [0]])
    data["target", "binds", "compound"].edge_index = torch.tensor([[0], [0]])
    data["adr", "causes", "target"].edge_index = torch.tensor([[0], [0]])
    return data


def test_extract_path_templates_finds_compound_target_adr_path():
    paths = extract_path_templates(toy_graph(), herb_id=0, adr_id=0)
    assert paths == [
        {
            "template": "herb-compound-target-adr",
            "herb_id": 0,
            "compound_id": 0,
            "target_id": 0,
            "adr_id": 0,
        }
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_subgraph_explainer.py -q
```

Expected:

```text
ImportError: cannot import name 'extract_path_templates'
```

- [ ] **Step 3: Implement path extraction**

Create `MSAT/inference/subgraph_explainer.py`:

```python
from __future__ import annotations


def _neighbors(data, edge_type: tuple[str, str, str], source_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[0] == int(source_id)
    return {int(v) for v in edge_index[1, mask].tolist()}


def _reverse_neighbors(data, edge_type: tuple[str, str, str], target_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[1] == int(target_id)
    return {int(v) for v in edge_index[0, mask].tolist()}


def extract_path_templates(data, herb_id: int, adr_id: int, max_paths: int = 20) -> list[dict]:
    paths: list[dict] = []
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)
    adr_targets = _neighbors(data, ("adr", "causes", "target"), adr_id)

    for compound_id in sorted(compounds):
        compound_targets = _reverse_neighbors(data, ("target", "binds", "compound"), compound_id)
        for target_id in sorted(compound_targets & adr_targets):
            paths.append(
                {
                    "template": "herb-compound-target-adr",
                    "herb_id": int(herb_id),
                    "compound_id": int(compound_id),
                    "target_id": int(target_id),
                    "adr_id": int(adr_id),
                }
            )
            if len(paths) >= max_paths:
                return paths

    direct_targets = _neighbors(data, ("herb", "targets", "target"), herb_id)
    for target_id in sorted(direct_targets & adr_targets):
        paths.append(
            {
                "template": "herb-target-adr",
                "herb_id": int(herb_id),
                "target_id": int(target_id),
                "adr_id": int(adr_id),
            }
        )
        if len(paths) >= max_paths:
            return paths
    return paths
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_subgraph_explainer.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/inference/subgraph_explainer.py MSAT/tests/test_subgraph_explainer.py
git commit -m "feat: add mechanism subgraph explainer"
```

## Task 11: Add Perturbation Contribution Scoring

**Files:**
- Create: `MSAT/inference/contribution_scoring.py`
- Test: `MSAT/tests/test_contribution_scoring.py`

- [ ] **Step 1: Write contribution scoring test**

Create `MSAT/tests/test_contribution_scoring.py`:

```python
from inference.contribution_scoring import rank_score_drops


def test_rank_score_drops_orders_largest_drop_first():
    ranked = rank_score_drops(
        original_score=0.9,
        masked_scores={"compound:1": 0.2, "target:2": 0.7},
    )
    assert ranked[0]["feature"] == "compound:1"
    assert ranked[0]["score_drop"] == 0.7
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_contribution_scoring.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'inference.contribution_scoring'
```

- [ ] **Step 3: Implement score-drop ranking**

Create `MSAT/inference/contribution_scoring.py`:

```python
from __future__ import annotations


def rank_score_drops(original_score: float, masked_scores: dict[str, float]) -> list[dict]:
    rows = [
        {
            "feature": feature,
            "masked_score": float(masked_score),
            "score_drop": round(float(original_score) - float(masked_score), 10),
        }
        for feature, masked_score in masked_scores.items()
    ]
    return sorted(rows, key=lambda row: (-row["score_drop"], row["feature"]))
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_contribution_scoring.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Add model perturbation helper**

Extend `MSAT/inference/contribution_scoring.py` with:

```python
import copy
import torch


def zero_node_features(data, node_type: str, node_ids: list[int]):
    copied = copy.deepcopy(data)
    if node_ids:
        copied[node_type].x[node_ids] = torch.zeros_like(copied[node_type].x[node_ids])
    return copied
```

Add a test that verifies the original graph is not mutated:

```python
def test_zero_node_features_does_not_mutate_original():
    import torch
    from torch_geometric.data import HeteroData
    from inference.contribution_scoring import zero_node_features

    data = HeteroData()
    data["compound"].x = torch.ones(2, 3)
    masked = zero_node_features(data, "compound", [1])
    assert data["compound"].x[1].sum().item() == 3
    assert masked["compound"].x[1].sum().item() == 0
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/inference/contribution_scoring.py MSAT/tests/test_contribution_scoring.py
git commit -m "feat: add perturbation contribution scoring"
```

## Task 12: Add Explanation Case Study Script

**Files:**
- Create: `MSAT/scripts/run_explanation_case_study.py`
- Test: `MSAT/tests/test_run_explanation_case_study.py`

- [ ] **Step 1: Write case row builder test**

Create `MSAT/tests/test_run_explanation_case_study.py`:

```python
from scripts.run_explanation_case_study import build_case_row


def test_build_case_row_contains_prediction_paths_and_contributions():
    row = build_case_row(
        herb_id=277,
        adr_id=2931,
        score=0.68,
        paths=[{"template": "herb-compound-target-adr"}],
        contributions=[{"feature": "compound:72344", "score_drop": 0.2}],
    )
    assert row["herb_id"] == 277
    assert row["adr_id"] == 2931
    assert row["prediction_score"] == 0.68
    assert row["path_count"] == 1
    assert row["contribution_count"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_explanation_case_study.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'scripts.run_explanation_case_study'
```

- [ ] **Step 3: Implement script**

Create `MSAT/scripts/run_explanation_case_study.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_case_row(
    herb_id: int,
    adr_id: int,
    score: float,
    paths: list[dict],
    contributions: list[dict],
) -> dict:
    return {
        "herb_id": int(herb_id),
        "adr_id": int(adr_id),
        "prediction_score": float(score),
        "paths": paths,
        "path_count": len(paths),
        "contributions": contributions,
        "contribution_count": len(contributions),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/explanation_case_studies.json")
    args = parser.parse_args()

    rows = [
        build_case_row(
            herb_id=277,
            adr_id=2931,
            score=0.6849409937858582,
            paths=[],
            contributions=[],
        )
    ]
    payload = {"experiment": "explanation_case_study", "rows": rows}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_explanation_case_study.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Extend script to load current predictions**

Extend the script so it can read:

```text
results/table5_top15.csv
results/case_zhishi_diarrhoea.json
```

and write at least 5 rows to:

```text
results/explanation_case_studies.json
```

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/run_explanation_case_study.py \
  --output results/explanation_case_studies.json
```

Expected:

```text
Wrote results/explanation_case_studies.json
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/scripts/run_explanation_case_study.py MSAT/tests/test_run_explanation_case_study.py MSAT/results/explanation_case_studies.json
git commit -m "feat: add explanation case study workflow"
```

## Task 13: Add Evidence Screening Table

**Files:**
- Create: `MSAT/scripts/build_evidence_screening_table.py`
- Test: `MSAT/tests/test_evidence_screening_table.py`

- [ ] **Step 1: Write evidence grading tests**

Create `MSAT/tests/test_evidence_screening_table.py`:

```python
from scripts.build_evidence_screening_table import assign_evidence_grade


def test_direct_database_support_gets_grade_a():
    grade = assign_evidence_grade(
        database_verified=True,
        direct_literature_support=False,
        mechanistic_support=False,
    )
    assert grade == "A"


def test_mechanistic_support_without_direct_evidence_gets_grade_c():
    grade = assign_evidence_grade(
        database_verified=False,
        direct_literature_support=False,
        mechanistic_support=True,
    )
    assert grade == "C"


def test_no_support_gets_grade_d():
    grade = assign_evidence_grade(
        database_verified=False,
        direct_literature_support=False,
        mechanistic_support=False,
    )
    assert grade == "D"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_evidence_screening_table.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'scripts.build_evidence_screening_table'
```

- [ ] **Step 3: Implement evidence grading**

Create `MSAT/scripts/build_evidence_screening_table.py`:

```python
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def assign_evidence_grade(
    database_verified: bool,
    direct_literature_support: bool,
    mechanistic_support: bool,
) -> str:
    if database_verified:
        return "A"
    if direct_literature_support:
        return "B"
    if mechanistic_support:
        return "C"
    return "D"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table5", default="results/table5_summary.json")
    parser.add_argument("--output-json", default="results/evidence_screening_summary.json")
    parser.add_argument("--output-csv", default="results/evidence_screening_table.csv")
    args = parser.parse_args()

    table5 = json.loads(Path(args.table5).read_text())
    rows = []
    for row in table5.get("rows", []):
        grade = assign_evidence_grade(
            database_verified=bool(row.get("database_verified")),
            direct_literature_support=bool(row.get("direct_literature_support")),
            mechanistic_support=bool(row.get("mechanistic_support")),
        )
        rows.append({**row, "evidence_grade": grade})

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"experiment": "evidence_screening", "rows": rows}, ensure_ascii=False, indent=2)
    )
    if rows:
        with out_csv.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {out_json} and {out_csv}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_evidence_screening_table.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Generate evidence table**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/build_evidence_screening_table.py \
  --table5 results/table5_summary.json \
  --output-json results/evidence_screening_summary.json \
  --output-csv results/evidence_screening_table.csv
```

Expected:

```text
Wrote results/evidence_screening_summary.json and results/evidence_screening_table.csv
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/scripts/build_evidence_screening_table.py MSAT/tests/test_evidence_screening_table.py MSAT/results/evidence_screening_summary.json MSAT/results/evidence_screening_table.csv
git commit -m "feat: add evidence screening table"
```

## Task 14: Add PU-XMSAT Result Summarizer

**Files:**
- Create: `MSAT/scripts/summarize_pu_xmsat_results.py`
- Test: `MSAT/tests/test_summarize_pu_xmsat_results.py`
- Output: `MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md`

- [ ] **Step 1: Write Markdown section test**

Create `MSAT/tests/test_summarize_pu_xmsat_results.py`:

```python
from scripts.summarize_pu_xmsat_results import markdown_metric_row


def test_markdown_metric_row_formats_four_decimals():
    row = markdown_metric_row("MSAT", {"auc": 0.979271, "auprc": 0.977094})
    assert row == "| MSAT | 0.9793 | 0.9771 |"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_summarize_pu_xmsat_results.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'scripts.summarize_pu_xmsat_results'
```

- [ ] **Step 3: Implement summarizer**

Create `MSAT/scripts/summarize_pu_xmsat_results.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def markdown_metric_row(name: str, metrics: dict) -> str:
    return f"| {name} | {metrics['auc']:.4f} | {metrics['auprc']:.4f} |"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/summary.json")
    parser.add_argument("--pu", default="results/pu_training_smoke_summary.json")
    parser.add_argument("--evidence", default="results/evidence_screening_summary.json")
    parser.add_argument("--output", default="results/PU_XMSAT_EXPERIMENT_REPORT.md")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    baseline_metrics = {
        "auc": baseline["overall_metrics"]["auc"]["mean"],
        "auprc": baseline["overall_metrics"]["auprc"]["mean"],
    }

    lines = [
        "# PU-XMSAT Experiment Report",
        "",
        "## Baseline",
        "",
        "| Model | AUC | AUPRC |",
        "| --- | ---: | ---: |",
        markdown_metric_row("MSAT", baseline_metrics),
        "",
        "## Current PU-XMSAT Status",
        "",
        "The first implementation round should be interpreted as a smoke-tested research prototype until full multi-seed training is complete.",
    ]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_summarize_pu_xmsat_results.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Generate report**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/summarize_pu_xmsat_results.py \
  --output results/PU_XMSAT_EXPERIMENT_REPORT.md
```

Expected:

```text
Wrote results/PU_XMSAT_EXPERIMENT_REPORT.md
```

- [ ] **Step 6: Commit**

```bash
git add MSAT/scripts/summarize_pu_xmsat_results.py MSAT/tests/test_summarize_pu_xmsat_results.py MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md
git commit -m "feat: add PU-XMSAT report summarizer"
```

## Task 15: Run One-Week Minimum Validation

**Files:**
- Read: `MSAT/results/summary.json`
- Read: `MSAT/results/table5_summary.json`
- Generate: `MSAT/results/pu_candidate_scores.sample.jsonl`
- Generate: `MSAT/results/pu_negative_sampling_summary.json`
- Generate: `MSAT/results/pu_training_smoke_summary.json`
- Generate: `MSAT/results/explanation_case_studies.json`
- Generate: `MSAT/results/evidence_screening_summary.json`
- Generate: `MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md`

- [ ] **Step 1: Run focused tests**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest \
  tests/test_verify_pu_xmsat_baseline.py \
  tests/test_pu_data_utils.py \
  tests/test_reliable_negative_sampling.py \
  tests/test_pu_dataset_builder.py \
  tests/test_pu_loss.py \
  tests/test_pu_training_contract.py \
  tests/test_subgraph_explainer.py \
  tests/test_contribution_scoring.py \
  tests/test_evidence_screening_table.py \
  -q
```

Expected:

```text
passed
```

- [ ] **Step 2: Run baseline audit**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/audit_reproduction_state.py \
  --out results/reproduction_state_audit.json \
  --fail-on-error
```

Expected:

```text
"issues": []
```

- [ ] **Step 3: Run PU smoke workflow**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python scripts/build_pu_candidate_cache.py \
  --output results/pu_candidate_scores.sample.jsonl

/Users/a67_2024/opt/anaconda3/bin/python experiments/run_negative_sampling_ablation.py \
  --output results/pu_negative_sampling_summary.json

/Users/a67_2024/opt/anaconda3/bin/python experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --max-folds 1 \
  --max-epochs 2 \
  --output results/pu_training_smoke_summary.json

/Users/a67_2024/opt/anaconda3/bin/python scripts/run_explanation_case_study.py \
  --output results/explanation_case_studies.json

/Users/a67_2024/opt/anaconda3/bin/python scripts/build_evidence_screening_table.py \
  --output-json results/evidence_screening_summary.json \
  --output-csv results/evidence_screening_table.csv

/Users/a67_2024/opt/anaconda3/bin/python scripts/summarize_pu_xmsat_results.py \
  --output results/PU_XMSAT_EXPERIMENT_REPORT.md
```

Expected:

```text
Wrote results/PU_XMSAT_EXPERIMENT_REPORT.md
```

- [ ] **Step 4: Commit smoke artifacts**

```bash
git add MSAT/results/pu_candidate_scores.sample.jsonl MSAT/results/pu_negative_sampling_summary.json MSAT/results/pu_training_smoke_summary.json MSAT/results/explanation_case_studies.json MSAT/results/evidence_screening_summary.json MSAT/results/evidence_screening_table.csv MSAT/results/PU_XMSAT_EXPERIMENT_REPORT.md
git commit -m "results: add PU-XMSAT smoke validation artifacts"
```

## Task 16: Server Full Run Gate

Do not start long server training until Task 15 passes locally.

**Files:**
- Create: `MSAT/scripts/server_pu_xmsat_run.sh`
- Create: `MSAT/scripts/server_pu_xmsat_monitor.sh`
- Test: `MSAT/tests/test_server_pu_xmsat_scripts.py`

- [ ] **Step 1: Write server script contract test**

Create `MSAT/tests/test_server_pu_xmsat_scripts.py`:

```python
from pathlib import Path


def test_server_pu_xmsat_run_uses_safe_outputs():
    text = Path("scripts/server_pu_xmsat_run.sh").read_text()
    assert "pu_training_summary.json" in text
    assert "summary.json" not in text.split("pu_training_summary.json")[0]
    assert "set -euo pipefail" in text
```

- [ ] **Step 2: Create server run script**

Create `MSAT/scripts/server_pu_xmsat_run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PY="${PY:-python}"
mkdir -p results/phase_pu_xmsat_logs

"$PY" scripts/verify_pu_xmsat_baseline.py

"$PY" experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --unlabeled-weight 0.2 \
  --reliable-negative-weight 0.8 \
  --max-folds 10 \
  --max-epochs 1000 \
  --output results/pu_training_summary.json \
  2>&1 | tee results/phase_pu_xmsat_logs/pu_training.log

"$PY" scripts/run_explanation_case_study.py \
  --output results/explanation_case_studies.json

"$PY" scripts/build_evidence_screening_table.py \
  --output-json results/evidence_screening_summary.json \
  --output-csv results/evidence_screening_table.csv

"$PY" scripts/summarize_pu_xmsat_results.py \
  --output results/PU_XMSAT_EXPERIMENT_REPORT.md
```

- [ ] **Step 3: Create monitor script**

Create `MSAT/scripts/server_pu_xmsat_monitor.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
tail -n 80 results/phase_pu_xmsat_logs/pu_training.log
```

- [ ] **Step 4: Verify script contract**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
chmod +x scripts/server_pu_xmsat_run.sh scripts/server_pu_xmsat_monitor.sh
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_server_pu_xmsat_scripts.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add MSAT/scripts/server_pu_xmsat_run.sh MSAT/scripts/server_pu_xmsat_monitor.sh MSAT/tests/test_server_pu_xmsat_scripts.py
git commit -m "chore: add PU-XMSAT server run scripts"
```

## Task 17: Final Verification Before Any Claim

Run from repository root:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q
/Users/a67_2024/opt/anaconda3/bin/python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error
/Users/a67_2024/opt/anaconda3/bin/python scripts/verify_pu_xmsat_baseline.py
```

Expected:

```text
all tests pass
"issues": []
"ok": true
```

Then run:

```bash
cd /Users/a67_2024/Desktop/drug-detect
git status --short
git log --oneline --decorate -5
```

Expected:

```text
working tree clean except intentional generated artifacts
HEAD on codex/pu-xmsat-implementation
```

If all verification passes:

```bash
git push origin codex/pu-xmsat-implementation
```

## Commit Cadence

Use small commits:

```text
test: lock PU-XMSAT baseline
feat: add PU pair data utilities
feat: add reliable negative sampling
feat: add PU dataset builder
feat: add weighted PU loss
feat: add PU training helpers
feat: add negative sampling ablation runner
feat: add PU-XMSAT smoke runner
feat: add mechanism subgraph explainer
feat: add perturbation contribution scoring
feat: add explanation case study workflow
feat: add evidence screening table
feat: add PU-XMSAT report summarizer
results: add PU-XMSAT smoke validation artifacts
chore: add PU-XMSAT server run scripts
```

## Decision Points Requiring User Confirmation

Ask the user before proceeding when any of these happen:

1. A change requires modifying default `MSAT/train.py` behavior.
2. A new dependency is needed beyond PyTorch/PyG/NumPy/pandas/scikit-learn/pytest.
3. Full server training is about to start.
4. Any result suggests original Table 2 baseline has regressed.
5. Evidence grading would require an external paid API, login credential, or LLM API key.
6. The implementation would overwrite existing `summary.json`, `table5_summary.json`, or other baseline result files.

## Success Criteria

The first implementation round is successful when:

1. Baseline remains locked and auditable.
2. Reliable negative candidates can be generated reproducibly.
3. PU training smoke test completes without changing original MSAT outputs.
4. Explanation script outputs at least five case rows with path or contribution fields.
5. Evidence screening table assigns A/B/C/D grades and keeps model prediction separate from evidence.
6. `PU_XMSAT_EXPERIMENT_REPORT.md` states whether PU-XMSAT is ready for full training.
7. The development branch is pushed as `codex/pu-xmsat-implementation`.
