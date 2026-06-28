# PU-XMSAT Case Selection Decision

**Date:** 2026-06-28  
**Purpose:** Decide whether the current project already has a strong paper-ready case study after completing PU-XMSAT, mechanism extraction, evidence grading, and Grade C manual review.

## Decision

The current project does **not** yet have a strong positive external-validation case suitable for a Table 5-style claim.

The project does have a complete case-screening workflow:

1. candidate prediction table;
2. mechanism path extraction;
3. evidence grading;
4. manual review of Grade C cases;
5. explicit manuscript claim boundaries.

This is enough to write the method and screening workflow, but not enough to claim confirmed external validation of the current top candidates.

## Evidence Checked

| Evidence Source | Result |
| --- | --- |
| Current `table5_top15.csv` / `table5_summary.json` | 15 current Table 5-style candidates; support rate 1/15 by internal mechanism/database criterion |
| `evidence_screening_table.csv` | Only one Grade C row: `Fragaria vesca L.` -> Altered state of consciousness |
| `PU_XMSAT_CASE_EVIDENCE_REPORT.md` | 16 candidate rows total; 2 Grade C, 14 Grade D |
| `PU_XMSAT_GRADE_C_MANUAL_EVIDENCE_AUDIT.md` | Both Grade C rows fail to upgrade to direct external evidence |
| `tcmda_cache.json` | Seeded from the original paper Table 5 reference flags; should not be used as new evidence for current local candidates |

## Candidate-Level Decision

| Candidate | Internal Status | Manual External Review | Decision |
| --- | --- | --- | --- |
| `Fragaria vesca L.` -> Altered state of consciousness | Current top15 Grade C through one graph path | No direct support found; EMA wild-strawberry leaf material does not support neurological ADR | Do not use as positive case |
| `Citrus aurantium L.` -> Watery diarrhoea | Curated mechanism case; nobiletin/ABCG2 hints | Gut-related evidence exists, but direction points toward anti-inflammatory/anti-diarrhoeal regulation rather than adverse diarrhoea induction | Use only as hypothesis-generating mechanism example |

## Manuscript Strategy

Recommended wording:

> Case-level screening produced a conservative evidence profile. The current candidates demonstrate that the proposed workflow can combine prediction scores, mechanism paths, and external evidence triage, but manual review did not identify direct external support strong enough to promote the Grade C cases to confirmed validation examples.

Do not write:

- "PU-XMSAT has externally validated case predictions."
- "The current Table 5-style cases reproduce the paper's Table 5 support rate."
- "Citrus aurantium is confirmed to cause watery diarrhoea."
- "Fragaria vesca is supported by literature for altered consciousness."

## Next Action If Strong Case Evidence Is Required

Do **not** continue long training just to look for a case. A stronger case should be selected by a targeted screen:

1. start from high-confidence prediction candidates;
2. require an explicit mechanism path;
3. require direct database or literature evidence before treating the row as a positive case;
4. manually verify the source before assigning Grade A/B;
5. keep unsupported but plausible rows as Grade C/D only.

If no such candidate appears in the current candidate pool, the paper should present case evidence as a conservative screening workflow and leave confirmed external validation as future work.

