# PU-XMSAT Direction 2 and Direction 3 Extension Plan

Date: 2026-06-29

## Purpose

The main PU-XMSAT prediction result is already strong enough for a conservative manuscript. The remaining work should improve paper value by strengthening the interpretation and evidence layers rather than blindly rerunning the main ten-fold experiment.

## Current Judgment

Direction 2 is the priority. The existing mechanism layer has a minimal working loop: key subgraph extraction, node perturbation, and path perturbation for two mechanism-supported cases. This supports a workflow claim, but it is still thin for a strong paper contribution because it covers only a small case set and uses the local predictor checkpoint rather than an explicitly exported final full-positive hybrid PU-XMSAT checkpoint.

Direction 3 should be targeted. Current evidence grading has no manually verified Grade B case. This is acceptable for a conservative screening paper, but not enough for a claim of external validation.

## Immediate Execution Order

1. Generate a contribution aggregate summary from the current Direction 2 output.
2. If a final hybrid PU checkpoint exists, rerun contribution scoring with that checkpoint; otherwise keep the checkpoint boundary explicit.
3. Use the strongest positive target/path perturbation cases as the entry point for targeted external evidence review.
4. Only update the Overleaf manuscript when the generated artifacts support stronger wording.

## New Direction 2 Artifacts

The next artifact set should be:

- `results/contribution_aggregate_summary.json`
- `results/contribution_aggregate_summary.csv`
- `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`

These files should summarize top compounds, targets, and paths by positive perturbation sensitivity across cases. They remain interpretation artifacts, not causal effects or SHAP attributions.

## Manuscript Claim Boundary

Use:

> PU-XMSAT adds a mechanism-prioritization layer by extracting candidate mechanism subgraphs and summarizing local node/path perturbation sensitivity.

Avoid:

> PU-XMSAT proves causal mechanisms, validates clinical adverse reactions, or provides SHAP-equivalent explanation.

## Stop Conditions

Stop expanding Direction 2 when the project has:

- a reproducible aggregate contribution report;
- a clear top target/path table;
- checkpoint provenance stated in the report;
- manuscript wording that does not overclaim.

Stop expanding Direction 3 when:

- targeted review produces no Grade B evidence after manual review; or
- one or more Grade B cases are found and can be safely added to the manuscript.
