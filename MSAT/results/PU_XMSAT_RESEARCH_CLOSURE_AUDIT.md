# PU-XMSAT Research Closure Audit

**Date:** 2026-06-28  
**Scope:** Audit whether the research direction proposed in `RESEARCH_DIRECTION_TECHNICAL_PROPOSAL.md` has been converted into a paper-facing reproducible research loop.  
**Branch:** `codex/pu-xmsat-implementation`

## Bottom Line

The project now has a complete minimal paper-facing loop:

1. reproduced MSAT baseline;
2. incomplete-label motivation;
3. reliable-negative and PU training implementation;
4. seed-robust hybrid PU-XMSAT comparison;
5. weight sensitivity;
6. mechanism subgraph, node contribution, and path contribution analysis;
7. external evidence grading and manual review;
8. causal-bias claim boundary.

This is sufficient to write a conservative manuscript-style Methods/Results/Discussion draft. It is not sufficient to claim full Table 5/6 reproduction, confirmed external validation of the case studies, or causal effects.

## Requirement-to-Evidence Audit

| Proposal requirement | Current status | Evidence | Remaining boundary |
| --- | --- | --- | --- |
| Freeze original MSAT as baseline | Achieved | `results/summary.json`, `results/reproduction_state_audit.json`, `scripts/verify_pu_xmsat_baseline.py` | Full-paper auxiliary tables still have known differences |
| Treat unobserved pairs as incomplete labels | Achieved | `experiments/pu_dataset_builder.py`, `experiments/pu_loss.py`, `experiments/full_msat_pu_training.py` | This reduces label-noise assumptions but does not identify true negatives |
| Reliable negative sampling | Achieved | `experiments/reliable_negative_sampling.py`, `results/pu_candidate_scores.sample.jsonl`, full-positive hybrid results | Candidate score is heuristic and should be described as reliable-negative selection, not ground truth |
| PU Learning training comparison | Achieved | `results/PU_XMSAT_FULL_MSAT_PILOT_REPORT.md`, `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`, `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv` | AUPRC gain is small and one seed is borderline versus MSAT |
| Negative strategy comparison | Achieved | `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv`, `results/PU_XMSAT_RESEARCH_PROGRESS_REPORT.md` | Legacy prefix-cache pilots must not be used as final evidence |
| PU weight sensitivity | Achieved | `results/pu_xmsat_hybrid_weight_sensitivity_summary.csv` | Only focused sensitivity around the strongest setting was run |
| Mechanism subgraph extraction | Achieved at minimal case-study level | `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md`, `results/contribution_quantification.json` | Current report covers two mechanism-supported cases, not a large case cohort |
| Compound and target contribution | Achieved at perturbation-sensitivity level | `results/contribution_quantification.csv` node rows | These are local score drops, not SHAP values or causal effects |
| Path contribution | Achieved at perturbation-sensitivity level | `results/contribution_quantification.csv` path rows | Negative drops mean masking increased model score; do not overinterpret biologically |
| External evidence grading | Achieved conservatively | `results/PU_XMSAT_CASE_EVIDENCE_REPORT.md`, `results/case_evidence_report.json`, `results/case_evidence_report.csv` | No current row has manually verified direct Grade A/B support |
| Manual review of strongest evidence cases | Achieved | `results/PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md`, `results/case_evidence_manual_review.json` | Both Grade C rows fail to upgrade to direct support |
| Case selection decision | Achieved | `results/PU_XMSAT_CASE_SELECTION_DECISION.md` | Case section should be framed as screening workflow, not confirmed validation |
| Causal graph / confounding framework | Achieved as discussion framework | `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` | No causal estimator is implemented because required patient-level variables are unavailable |
| Manuscript-ready result wording | Achieved as draft | `results/PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md`, `results/PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` | Needs journal-specific editing before submission |

## Current Strongest Scientific Claim

The strongest claim supported by current evidence is:

> Under the reproduced MSAT protocol, full-positive hybrid PU-XMSAT shows seed-robust gains over the reproduced MSAT baseline on AUC, F1, and MCC, with a stable positive but smaller AUPRC trend. The method also provides a conservative interpretation workflow combining mechanism subgraphs, local perturbation sensitivity, evidence grading, and causal-bias claim boundaries.

## Claims That Remain Unsupported

Do not claim:

1. full MSAT paper reproduction including Table 5/6;
2. PU-XMSAT universal superiority on every metric;
3. confirmed external validation of current case predictions;
4. causal effects of CMM exposure on ADR risk;
5. SHAP-equivalent attribution;
6. clinical risk incidence or dose-specific safety conclusions.

## Practical Next Step

The next research step should be writing and polishing, not more blind training. Specifically:

1. integrate `PU_XMSAT_MANUSCRIPT_RESULTS_DRAFT.md` and `PU_XMSAT_MANUSCRIPT_SECTIONS_DRAFT.md` into a single manuscript draft;
2. use `PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md` in the limitations or discussion section;
3. keep the case section conservative unless a future targeted screen finds a Grade A/B externally supported case;
4. only use the H800 server for targeted follow-up experiments, such as exporting a final PU checkpoint for attribution or running a larger case-contribution batch.

## Completion Judgment

The proposal's current-stage plan has been completed as a minimal, conservative research loop. The remaining items are either manuscript polishing or future-work extensions that require additional evidence or data beyond the current project scope.
