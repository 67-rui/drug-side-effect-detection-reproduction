# PU-XMSAT Batch Mechanism Interpretability

- Candidate source: `final_pu_xmsat_top_predictions`
- Candidate source note: Final PU-XMSAT top-ranking export.
- Checkpoint path: `saved_models/pu_xmsat_formal/pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt`
- Checkpoint is final PU-XMSAT: yes
- Checkpoint context: Final full-positive hybrid PU-XMSAT checkpoint attribution.
- Quantified case count: 20
- Top-prediction candidates checked: 5000
- Top-prediction rows available: 5000
- Requested candidate pool top-K: 5000
- Candidate pool complete: yes
- Candidate pool missing rows: 0
- Coverage-missing top-prediction candidates: 4609
- Unquantified explicit-path candidates: 0
- Cases with explicit mechanism paths: 20
- Near-zero sensitivity cases: 12
- Negative score_drop cases: 0
- Coverage boundary: top-prediction candidates without parseable explicit mechanism paths were counted as coverage-missing, not silently dropped.
- Mechanism coverage by top-K: reported separately so mechanism-supported cases are not treated as representative of all top-ranked predictions.
- Random perturbation controls: available for score-drop context.

Perturbation score drops are local sensitivity signals for mechanism triage; they are not causal effects, not SHAP values, and not external clinical validation.
Negative score_drop is not protective biology; it means the score increased after masking.

## Explicit Mechanism Path Coverage

| Top K | Candidates checked | Explicit-path candidates | Coverage rate |
| ---: | ---: | ---: | ---: |
| 50 | 50 | 1 | 0.020000 |
| 100 | 100 | 8 | 0.080000 |
| 500 | 500 | 31 | 0.062000 |
| 1000 | 1000 | 64 | 0.064000 |
| 5000 | 5000 | 391 | 0.078200 |

## Top Component/Compound Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `compound:761` (Compound #761) | 3 | 0.000309 | 0.000318 | 3 | 0 | 0 |
| 2 | `compound:821` (Compound #821) | 4 | 0.000247 | 0.000313 | 4 | 0 | 0 |
| 3 | `compound:480` (Compound #480) | 5 | 0.000034 | 0.000041 | 0 | 5 | 0 |
| 4 | `compound:1073` (Compound #1073) | 4 | 0.000021 | 0.000028 | 0 | 4 | 0 |
| 5 | `compound:1121` (Compound #1121) | 1 | 0.000011 | 0.000011 | 0 | 1 | 0 |
| 6 | `compound:745` (Compound #745) | 2 | 0.000004 | 0.000005 | 0 | 2 | 0 |
| 7 | `compound:1023` (Compound #1023) | 5 | -0.000003 | 0.000001 | 0 | 5 | 0 |
| 8 | `compound:1243` (Compound #1243) | 3 | -0.000004 | 0.000001 | 0 | 3 | 0 |
| 9 | `compound:132` (Compound #132) | 1 | 0.000000 | 0.000000 | 0 | 1 | 0 |
| 10 | `compound:1257` (Compound #1257) | 2 | 0.000000 | 0.000000 | 0 | 2 | 0 |

## Top Target Contributions

| Rank | Feature | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` (Target #15721) | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `target:15692` (Target #15692) | 2 | 0.000052 | 0.000102 | 1 | 1 | 0 |
| 3 | `target:1782` (Target #1782) | 1 | 0.000096 | 0.000096 | 0 | 1 | 0 |
| 4 | `target:7213` (Target #7213) | 5 | 0.000005 | 0.000014 | 0 | 5 | 0 |
| 5 | `target:19496` (Target #19496) | 1 | 0.000007 | 0.000007 | 0 | 1 | 0 |
| 6 | `target:2432` (Target #2432) | 3 | 0.000004 | 0.000006 | 0 | 3 | 0 |
| 7 | `target:2586` (Target #2586) | 4 | 0.000002 | 0.000005 | 0 | 4 | 0 |
| 8 | `target:1933` (Target #1933) | 1 | 0.000005 | 0.000005 | 0 | 1 | 0 |
| 9 | `target:11486` (Target #11486) | 3 | 0.000005 | 0.000005 | 0 | 3 | 0 |
| 10 | `target:1774` (Target #1774) | 3 | 0.000003 | 0.000005 | 0 | 3 | 0 |

## Top Pathway/Path Contributions

| Rank | Path features | Cases | Mean drop | Max drop | Positive | Near-zero | Negative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `target:15721` (Target #15721) | 1 | 0.001174 | 0.001174 | 1 | 0 | 0 |
| 2 | `compound:821;target:11486` (Compound #821;Target #11486) | 1 | 0.000320 | 0.000320 | 1 | 0 | 0 |
| 3 | `compound:761;target:7802` (Compound #761;Target #7802) | 2 | 0.000314 | 0.000318 | 2 | 0 | 0 |
| 4 | `compound:821;target:469` (Compound #821;Target #469) | 1 | 0.000315 | 0.000315 | 1 | 0 | 0 |
| 5 | `compound:761;target:2432` (Compound #761;Target #2432) | 1 | 0.000310 | 0.000310 | 1 | 0 | 0 |
| 6 | `compound:761;target:19336` (Compound #761;Target #19336) | 1 | 0.000300 | 0.000300 | 1 | 0 | 0 |
| 7 | `compound:821;target:19336` (Compound #821;Target #19336) | 1 | 0.000263 | 0.000263 | 1 | 0 | 0 |
| 8 | `compound:821;target:2586` (Compound #821;Target #2586) | 2 | 0.000210 | 0.000214 | 2 | 0 | 0 |
| 9 | `compound:821;target:1774` (Compound #821;Target #1774) | 1 | 0.000214 | 0.000214 | 1 | 0 | 0 |
| 10 | `compound:1073;target:15692` (Compound #1073;Target #15692) | 1 | 0.000124 | 0.000124 | 1 | 0 | 0 |

## Near-Zero Sensitivity Cases

- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3989
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 24
- `pu_xmsat_global_unobserved_pairs` herb 500 -> ADR 3989
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2453
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 3387
- `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 4997
- `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 3989
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2540
- `pu_xmsat_global_unobserved_pairs` herb 500 -> ADR 5468
- `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 1810
- `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 2095
- `pu_xmsat_global_unobserved_pairs` herb 618 -> ADR 4759

## Negative score_drop Cases

- none

## Random Perturbation Controls

| Group | Count | Mean drop | Max drop |
| --- | ---: | ---: | ---: |
| component | 100 | 0.000000 | 0.000000 |
| pathway | 86 | 0.000000 | 0.000030 |
| target | 100 | 0.000000 | 0.000001 |

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
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 2481: top `compound:1073;target:15692` drop 0.000124; class `positive`.
- `pu_xmsat_global_unobserved_pairs` herb 495 -> ADR 3989: top `compound:821;target:2586` drop 0.000214; class `positive`.
- `pu_xmsat_global_unobserved_pairs` herb 237 -> ADR 24: top `compound:745;target:19336` drop 0.000003; class `near_zero`.
- `pu_xmsat_global_unobserved_pairs` herb 500 -> ADR 3989: top `target:7213` drop 0.000001; class `near_zero`.

## Claim Boundary

This batch uses the final PU-XMSAT top-ranking export and an explicit final PU-XMSAT checkpoint. Perturbation sensitivity remains local model sensitivity: it is not causal evidence, not SHAP, not clinical validation, and cannot upgrade evidence grades.
