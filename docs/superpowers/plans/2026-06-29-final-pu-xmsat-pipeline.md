# Final PU-XMSAT Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested server-side pipeline entrypoint that runs the full 10-fold final PU-XMSAT checkpoint export and then regenerates top predictions, contribution quantification, batch interpretability, aggregate summary, and the Direction 3 evidence queue.

**Architecture:** Create one Python orchestration script under `MSAT/scripts/` that builds subprocess argument lists from a validated formal configuration. The script refuses nonfinal fold counts by default, supports `--dry-run` for auditability, and writes no credentials.

**Tech Stack:** Python standard library (`argparse`, `subprocess`, `json`, `dataclasses`, `pathlib`), existing MSAT scripts, pytest.

---

### Task 1: Pipeline Command Builder And Validation

**Files:**
- Create: `MSAT/scripts/run_final_pu_xmsat_interpretability_pipeline.py`
- Create: `MSAT/tests/test_run_final_pu_xmsat_interpretability_pipeline.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_default_pipeline_uses_full_final_configuration():
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(["--dry-run"])
    pipeline.validate_args(args)
    commands = pipeline.build_pipeline_commands(args)

    training = commands[0].argv
    assert "--backend" in training
    assert training[training.index("--backend") + 1] == "full_msat_pu"
    assert training[training.index("--max-folds") + 1] == "10"
    assert training[training.index("--max-epochs") + 1] == "200"
    assert training[training.index("--max-pairs") + 1] == "66015"
    assert "--save-checkpoints" in training
    assert "saved_models/pu_xmsat_formal" in training
    assert "best_model_for_prediction" not in " ".join(training)

    top_predictions = commands[1].argv
    assert "--checkpoint-is-final-pu-xmsat" in top_predictions
    assert top_predictions[top_predictions.index("--top-k") + 1] == "50"
```

```python
def test_pipeline_rejects_nonfinal_fold_count_without_override():
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args(["--max-folds", "1", "--dry-run"])
    with pytest.raises(ValueError, match="full 10-fold"):
        pipeline.validate_args(args)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_run_final_pu_xmsat_interpretability_pipeline.py -q
```

Expected: FAIL because the script module does not exist.

- [ ] **Step 3: Implement the script**

Create `PipelineStep`, `build_arg_parser()`, `validate_args(args)`, `formal_prefix(args)`, `formal_checkpoint_path(args)`, `build_pipeline_commands(args)`, `run_pipeline(args)`, and `main(argv=None)`. Defaults must use seed 2026, 10 folds, 200 epochs, 66,015 pair budget, hybrid sampling, `val_f1`, `u0.2/rn0.8`, top-K 50, contribution max-cases 50, and CUDA device.

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_run_final_pu_xmsat_interpretability_pipeline.py -q
```

Expected: PASS.

### Task 2: Pipeline Runner And Manifest Behavior

**Files:**
- Modify: `MSAT/scripts/run_final_pu_xmsat_interpretability_pipeline.py`
- Modify: `MSAT/tests/test_run_final_pu_xmsat_interpretability_pipeline.py`

- [ ] **Step 1: Add failing tests**

```python
def test_dry_run_writes_manifest_without_executing(tmp_path):
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args([
        "--dry-run",
        "--manifest",
        str(tmp_path / "manifest.json"),
    ])
    executed = []
    pipeline.run_pipeline(args, runner=lambda *a, **k: executed.append(a))
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert executed == []
    assert manifest["dry_run"] is True
    assert manifest["commands"][0]["name"] == "train_final_checkpoint"
```

```python
def test_runner_stops_when_a_step_fails(tmp_path):
    pipeline = _module()
    args = pipeline.build_arg_parser().parse_args([
        "--allow-nonfinal-config",
        "--max-folds",
        "10",
        "--manifest",
        str(tmp_path / "manifest.json"),
    ])
    calls = []

    def runner(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 2)

    with pytest.raises(RuntimeError, match="failed"):
        pipeline.run_pipeline(args, runner=runner)
    assert len(calls) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_run_final_pu_xmsat_interpretability_pipeline.py -q
```

Expected: FAIL until manifest and failure behavior are implemented.

- [ ] **Step 3: Implement manifest and runner**

In `run_pipeline`, always build command metadata, write the manifest path before execution, return early for `--dry-run`, and execute each step with `subprocess.run(..., cwd=MSAT_ROOT, env=PYTHONPATH includes MSAT_ROOT)`. Raise `RuntimeError` on first nonzero return code.

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_run_final_pu_xmsat_interpretability_pipeline.py -q
```

Expected: PASS.

### Task 3: Documentation Wiring

**Files:**
- Modify: `MSAT/results/PU_XMSAT_FINAL_CHECKPOINT_EXPORT_REPORT.md`
- Modify: `MSAT/results/PU_XMSAT_DELIVERABLE_INDEX_CN.md`
- Modify: `MSAT/results/README.md`
- Modify: `MSAT/PROJECT_MEMORY.md`

- [ ] **Step 1: Update docs to reference the pipeline script**

Add the command:

```bash
PYTHONPATH=. python scripts/run_final_pu_xmsat_interpretability_pipeline.py
```

and explain that it runs the full final pipeline and refuses nonfinal fold counts unless explicitly overridden.

- [ ] **Step 2: Verify docs and tests**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests -q
PYTHONPATH=. python scripts/run_final_pu_xmsat_interpretability_pipeline.py --dry-run --manifest results/final_pu_xmsat_pipeline_manifest.json
git diff --check
```

Expected: tests pass, dry-run manifest is written, and diff check is clean.
