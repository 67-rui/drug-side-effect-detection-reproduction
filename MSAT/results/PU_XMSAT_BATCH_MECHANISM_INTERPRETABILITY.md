# PU-XMSAT Batch Mechanism Interpretability

- Candidate source: `final_pu_xmsat_top_predictions`
- Candidate source note: Final PU-XMSAT top-ranking export.
- Checkpoint path: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint is final PU-XMSAT: yes
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint attribution.
- Quantified case count: 1
- Top-prediction candidates checked: 50
- Top-prediction rows available: 50
- Requested candidate pool top-K: 5000
- Candidate pool complete: no
- Candidate pool missing rows: 4950
- Coverage-missing top-prediction candidates: 49
- Unquantified explicit-path candidates: 0
- Cases with explicit mechanism paths: 1
- Near-zero sensitivity cases: 1
- Negative score_drop cases: 0
- Fewer than requested top-K: Only 1 candidates with explicit mechanism paths were available.
- Coverage boundary: top-prediction candidates without parseable explicit mechanism paths were counted as coverage-missing, not silently dropped.
- Mechanism coverage by top-K: reported separately so mechanism-supported cases are not treated as representative of all top-ranked predictions.

Perturbation score drops are local sensitivity signals for mechanism triage; they are not causal effects, not SHAP values, and not external clinical validation.
Negative score_drop is not protective biology; it means the score increased after masking.

## Explicit Mechanism Path Coverage

| Top K | Candidates checked | Explicit-path candidates | Coverage rate |
| ---: | ---: | ---: | ---: |
| 50 | 50 | 1 | 0.020000 |
| 100 | 50 | 1 | 0.020000 |
| 500 | 50 | 1 | 0.020000 |
| 1000 | 50 | 1 | 0.020000 |
| 5000 | 50 | 1 | 0.020000 |

## Top Component/Compound Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073` (Compound #1073) | 1 | 0.000013 | 0.000013 | 0 | 1 | 0 |
| 2 | `compound:965` (Compound #965) | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 3 | `compound:1023` (Compound #1023) | 1 | -0.000003 | -0.000003 | 0 | 1 | 0 |

## Top Target Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:7213` (Target #7213) | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 2 | `target:2586` (Target #2586) | 1 | 0.000002 | 0.000002 | 0 | 1 | 0 |
| 3 | `target:6478` (Target #6478) | 1 | 0.000001 | 0.000001 | 0 | 1 | 0 |

## Top Pathway/Path Contributions

| Rank | Path features | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:1073;target:7213` (Compound #1073;Target #7213) | 1 | 0.000018 | 0.000018 | 0 | 2 | 0 |
| 2 | `compound:1073;target:2586` (Compound #1073;Target #2586) | 1 | 0.000015 | 0.000015 | 0 | 2 | 0 |
| 3 | `compound:965;target:7213` (Compound #965;Target #7213) | 1 | 0.000005 | 0.000005 | 0 | 2 | 0 |
| 4 | `compound:965;target:2586` (Compound #965;Target #2586) | 1 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 5 | `compound:1023;target:7213` (Compound #1023;Target #7213) | 1 | 0.000002 | 0.000002 | 0 | 2 | 0 |
| 6 | `compound:1023;target:6478` (Compound #1023;Target #6478) | 1 | -0.000001 | -0.000001 | 0 | 2 | 0 |

## Near-Zero Sensitivity Cases

- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3989

## Negative score_drop Cases

- none

## Random Perturbation Controls

- not available in the current contribution payload

## Coverage-Missing Top-Prediction Candidates

- rank 1, `pu_xmsat_global_unobserved_pairs` herb 234 -> ADR 3989: unparseable_explicit_mechanism_path.
- rank 3, `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 1506: unparseable_explicit_mechanism_path.
- rank 4, `pu_xmsat_global_unobserved_pairs` herb 234 -> ADR 4363: unparseable_explicit_mechanism_path.
- rank 5, `pu_xmsat_global_unobserved_pairs` herb 573 -> ADR 1506: unparseable_explicit_mechanism_path.
- rank 6, `pu_xmsat_global_unobserved_pairs` herb 526 -> ADR 1506: unparseable_explicit_mechanism_path.
- rank 7, `pu_xmsat_global_unobserved_pairs` herb 234 -> ADR 4535: unparseable_explicit_mechanism_path.
- rank 8, `pu_xmsat_global_unobserved_pairs` herb 526 -> ADR 4363: unparseable_explicit_mechanism_path.
- rank 9, `pu_xmsat_global_unobserved_pairs` herb 145 -> ADR 4363: unparseable_explicit_mechanism_path.
- rank 10, `pu_xmsat_global_unobserved_pairs` herb 52 -> ADR 4363: unparseable_explicit_mechanism_path.
- rank 11, `pu_xmsat_global_unobserved_pairs` herb 145 -> ADR 4535: unparseable_explicit_mechanism_path.
- rank 12, `pu_xmsat_global_unobserved_pairs` herb 52 -> ADR 4997: unparseable_explicit_mechanism_path.
- rank 13, `pu_xmsat_global_unobserved_pairs` herb 234 -> ADR 1810: unparseable_explicit_mechanism_path.
- rank 14, `pu_xmsat_global_unobserved_pairs` herb 526 -> ADR 862: unparseable_explicit_mechanism_path.
- rank 15, `pu_xmsat_global_unobserved_pairs` herb 234 -> ADR 862: unparseable_explicit_mechanism_path.
- rank 16, `pu_xmsat_global_unobserved_pairs` herb 483 -> ADR 4535: unparseable_explicit_mechanism_path.
- rank 17, `pu_xmsat_global_unobserved_pairs` herb 483 -> ADR 4363: unparseable_explicit_mechanism_path.
- rank 18, `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2625: unparseable_explicit_mechanism_path.
- rank 19, `pu_xmsat_global_unobserved_pairs` herb 145 -> ADR 1810: unparseable_explicit_mechanism_path.
- rank 20, `pu_xmsat_global_unobserved_pairs` herb 573 -> ADR 2625: unparseable_explicit_mechanism_path.
- rank 21, `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 5965: unparseable_explicit_mechanism_path.

## Case-Level Explanation Examples

- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3989: top `compound:1073;target:7213` drop 0.000018; class `near_zero`.

## Claim Boundary

This batch uses the final PU-XMSAT top-ranking export and an explicit final PU-XMSAT checkpoint. Perturbation sensitivity remains local model sensitivity: it is not causal evidence, not SHAP, not clinical validation, and cannot upgrade evidence grades.
