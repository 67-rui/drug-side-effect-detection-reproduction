# PU-XMSAT Cluster-Held-Out Generalization

- Fold count: 1
- Claim boundary: Cluster-held-out evaluation probes generalization to held-out herb/CMM clusters; it is not external clinical validation, causal transportability, or evidence that all unobserved pairs are true negatives.
- Heldout herbs filtered from PU training: yes
- Eval positive CMM-ADR edges hidden: yes
- Mechanism edges retained: yes

## Mean Metrics

| Metric | Mean |
| --- | ---: |
| AUC | 0.633572 |
| AUPRC | 0.628962 |
| F1 | 0.569064 |
| MCC | 0.195043 |

## Fold Summary

| Fold | Holdout cluster | Heldout herbs | Test positives | Hidden eval positives | AUC | AUPRC | F1 | MCC |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 207 | 14977 | 14977 | 0.633572 | 0.628962 | 0.569064 | 0.195043 |
