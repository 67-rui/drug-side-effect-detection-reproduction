# Evidence-Aware Candidate Reranking Design

## Context

The final PU-XMSAT top-5000 export contains 391 candidates with parseable explicit mechanism paths. The previous deep interpretation pass selected 20 mechanism-supported candidates and quantified local component, target, and pathway perturbation sensitivity, but the top-20 set was model-priority rather than evidence-priority. First-pass external review found 0/20 strong complete-chain external validation cases.

## Goal

Build a reproducible evidence-aware queue that reranks the 391 explicit-path candidates to identify 20-30 candidates that are more suitable for manual external evidence review and manuscript case selection.

## Non-Goals

- Do not claim that reranked candidates are externally validated.
- Do not infer real compound or target names from graph-local IDs.
- Do not run expensive perturbation quantification for all 391 candidates in the first version.
- Do not replace the existing top-20 perturbation artifacts; use them as known deep-interpretability evidence where available.

## Approach

Create a focused script that reads `results/pu_xmsat_top_predictions_top5000.json`, filters candidates with explicit mechanism paths, and computes an evidence-aware priority score from:

- prediction rank and model score;
- explicit path count and parseable compound/target node coverage;
- availability of prior perturbation sensitivity for already quantified cases;
- herb/ADR diversity to avoid a queue dominated by the same few herbs;
- evidence-retrievability heuristics based on herb/ADR names, exact species specificity, and ADR term class.

The first version is deterministic and local-only. It may generate search query strings for PubMed, EMA, openFDA, and general manual review, but it will not treat search-hit counts as evidence unless later manually verified.

## Outputs

- `results/evidence_aware_mechanism_candidate_queue.json`
- `results/evidence_aware_mechanism_candidate_queue.csv`
- `results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`

The report must include the source candidate count, reranked top candidates, score components, diversity notes, and claim boundaries.

## Testing

Add unit tests for:

- filtering 391 explicit-path candidates from top predictions;
- score computation with model, path, diversity, and retrievability components;
- deterministic ranking and top-k truncation;
- artifact writing with claim-boundary metadata.

## Manuscript Use

Use the new queue to choose manual-review candidates. It should support wording such as: "We expanded the mechanism-supported pool from 20 deeply quantified candidates to 391 explicit-path candidates and reranked them for evidence review." It should not support wording such as: "The reranked candidates are externally validated mechanisms."
