# PU-XMSAT Full MSAT Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded `full_msat_pu` backend that trains the real `MSATTCMFSFinal` model with PU sample weights without changing the default MSAT reproduction path.

**Architecture:** Keep `weighted_embedding_smoke` as the default fast backend and add full GNN training behind an explicit `--backend full_msat_pu` switch. Put full-backend helpers in a new focused module, reuse stable protocol helpers from `train.py`, and write only PU-prefixed or PU-specific outputs.

**Tech Stack:** Python 3.12, PyTorch, PyTorch Geometric, NumPy, scikit-learn metrics through existing `train.py`, pytest.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `MSAT/experiments/pu_loss.py` | Keep logits-based smoke loss and add probability-safe weighted BCE for `MSATTCMFSFinal` outputs. |
| `MSAT/experiments/pu_training.py` | Keep batch tensor helper and add a probability-output weighted train step. |
| `MSAT/experiments/full_msat_pu_training.py` | New full GNN PU backend: fold split, graph edge hiding, model setup, weighted training, evaluation, summary. |
| `MSAT/experiments/run_pu_msat_experiment.py` | Add `--backend` dispatch and full-backend output aggregation. |
| `MSAT/scripts/server_pu_xmsat_run.sh` | Add safe env-configurable full-backend pilot defaults. |
| `MSAT/scripts/summarize_pu_xmsat_results.py` | Report backend and full metrics when `pu_training_summary.json` exists. |
| `MSAT/scripts/verify_pu_xmsat_final.py` | Keep smoke artifact checks and optionally surface full-backend summary. |
| `MSAT/tests/test_pu_loss.py` | Tests for probability-safe weighted BCE. |
| `MSAT/tests/test_pu_training_contract.py` | Tests for probability-output weighted train step and unchanged default train signature. |
| `MSAT/tests/test_run_pu_msat_experiment.py` | Tests for backend config and dispatch behavior. |
| `MSAT/tests/test_server_pu_xmsat_scripts.py` | Tests for safe server pilot defaults. |
| `MSAT/tests/test_summarize_pu_xmsat_results.py` | Tests for report wording with full backend metrics. |

## Task 1: Add Probability-Safe PU Loss

**Files:**
- Modify: `MSAT/experiments/pu_loss.py`
- Modify: `MSAT/tests/test_pu_loss.py`

- [ ] **Step 1: Write failing probability-loss tests**

Add to `MSAT/tests/test_pu_loss.py`:

```python
def test_weighted_pu_probability_bce_loss_matches_manual_bce():
    probs = torch.tensor([0.8, 0.25, 0.6], requires_grad=True)
    labels = torch.tensor([1.0, 0.0, 0.0])
    weights = torch.tensor([1.0, 0.8, 0.2])

    loss = weighted_pu_probability_bce_loss(probs, labels, weights)
    expected = -(
        torch.log(torch.tensor(0.8)) * 1.0
        + torch.log(torch.tensor(0.75)) * 0.8
        + torch.log(torch.tensor(0.4)) * 0.2
    ) / 3

    assert torch.allclose(loss, expected, atol=1e-6)
    loss.backward()
    assert probs.grad is not None


def test_weighted_pu_probability_bce_loss_clamps_extreme_probs():
    probs = torch.tensor([0.0, 1.0], requires_grad=True)
    labels = torch.tensor([0.0, 1.0])
    weights = torch.tensor([1.0, 1.0])

    loss = weighted_pu_probability_bce_loss(probs, labels, weights)
    loss.backward()

    assert torch.isfinite(loss)
    assert probs.grad is not None
```

- [ ] **Step 2: Run tests and verify RED**

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_loss.py -q
```

Expected: import/name failure for `weighted_pu_probability_bce_loss`.

- [ ] **Step 3: Implement probability loss**

Add to `MSAT/experiments/pu_loss.py`:

```python
def weighted_pu_probability_bce_loss(
    probabilities: torch.Tensor,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
    eps: float = 1e-7,
) -> torch.Tensor:
    probs = probabilities.float().clamp(min=eps, max=1.0 - eps)
    labels = labels.float().to(probs.device)
    weights = sample_weights.float().to(probs.device)
    per_sample = -(labels * torch.log(probs) + (1.0 - labels) * torch.log(1.0 - probs))
    return (per_sample * weights).mean()
```

- [ ] **Step 4: Verify GREEN**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_loss.py -q
```

Expected: all tests in `test_pu_loss.py` pass.

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_loss.py MSAT/tests/test_pu_loss.py
git commit -m "feat: add probability-safe PU loss"
```

## Task 2: Add Probability-Output Weighted Train Step

**Files:**
- Modify: `MSAT/experiments/pu_training.py`
- Modify: `MSAT/tests/test_pu_training_contract.py`

- [ ] **Step 1: Write failing train-step test**

Add to `MSAT/tests/test_pu_training_contract.py`:

```python
import torch

from experiments.pu_training import train_one_epoch_weighted_probabilities


class ProbabilityToyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.logit = torch.nn.Parameter(torch.tensor([0.0, 0.0]))

    def forward(self, x_dict, edge_index_dict, edge_attr_dict, herb_indices, adr_indices):
        del x_dict, edge_index_dict, edge_attr_dict, herb_indices, adr_indices
        return torch.sigmoid(self.logit)


class ToyData:
    x_dict = {}
    edge_index_dict = {}
    edge_attr_dict = {}


def test_train_one_epoch_weighted_probabilities_updates_probability_model():
    model = ProbabilityToyModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    edges = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
    labels = torch.tensor([1.0, 0.0])
    weights = torch.tensor([1.0, 0.2])

    before = model.logit.detach().clone()
    loss = train_one_epoch_weighted_probabilities(
        model, ToyData(), optimizer, edges, labels, weights, "cpu"
    )

    assert loss > 0
    assert not torch.equal(before, model.logit.detach())
```

- [ ] **Step 2: Run test and verify RED**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_training_contract.py -q
```

Expected: import/name failure for `train_one_epoch_weighted_probabilities`.

- [ ] **Step 3: Implement train step**

Add to `MSAT/experiments/pu_training.py`:

```python
from experiments.pu_loss import weighted_pu_probability_bce_loss


def train_one_epoch_weighted_probabilities(
    model,
    data,
    optimizer,
    train_edges: torch.Tensor,
    train_labels: torch.Tensor,
    sample_weights: torch.Tensor,
    device,
    gradient_clip: float = 1.0,
) -> float:
    model.train()
    optimizer.zero_grad()
    probabilities = model(
        data.x_dict,
        data.edge_index_dict,
        data.edge_attr_dict,
        train_edges[0].to(device),
        train_edges[1].to(device),
    )
    loss = weighted_pu_probability_bce_loss(
        probabilities,
        train_labels.float().to(device),
        sample_weights.float().to(device),
    )
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=gradient_clip)
    optimizer.step()
    return float(loss.item())
```

- [ ] **Step 4: Verify GREEN**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_training_contract.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/pu_training.py MSAT/tests/test_pu_training_contract.py
git commit -m "feat: add weighted probability training step"
```

## Task 3: Add Full MSAT PU Backend Module

**Files:**
- Create: `MSAT/experiments/full_msat_pu_training.py`
- Modify: `MSAT/tests/test_run_pu_msat_experiment.py`

- [ ] **Step 1: Write failing module tests**

Add imports and tests to `MSAT/tests/test_run_pu_msat_experiment.py`:

```python
from experiments.full_msat_pu_training import FullMSATPUConfig, summarize_full_fold_results


def test_full_msat_pu_config_uses_pu_checkpoint_names():
    cfg = FullMSATPUConfig(max_epochs=1, max_pairs=96)
    assert cfg.training_backend == "full_msat_pu"
    assert cfg.checkpoint_prefix == "pu_xmsat"


def test_summarize_full_fold_results_reports_metric_means():
    payload = summarize_full_fold_results(
        [
            {
                "fold": 0,
                "test_metrics": {"auc": 0.7, "auprc": 0.6, "f1": 0.5, "mcc": 0.4},
                "training_history": {"train_loss": [0.9, 0.8]},
            },
            {
                "fold": 1,
                "test_metrics": {"auc": 0.9, "auprc": 0.8, "f1": 0.7, "mcc": 0.6},
                "training_history": {"train_loss": [0.7, 0.6]},
            },
        ]
    )
    assert payload["auc"] == 0.8
    assert payload["auprc"] == 0.7
    assert payload["final_loss"] == 0.7
```

- [ ] **Step 2: Run test and verify RED**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected: module import failure for `experiments.full_msat_pu_training`.

- [ ] **Step 3: Implement module skeleton and summary helper**

Create `MSAT/experiments/full_msat_pu_training.py` with `FullMSATPUConfig`, `summarize_full_fold_results`, and fold-running helper signatures.

- [ ] **Step 4: Verify GREEN for summary tests**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/full_msat_pu_training.py MSAT/tests/test_run_pu_msat_experiment.py
git commit -m "feat: add full MSAT PU training scaffold"
```

## Task 4: Wire Backend Dispatch Into Runner

**Files:**
- Modify: `MSAT/experiments/run_pu_msat_experiment.py`
- Modify: `MSAT/tests/test_run_pu_msat_experiment.py`

- [ ] **Step 1: Write failing backend dispatch tests**

Add to `MSAT/tests/test_run_pu_msat_experiment.py`:

```python
from experiments.run_pu_msat_experiment import resolve_training_backend


def test_build_experiment_config_records_full_backend():
    cfg = build_experiment_config(
        sampling_strategy="hybrid",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        max_folds=1,
        max_epochs=1,
        training_backend="full_msat_pu",
    )
    assert cfg["training_backend"] == "full_msat_pu"


def test_resolve_training_backend_rejects_unknown_backend():
    try:
        resolve_training_backend("unknown")
    except ValueError as exc:
        assert "unknown backend" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
```

- [ ] **Step 2: Run test and verify RED**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected: signature/name failures.

- [ ] **Step 3: Implement backend argument and dispatch**

Update `build_experiment_config()` to accept `training_backend`. Add `--backend` parser argument. Dispatch `weighted_embedding_smoke` to the existing path and `full_msat_pu` to the new full training module.

- [ ] **Step 4: Verify GREEN**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_run_pu_msat_experiment.py -q
```

Expected: runner tests pass.

- [ ] **Step 5: Commit**

```bash
git add MSAT/experiments/run_pu_msat_experiment.py MSAT/tests/test_run_pu_msat_experiment.py
git commit -m "feat: add PU-XMSAT backend dispatch"
```

## Task 5: Implement Full Fold Training

**Files:**
- Modify: `MSAT/experiments/full_msat_pu_training.py`
- Modify: `MSAT/experiments/run_pu_msat_experiment.py`

- [ ] **Step 1: Implement full fold runner behind existing tested interface**

Implement this public function in `MSAT/experiments/full_msat_pu_training.py`:

```python
def run_full_msat_pu_experiment(
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    max_folds: int,
    max_epochs: int,
    max_pairs: int,
    candidate_cache: str | Path,
    seed: int,
) -> dict:
    """Run bounded PU-weighted MSAT GNN training and return JSON-safe summary."""
```

The function must perform these concrete actions for every fold in `range(max(1, max_folds))`:

1. Load graph and fold data with `FeatureExtractor`.
2. Split development samples into train/validation with `TrainingConfig.RANDOM_STATE + fold_idx`.
3. Build PU train arrays from train positives, reliable negatives, and unlabeled pairs.
4. Hide validation/test positive CMM-ADR edges with the same helpers used by `train.py`.
5. Initialize `MSATTCMFSFinal` with existing `ModelConfig`.
6. Train for `max_epochs` using `train_one_epoch_weighted_probabilities`.
7. Track `train_loss` and validation AUC.
8. Restore the best validation-AUC state before test evaluation.
9. Evaluate official test pairs with `train.evaluate`.
10. Return a summary with `training_backend: "full_msat_pu"`, `fold_results`, `mean_metrics`, `runtime_seconds`, and `note`.

- [ ] **Step 2: Run targeted tests**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_pu_loss.py tests/test_pu_training_contract.py tests/test_run_pu_msat_experiment.py -q
```

Expected: all targeted tests pass.

- [ ] **Step 3: Run smoke backend CLI to protect existing behavior**

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python experiments/run_pu_msat_experiment.py \
  --backend weighted_embedding_smoke \
  --max-folds 1 \
  --max-epochs 2 \
  --output /tmp/pu_xmsat_smoke_backend_check.json
```

Expected: command exits 0 and writes `/tmp/pu_xmsat_smoke_backend_check.json`.

- [ ] **Step 4: Commit**

```bash
git add MSAT/experiments/full_msat_pu_training.py MSAT/experiments/run_pu_msat_experiment.py
git commit -m "feat: train PU-XMSAT with full MSAT backend"
```

## Task 6: Update Server Script, Report, And Verifier

**Files:**
- Modify: `MSAT/scripts/server_pu_xmsat_run.sh`
- Modify: `MSAT/scripts/summarize_pu_xmsat_results.py`
- Modify: `MSAT/scripts/verify_pu_xmsat_final.py`
- Modify: `MSAT/tests/test_server_pu_xmsat_scripts.py`
- Create or modify: `MSAT/tests/test_summarize_pu_xmsat_results.py`

- [ ] **Step 1: Write failing script/report tests**

Update script tests to assert:

```python
def test_server_pu_xmsat_run_defaults_to_bounded_full_backend():
    text = Path("scripts/server_pu_xmsat_run.sh").read_text()
    assert "PU_XMSAT_BACKEND:-full_msat_pu" in text
    assert "PU_XMSAT_MAX_FOLDS:-1" in text
    assert "PU_XMSAT_MAX_EPOCHS:-5" in text
    assert "--backend" in text
```

Add report test:

```python
from scripts.summarize_pu_xmsat_results import build_report


def test_report_includes_full_backend_metrics_when_available():
    baseline = {"overall_metrics": {"auc": {"mean": 0.97}, "auprc": {"mean": 0.96}}}
    pu = {
        "status": "completed",
        "training_executed": True,
        "training_backend": "full_msat_pu",
        "mean_metrics": {"auc": 0.71, "auprc": 0.62, "f1": 0.55, "mcc": 0.40},
    }
    report = build_report(baseline, pu, {"rows": []})
    assert "Backend: full_msat_pu" in report
    assert "PU-XMSAT | 0.7100 | 0.6200" in report
```

- [ ] **Step 2: Run tests and verify RED**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_server_pu_xmsat_scripts.py tests/test_summarize_pu_xmsat_results.py -q
```

Expected: assertions fail.

- [ ] **Step 3: Implement script/report/verifier updates**

Update server script with bounded env defaults. Update report to include backend and metrics when present. Update verifier to keep smoke checks and optionally include `pu_training_summary.json` backend/metrics.

- [ ] **Step 4: Verify GREEN**

```bash
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_server_pu_xmsat_scripts.py tests/test_summarize_pu_xmsat_results.py -q
```

Expected: tests pass.

- [ ] **Step 5: Commit**

```bash
git add MSAT/scripts/server_pu_xmsat_run.sh MSAT/scripts/summarize_pu_xmsat_results.py MSAT/scripts/verify_pu_xmsat_final.py MSAT/tests/test_server_pu_xmsat_scripts.py MSAT/tests/test_summarize_pu_xmsat_results.py
git commit -m "chore: prepare bounded full PU server pilot"
```

## Task 7: Final Local Verification And Server Pilot

**Files:**
- Read-only verification unless a command fails and exposes a concrete defect.

- [ ] **Step 1: Run full local test suite**

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 2: Run baseline and final verifiers**

```bash
/Users/a67_2024/opt/anaconda3/bin/python scripts/verify_pu_xmsat_baseline.py
/Users/a67_2024/opt/anaconda3/bin/python scripts/verify_pu_xmsat_final.py
```

Expected: both report `"ok": true`.

- [ ] **Step 3: Run one-fold full backend pilot on server**

```bash
cd /root/autodl-tmp/drug-detect/MSAT
PU_XMSAT_BACKEND=full_msat_pu \
PU_XMSAT_MAX_FOLDS=1 \
PU_XMSAT_MAX_EPOCHS=1 \
PU_XMSAT_MAX_PAIRS=96 \
bash scripts/server_pu_xmsat_run.sh
```

Expected: `results/pu_training_summary.json` has `training_backend: full_msat_pu`, finite loss, and finite test metrics.

- [ ] **Step 4: Pull server pilot results and inspect**

```bash
rsync -azP -e "ssh -i /tmp/codex_autodl_key -p <PORT> -o StrictHostKeyChecking=no -o UserKnownHostsFile=/tmp/codex_known_hosts_autodl" \
  root@<REMOTE_HOST>:/root/autodl-tmp/drug-detect/MSAT/results/pu_training_summary.json \
  /Users/a67_2024/Desktop/drug-detect/MSAT/results/pu_training_summary.json
```

Expected: local summary contains full backend pilot metrics.

- [ ] **Step 5: Commit pilot artifacts only if scientifically useful**

Commit full-backend pilot artifacts only after confirming they are not misleading and do not overwrite baseline artifacts.
