# PU-XMSAT Direction 2 and Direction 3 Extension Plan

Date: 2026-06-29

## Purpose

The main PU-XMSAT prediction result is already strong enough for a conservative manuscript. The remaining work should improve paper value by strengthening the interpretation and evidence layers rather than blindly rerunning the main ten-fold experiment.

## Current Judgment

Direction 2 has now been refreshed with the formal full-positive hybrid PU-XMSAT checkpoint. The current mechanism layer is no longer the old local-predictor two-case demo: it uses the final checkpoint top-50 prediction export, records 50 top-prediction candidates, marks 49 as coverage-missing because they lack parseable explicit mechanism paths, and perturbation-quantifies the one explicit-path case. All node/path drops in the quantified case are near-zero.

Direction 3 remains targeted. Current evidence grading has no manually verified Grade B/A case. This is acceptable for a conservative screening paper, but not enough for a claim of external validation.

## Immediate Execution Order

1. Treat `PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY.md` as the current Direction 2 entry point.
2. Treat `PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md` as the current aggregate contribution entry point.
3. Treat `PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md` as the current Direction 3 queue.
4. Do not use the old local-predictor two-case perturbation rows as the manuscript's primary explanation result.

## New Direction 2 Artifacts

The next artifact set should be:

- `results/contribution_aggregate_summary.json`
- `results/contribution_aggregate_summary.csv`
- `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`

These files should summarize compounds, targets, and paths with explicit positive, near-zero, and negative perturbation buckets. They remain interpretation artifacts, not causal effects or SHAP attributions.

## Manuscript Claim Boundary

Use:

> PU-XMSAT adds a mechanism-prioritization layer by extracting candidate mechanism subgraphs and summarizing local node/path perturbation sensitivity.

Avoid:

> PU-XMSAT proves causal mechanisms, validates clinical adverse reactions, or provides SHAP-equivalent explanation.

## Current Execution Status

As of 2026-06-29, Direction 2 has a reproducible aggregate contribution report:

- `results/contribution_aggregate_summary.json`
- `results/contribution_aggregate_summary.csv`
- `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md`

Direction 3 now has a targeted review queue derived from the Direction 2 perturbation outputs:

- `results/direction3_targeted_review_queue.json`
- `results/direction3_targeted_review_queue.csv`
- `results/PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md`

The queue now contains one final-checkpoint explicit-path candidate, Fragaria--altered-consciousness. It remains a Grade C boundary case after manual review. The queue contains zero ready strong-evidence cases, so the manuscript should continue to describe this layer as screening and prioritization, not external validation.

## Stop Conditions

Stop expanding Direction 2 when the project has:

- a reproducible aggregate contribution report;
- a clear top target/path table;
- checkpoint provenance stated in the report;
- manuscript wording that does not overclaim.

Stop expanding Direction 3 when:

- targeted review produces no Grade B evidence after manual review; or
- one or more Grade B cases are found and can be safely added to the manuscript.
