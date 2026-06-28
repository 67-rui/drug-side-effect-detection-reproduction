# PU-XMSAT Causal Bias Framework

**Date:** 2026-06-28  
**Purpose:** Provide a conservative causal-graph and bias framework for the PU-XMSAT manuscript. This file responds to the causal-graph direction in the research proposal without overstating causal identification from the current data.

## Position

The current project should not claim strict causal effects. The available data support a causal-bias analysis layer, not causal effect estimation.

PU-XMSAT can reduce one important source of modeling bias: treating unobserved CMM-ADR pairs as confirmed negatives. It does not, by itself, remove confounding from co-medication, indication, reporting behavior, exposure population, dose, preparation quality, or database curation.

## Conceptual DAG

```text
CMM exposure / formula use
        |
        v
bioactive ingredients -> targets / pathways -> true ADR risk
        |                       ^
        v                       |
predicted mechanism score        |
                                |
indication / disease -----------+
co-medication ------------------+
dose / preparation quality -----+
population exposure ------------+
reporting propensity -----------> observed FAERS / literature report
database curation --------------> observed CMM-ADR label
```

## Bias Sources and Current Handling

| Bias source | How it can affect CMM-ADR prediction | Current evidence in project | Current handling | Claim boundary |
| --- | --- | --- | --- | --- |
| Incomplete labels | Unobserved pairs may include undiscovered positives | Core issue motivating PU-XMSAT | Reliable negatives, unlabeled pairs, weighted PU BCE | Can claim incomplete-label mitigation, not true negative certainty |
| Co-medication | ADR may be caused by another medicine used together | Not available in current graph | Listed as unobserved confounder | Cannot estimate or adjust co-medication effects |
| Indication bias | Disease being treated may itself relate to ADR | Partially represented by disease-related graph structure, not patient-level indication | Mechanism paths may include disease context when present | Cannot separate disease effect from CMM effect |
| Reporting bias | More commonly reported herbs/ADRs may be overrepresented | FAERS-informed labels and literature records are reporting-dependent | Evidence grading separates prediction from external support | Cannot interpret prediction score as incidence or reporting-corrected risk |
| Exposure population | Rarely used herbs may have sparse observed ADRs | No population denominator | Frequency/degree awareness in candidate scoring | Cannot compare absolute clinical risk across herbs |
| Dose and preparation quality | Toxicity may depend on dose, processing, or product quality | Not available in current graph | Treated as limitation | Cannot make dose-specific safety claims |
| Database curation | Labels depend on source coverage and mapping rules | Table 5/6 reproduction gap demonstrates this risk | Reproduction audit and claim boundaries | Cannot use missing database support as proof of no association |

## What PU-XMSAT Changes

PU-XMSAT changes the supervision assumption:

```text
original MSAT:
observed positive vs sampled unobserved-as-negative

PU-XMSAT:
observed positive vs reliable negative vs down-weighted unlabeled
```

This makes the model less dependent on the strong assumption that every unobserved pair is negative. It is a label-noise and incomplete-label improvement, not a causal adjustment method.

## How to Use This in the Manuscript

Recommended wording:

> We used a causal-bias framework to clarify the interpretation of PU-XMSAT outputs. The proposed PU training strategy addresses incomplete-label bias by separating observed positives, reliable negatives, and unlabeled pairs. However, the available graph data do not include patient-level co-medication, indication, exposure denominator, dose, or reporting propensity, so the model outputs should be interpreted as pharmacovigilance risk signals rather than causal effect estimates.

Avoid:

- Do not claim that PU-XMSAT proves a CMM causes an ADR.
- Do not claim that perturbation score drops are causal effects.
- Do not claim that evidence Grade D means no real association exists.
- Do not claim that the current dataset controls co-medication or indication bias.

## Future Data Needed for Causal Estimation

Strict causal modeling would require additional variables:

1. patient-level CMM exposure and timing;
2. co-medication records;
3. indication or diagnosis before exposure;
4. ADR onset time;
5. dose, preparation, and duration;
6. exposure population denominator;
7. reporting source and reporting propensity indicators.

If these become available, the next methods to consider are propensity score adjustment, inverse probability weighting, stratified analysis by indication, and causal representation learning constrained by a pre-specified DAG.

## Current Project Status

This causal-bias framework completes the current-stage causal requirement in the proposal at the discussion and claim-boundary level. It does not add a causal estimator, because the current data do not support one without making stronger assumptions than the evidence allows.
