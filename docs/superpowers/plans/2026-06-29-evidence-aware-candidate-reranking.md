# Evidence-Aware Candidate Reranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic evidence-aware queue from the 391 explicit-path PU-XMSAT candidates.

**Architecture:** Add one focused script under `MSAT/scripts/` that reads final top-5000 predictions and optional existing contribution rows, scores explicit-path candidates, and writes JSON/CSV/Markdown artifacts. Add one unit-test file under `MSAT/tests/` covering filtering, scoring, diversity penalties, and artifact writing.

**Tech Stack:** Python standard library, pytest, existing MSAT JSON artifacts.

---

### Task 1: Evidence-Aware Queue Builder

**Files:**
- Create: `MSAT/tests/test_build_evidence_aware_candidate_queue.py`
- Create: `MSAT/scripts/build_evidence_aware_candidate_queue.py`

- [ ] **Step 1: Write failing tests**

Write tests for `build_evidence_aware_queue()` and `write_outputs()` using small in-memory payloads.

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONPATH=. pytest tests/test_build_evidence_aware_candidate_queue.py -q
```

Expected: import failure because the script does not exist yet.

- [ ] **Step 3: Implement minimal queue builder**

Implement explicit-path filtering, score components, deterministic ranking, top-k truncation, JSON/CSV/MD writers, and CLI defaults.

- [ ] **Step 4: Verify targeted tests pass**

Run:

```bash
PYTHONPATH=. pytest tests/test_build_evidence_aware_candidate_queue.py -q
```

Expected: all tests pass.

### Task 2: Generate Real Artifacts

**Files:**
- Generate: `MSAT/results/evidence_aware_mechanism_candidate_queue.json`
- Generate: `MSAT/results/evidence_aware_mechanism_candidate_queue.csv`
- Generate: `MSAT/results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`

- [ ] **Step 1: Run builder on final top-5000 export**

Run:

```bash
PYTHONPATH=. python scripts/build_evidence_aware_candidate_queue.py \
  --top-predictions results/pu_xmsat_top_predictions_top5000.json \
  --batch-interpretability results/batch_mechanism_interpretability_top5000_random_controls.json \
  --top-k 30
```

Expected: summary reports 391 explicit-path candidates and 30 queued rows.

- [ ] **Step 2: Inspect top rows**

Confirm the top rows are not only a repeat of the previous top-20 and include score components plus manual-review query strings.

### Task 3: Documentation And Verification

**Files:**
- Modify: `MSAT/results/README.md`
- Modify: `MSAT/results/PU_XMSAT_DELIVERABLE_INDEX_CN.md`
- Modify: `MSAT/PROJECT_MEMORY.md`

- [ ] **Step 1: Add artifact links and claim boundaries**

Document that this queue expands from the 20 quantified cases to the 391 explicit-path candidate pool, but remains a manual-review priority list.

- [ ] **Step 2: Run full checks**

Run:

```bash
PYTHONPATH=. pytest tests -q
git diff --check
```

Expected: tests pass and whitespace check is clean.
