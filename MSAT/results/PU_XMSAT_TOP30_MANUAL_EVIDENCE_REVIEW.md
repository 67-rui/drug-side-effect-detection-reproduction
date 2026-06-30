# PU-XMSAT Top30 Manual Evidence Review

**Generated:** 2026-06-30
**Primary source queue:** `MSAT/results/evidence_aware_mechanism_candidate_queue.csv`
**Review table:** `MSAT/results/top30_manual_evidence_review.csv`

## Scope

This file prepares the next manual evidence review pass. It does not add new external-search claims and does not upgrade unverified PubMed or web hits to Grade A/B evidence.

The primary table contains the 30 evidence-aware candidates selected from the 391 explicit-path PU-XMSAT pool. One additional pre-reviewed seed row, `Fragaria vesca L. -> Altered state of consciousness`, is carried in the CSV with `review_rank=seed_boundary_fragaria_asc` because it is already used as a manuscript boundary example but is not part of the evidence-aware top30 queue.

## Evidence Grade Rules

| Grade | Meaning for this review | Manuscript use |
| --- | --- | --- |
| A | Direct species-level CMM/herb adverse-reaction evidence plus compatible mechanism/entity evidence. | Main external evidence case. Not currently assigned. |
| B | Direct or high-quality adverse-reaction evidence for the herb/ADR pair, but incomplete mechanism chain. | Supportive case. Not currently assigned. |
| C | Moderate indirect biological or direction-level support, without direct species-compound-target-ADR validation. | Triage example only. |
| D | No direct support found, or evidence remains too weak/sparse/confounded. | Queue or boundary case only. |
| Conflict | Herb and ADR concept co-occur, but reported direction conflicts with adverse-reaction validation. | Direction-conflict review case. |

## Pre-Filled Evidence Decisions

| Candidate | Evidence source | Direction | Grade | Manuscript use | Boundary |
| --- | --- | --- | --- | --- | --- |
| `Polypodium glycyrrhiza -> Watery diarrhoea` | EMA Polypodii Rhizoma page and EMA assessment report, reviewed in `PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md`. | indirect | C | Main positive mechanism-triage case. | Moderate indirect GI-direction only; no confirmed species-level ADR, compound identity, target identity, or complete mechanism chain. |
| `Marchantia polymorpha -> Liver injury` | PubMed PMID 33128532 and PMID 37273612, reviewed in `PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`. | conflict | Conflict | Direction-conflict evidence-review case. | Hepatoprotective or chemically induced liver-injury model evidence, not adverse liver-injury validation; formal final targeted perturbation remains pending because local final `.pt` weights are absent. |
| `Fragaria vesca L. -> Altered state of consciousness` | EMA Fragariae Folium page and first-pass openFDA/PubMed review in `PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md`. | negative | D | Boundary/negative evidence case. | Weak-to-negative boundary; high rank and perturbation sensitivity do not imply external support. |
| `Marchantia polymorpha -> Dry cough` | Existing top30 queue and first-pass screen. | none | D | Quantified same-herb queue case only. | Already quantified, but no direct support in the first-pass screen. |

## Review Instructions

For each queued row, reviewers should record:

- the exact source checked;
- URL, PMID, database name, or document title;
- access date;
- whether evidence supports, indirectly relates to, conflicts with, or fails to support the CMM-ADR direction;
- why the evidence grade is assigned;
- whether the row can be used in the manuscript, supplement, or only as a no-support example.

Do not infer compound or target names from `compound:<id>` or `target:<id>`. These remain MSAT graph-local identifiers unless an original node dictionary or source-ID bridge is recovered.

## Current Manuscript Boundary

The top30 review table supports evidence-aware prioritization. It does not currently support strong external validation, clinical validation, causal interpretation, SHAP-style explanation, or confirmed compound/target identity.
