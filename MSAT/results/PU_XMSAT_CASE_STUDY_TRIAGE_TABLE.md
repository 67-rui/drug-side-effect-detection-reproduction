# PU-XMSAT Case-Study Triage Table

**Generated:** 2026-06-29

**Purpose:** publication-facing case-study table for mechanism triage, evidence-boundary discussion, and manual review prioritization.

**Claim boundary:** These examples do not validate a complete herb-compound-target-ADR causal chain. They show how PU-XMSAT links high-ranking predictions to parseable mechanism paths, local perturbation sensitivity where available, and external-evidence grades.

## Primary Case-Study Table

| Role | Candidate | Rank / score | Explicit mechanism paths | Perturbation status | External evidence | Manuscript use |
| --- | --- | ---: | ---: | --- | --- | --- |
| Positive mechanism-triage example | `Polypodium glycyrrhiza` -> `Watery diarrhoea` | 224 / 0.997507 | 7 | Quantified. Top component `compound:761`, score drop 0.0003104806; top target `target:15721`, score drop 0.0011743903; top path `target:15721`, score drop 0.0011743903. | Moderate indirect gastrointestinal-direction support only. EMA polypody material discusses laxative/constipation use, but this is not species-level, compound-level, target-level, or adverse-reaction validation. | Use as the main positive triage case: the model identifies an interpretable local path and the external evidence is directionally relevant but incomplete. |
| Direction-conflict evidence-review example | `Marchantia polymorpha` -> `Liver injury` | 414 / 0.997034 | 8 | Targeted perturbation is pending for the formal final checkpoint because the local workspace currently contains final checkpoint metadata sidecars but not the corresponding final `.pt` weights. The evidence-aware queue records `prior_perturbation_score_drop=0`, meaning no formal prior perturbation result exists for this exact ADR. Top parseable path: `compound:480;target:4`. | PubMed first-pass retained PMID 33128532 and PMID 37273612. Both co-mention `Marchantia polymorpha` and liver injury, but the direction is hepatoprotective or chemically induced liver-injury modeling, not observed adverse liver injury. | Use as a direction-conflict review case: it demonstrates why evidence screening is necessary before upgrading a prediction to validation. Do not present it as a confirmed adverse-reaction case. |
| Boundary / negative evidence example | `Fragaria vesca L.` -> `Altered state of consciousness` | 2 / 0.998971 | 6 | Quantified. Top component `compound:1073`, score drop 0.0000126362; top target `target:7213`, score drop 0.0000047684; top path `compound:1073;target:7213`, score drop 0.0000175238. | Weak-to-negative boundary. EMA wild-strawberry leaf material does not support notable adverse-effect evidence for altered state of consciousness. | Use as a boundary case: high model rank and parseable path do not imply external support. |

## Marchantia Liver-Injury Perturbation Status

The requested Marchantia liver-injury case has a strong reason to appear in the paper, but not as a completed final perturbation case yet.

- Prediction exists in the final top-5000 export: rank 414, score 0.9970338344573975, 8 explicit mechanism paths.
- Evidence-aware review queue includes it as rank 6 with evidence priority score 0.6833383855604183.
- PubMed review found two herb+ADR text matches, but both are direction-conflicting hepatoprotective or chemically induced liver-injury model records.
- The local file system currently has `MSAT/saved_models/pu_xmsat_formal/*.metadata.json` only. It does not have the corresponding formal final `.pt` checkpoint weights required to run a final-checkpoint targeted perturbation for this exact pair.
- Running the old `MSAT/saved_models/best_model_for_prediction.pt` would mix checkpoint contexts and should not be reported as formal PU-XMSAT perturbation evidence.

If the final checkpoint weights are restored, rerun a one-case targeted perturbation for:

```text
herb_id=618
adr_id=5468
herb_latin=Marchantia polymorpha
adr_pt=Liver injury
checkpoint=saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt
```

Until then, the paper should write Marchantia liver injury as an evidence-review and direction-conflict example, not a completed perturbation-quantified mechanism case.

## Optional Same-Herb Quantified Fallback

If a fully quantified Marchantia example is needed for a supplementary sentence, use the already quantified same-herb case:

| Candidate | Rank / score | Paths | Top perturbation |
| --- | ---: | ---: | --- |
| `Marchantia polymorpha` -> `Dry cough` | 239 / 0.997471 | 8 | Top component `compound:480`, score drop 0.0000408292; top target `target:11486`, score drop 0.0000048876; top path `compound:480;target:11486`, score drop 0.0000456572. |

This fallback has no direct external support in the first-pass screen, so it is less valuable for the main manuscript than the liver-injury direction-conflict case.

## Evidence Notes

- Polypodium evidence source: EMA `Polypodii Rhizoma` monograph and assessment report.
- Fragaria evidence source: EMA `Fragariae Folium` material.
- Marchantia evidence sources: PubMed PMID 33128532 and PMID 37273612. These are biologically relevant, but their reported direction is hepatoprotective/preclinical rather than adverse-event validation.

