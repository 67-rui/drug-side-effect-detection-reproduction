# Reproduction Protocol Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove remaining protocol-level leakage and artifact ambiguity before any MSAT reproduction results are cited.

**Architecture:** Keep the existing training and baseline structure, but add small protocol helpers around graph edge removal, checkpoint paths, thresholded predictions, and imbalanced configuration. Tests should assert the exact reproduction contract so future experiment runs cannot silently regress.

**Tech Stack:** Python, PyTorch/PyG, pytest, existing MSAT scripts.

---

### Task 1: Validation Edge Isolation

**Files:**
- Modify: `MSAT/train.py`
- Modify: `MSAT/baselines/common.py`
- Test: `MSAT/tests/test_protocol_edge_isolation.py`

- [x] **Step 1: Write failing tests**

Add tests that construct a small heterogeneous graph containing training, validation, and test CMM-ADR positive edges. Assert that the protocol removal helper removes validation and test positives while preserving training positives and reverse edges stay consistent.

- [x] **Step 2: Verify tests fail**

Run:

```bash
cd MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_protocol_edge_isolation.py -q
```

Expected before implementation: at least one assertion failure showing validation positive edges remain.

- [x] **Step 3: Implement minimal protocol helper**

Create a helper in `MSAT/train.py` to combine validation and test positive pairs before calling `_remove_cmm_adr_pairs()`. Use the same logic in `MSAT/baselines/common.py::prepare_fold()` so MSAT and GNN baselines use the same inductive validation protocol.

- [x] **Step 4: Verify tests pass**

Run the same pytest command and confirm all tests in `test_protocol_edge_isolation.py` pass.

### Task 2: Checkpoint Provenance and Selection

**Files:**
- Modify: `MSAT/train.py`
- Test: `MSAT/tests/test_checkpoint_paths.py`

- [x] **Step 1: Write failing tests**

Extend checkpoint tests to assert fold checkpoints include the experiment tag when present, and that the prediction checkpoint selection score is validation AUC rather than test AUC.

- [x] **Step 2: Verify tests fail**

Run:

```bash
cd MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_checkpoint_paths.py -q
```

Expected before implementation: tagged fold checkpoint path helpers are missing, or selection policy still refers to test AUC.

- [x] **Step 3: Implement minimal checkpoint helpers**

Add `fold_checkpoint_path(fold_idx, experiment_tag='')` and `model_selection_score(fold_result)` in `MSAT/train.py`. Thread `experiment_tag` into `train_single_fold()`, save fold checkpoints with tagged names for tagged experiments, and select `best_model_for_prediction*.pt` by `best_val_auc`.

- [x] **Step 4: Verify tests pass**

Run the same pytest command and confirm checkpoint path and selection tests pass.

### Task 3: Threshold and 1:10 Configuration Consistency

**Files:**
- Modify: `MSAT/train.py`
- Modify: `MSAT/baselines/gnn_models.py`
- Modify: `MSAT/scripts/run_imbalanced.py`
- Modify: `MSAT/scripts/run_baselines.py`
- Test: `MSAT/tests/test_threshold_protocol.py`
- Test: `MSAT/tests/test_script_protocol_config.py`

- [x] **Step 1: Write failing tests**

Add tests asserting saved `y_pred` uses the fold optimal threshold, GNN metrics can use a supplied threshold, and 1:10 entrypoints set both `NEG_RATIO` and `TEST_NEG_RATIO` to 10.

- [x] **Step 2: Verify tests fail**

Run:

```bash
cd MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests/test_threshold_protocol.py tests/test_script_protocol_config.py -q
```

Expected before implementation: thresholded prediction and 1:10 config assertions fail.

- [x] **Step 3: Implement minimal consistency fixes**

Save `y_pred` using `optimal_threshold`, add validation-threshold selection for GNN baselines when `TrainingConfig.USE_OPTIMAL_THRESHOLD` is true, and set `DataConfig.TEST_NEG_RATIO = 10` in both 1:10 baseline and MSAT scripts.

- [x] **Step 4: Verify tests pass**

Run the same pytest command and confirm both test files pass.

### Task 4: Full Verification and Audit Notes

**Files:**
- Modify: `MSAT/results/CHECKPOINT_RUNBOOK.md`
- Modify: `MSAT/PROJECT_MEMORY.md`

- [x] **Step 1: Run full local test suite**

Run:

```bash
cd MSAT
/Users/a67_2024/opt/anaconda3/bin/python -m pytest tests -q
```

Expected: all tests pass.

- [x] **Step 2: Run protocol diagnostic**

Run a read-only fold-0 diagnostic that confirms validation and test positive edges are absent from the message-passing graph after protocol removal.

- [x] **Step 3: Update project memory**

Record that old numeric MSAT/GNN results remain invalid until rerun under the corrected validation-edge protocol and checkpoint selection rule.

- [x] **Step 4: Report remaining work**

Summarize code fixes, verification output, and exact experiments that still need server reruns.
