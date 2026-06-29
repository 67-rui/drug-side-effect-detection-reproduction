# PU-XMSAT Direction 2 and Direction 3 Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen the manuscript beyond the main PU-XMSAT prediction result by expanding mechanism interpretation outputs first, then performing targeted external-evidence screening on the most interpretable candidates.

**Architecture:** Keep the reproduced MSAT and PU-XMSAT prediction protocol frozen. Add paper-facing scripts that consume existing curated JSON/CSV artifacts, generate auditable mechanism contribution summaries, and update the Overleaf manuscript only when the generated evidence supports the claim boundary.

**Tech Stack:** Python 3, pytest, pandas-free standard-library CSV/JSON processing where possible, existing MSAT inference scripts, ACM LaTeX manuscript project under `Template/PU-XMSAT-Overleaf`.

---

## Files

- Modify: `MSAT/scripts/run_contribution_quantification.py` only if batch metadata or output options are missing.
- Create: `MSAT/scripts/summarize_contribution_quantification.py`
- Create: `MSAT/tests/test_summarize_contribution_quantification.py`
- Generate: `MSAT/results/contribution_aggregate_summary.json`
- Generate: `MSAT/results/contribution_aggregate_summary.csv`
- Generate: `MSAT/results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`
- Generate: `MSAT/results/PU_XMSAT_DIRECTION23_EXTENSION_PLAN.md`
- Later modify: `Template/PU-XMSAT-Overleaf/main.tex` only after generated mechanism/evidence results justify stronger wording.

## Task 1: Baseline Guardrail

- [ ] **Step 1: Verify reproduction audit before new experiments**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
python scripts/verify_pu_xmsat_baseline.py
python scripts/verify_pu_xmsat_final.py --audit-out results/reproduction_state_audit.direction23.json
```

Expected:

```text
baseline verification exits 0
final audit exits 0 or reports only known Table 5/6 external-evidence boundaries
```

- [ ] **Step 2: Keep current main-result claim frozen**

The manuscript may continue to claim seed-robust full-positive hybrid PU-XMSAT gains over reproduced MSAT on AUC, F1, and MCC, with a smaller positive AUPRC trend. It must not claim causal effects, SHAP attribution, or externally confirmed case validation.

## Task 2: Contribution Aggregation Script

- [ ] **Step 1: Write the failing test**

Create `MSAT/tests/test_summarize_contribution_quantification.py` with tests that build a temporary contribution JSON containing two cases, repeated target/path features, positive and negative score drops, then assert:

```python
summary["case_count"] == 2
summary["positive_node_count"] == 3
summary["positive_path_count"] == 2
summary["top_nodes"][0]["feature"] == "target:20"
summary["top_nodes"][0]["case_count"] == 2
summary["top_paths"][0]["path_features"] == "compound:10;target:20"
```

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_summarize_contribution_quantification.py -q
```

Expected:

```text
FAIL because scripts.summarize_contribution_quantification does not exist
```

- [ ] **Step 2: Implement `MSAT/scripts/summarize_contribution_quantification.py`**

The script must expose these functions:

```python
load_contribution_payload(path: str | Path) -> dict
summarize_contributions(payload: dict, top_k: int = 10) -> dict
write_summary_artifacts(summary: dict, output_json: Path, output_csv: Path, output_md: Path) -> None
```

Behavior:

- Aggregate node rows by `feature`, `node_type`, and `node_id`.
- Aggregate path rows by semicolon-joined `features`.
- Track `case_count`, `occurrence_count`, `mean_score_drop`, `max_score_drop`, `positive_drop_count`, and `negative_drop_count`.
- Sort by `mean_score_drop` descending, then `max_score_drop` descending, then feature key.
- Generate a Markdown report with claim boundary text: "These are perturbation sensitivity aggregates, not causal or SHAP attributions."

- [ ] **Step 3: Run the new test**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. pytest tests/test_summarize_contribution_quantification.py -q
```

Expected:

```text
all tests pass
```

## Task 3: Generate Current Direction 2 Aggregate Evidence

- [ ] **Step 1: Run aggregation on current contribution output**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. python scripts/summarize_contribution_quantification.py \
  --input results/contribution_quantification.json \
  --output-json results/contribution_aggregate_summary.json \
  --output-csv results/contribution_aggregate_summary.csv \
  --output-md results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md \
  --top-k 10
```

Expected:

```text
Wrote contribution aggregate summary
```

- [ ] **Step 2: Verify generated artifacts**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
test -s results/contribution_aggregate_summary.json
test -s results/contribution_aggregate_summary.csv
test -s results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md
rg -n "perturbation sensitivity|not causal|not SHAP" results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md
```

Expected:

```text
all commands exit 0
```

## Task 4: Optional Final PU Checkpoint Attribution

- [ ] **Step 1: Check whether a final hybrid PU prediction checkpoint exists**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
find saved_models -maxdepth 1 -type f -name '*pu*xmsat*hybrid*pt' -o -name 'best_model_for_prediction_pu*.pt'
```

Expected:

```text
one explicit final hybrid PU checkpoint path, or no output
```

- [ ] **Step 2: If no explicit final checkpoint exists, keep the manuscript boundary unchanged**

Use the existing local predictor checkpoint result only as a mechanism workflow demonstration. Do not describe it as final full-positive hybrid PU-XMSAT attribution.

- [ ] **Step 3: If a final checkpoint exists, rerun contribution quantification with that checkpoint**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. python scripts/run_contribution_quantification.py \
  --input results/explanation_case_studies.json \
  --checkpoint saved_models/best_model_for_prediction_pu_xmsat_hybrid_seed2026_full.pt \
  --max-cases 10 \
  --max-features 10 \
  --output-json results/contribution_quantification_pu_hybrid_topk.json \
  --output-csv results/contribution_quantification_pu_hybrid_topk.csv \
  --output-md results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION_PU_HYBRID_TOPK.md
```

Expected:

```text
script exits 0 and report clearly names the PU checkpoint
```

## Task 5: Direction 3 Targeted Evidence Review

- [ ] **Step 1: Select evidence-review cases from Direction 2**

Use cases with positive path-level or target-level perturbation sensitivity first. If only two current cases are available, review those two and state that the evidence layer remains a targeted screening pilot.

- [ ] **Step 2: Fetch automated review candidates**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
PYTHONPATH=. python scripts/fetch_table5_literature_evidence.py \
  --table5 results/table5_top15.csv \
  --output-csv results/direction3_targeted_literature_candidates.csv \
  --output-json results/direction3_targeted_literature_candidates.json \
  --limit 15
```

Expected:

```text
candidate files exist; no row is upgraded without manual verification
```

- [ ] **Step 3: Preserve evidence grading discipline**

Grade B requires a manually verified source that directly supports the same herb and ADR. Automated keyword hits remain review candidates. Mechanism-only cases remain Grade C. Prediction-only cases remain Grade D.

## Task 6: Manuscript Integration Gate

- [ ] **Step 1: Update manuscript only if the new artifacts strengthen the supported claim**

Modify `Template/PU-XMSAT-Overleaf/main.tex` only after `PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md` or targeted evidence review gives stronger paper-facing material.

- [ ] **Step 2: Compile and visually verify**

Run:

```bash
cd /Users/a67_2024/Desktop/drug-detect/Template/PU-XMSAT-Overleaf
latexmk -pdf -interaction=nonstopmode main.tex
pdfinfo main.pdf | rg "Pages|Page size"
```

Expected:

```text
latexmk exits 0
PDF remains ACM review manuscript on Letter paper
```

## Self-Review

- The plan prioritizes Direction 2 before Direction 3.
- It avoids rerunning the already sufficient main prediction experiment.
- It separates perturbation sensitivity from causal, SHAP, and external-validation claims.
- It requires generated artifacts before manuscript claim strengthening.
