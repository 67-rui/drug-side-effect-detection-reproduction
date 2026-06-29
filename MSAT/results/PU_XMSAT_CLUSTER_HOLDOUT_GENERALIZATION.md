# PU-XMSAT Cluster-Held-Out Generalization

- Fold count: 10
- Claim boundary: Cluster-held-out evaluation probes generalization to held-out herb/CMM clusters; it is not external clinical validation, causal transportability, or evidence that all unobserved pairs are true negatives.
- Heldout herbs filtered from PU training: yes
- Eval positive CMM-ADR edges hidden: yes
- Mechanism edges retained: yes
- Tiny heldout clusters (<5 herbs): 3
- Heldout herb count range: 1 to 207

## Interpretation Caveats

- 3 tiny heldout clusters have fewer than 5 herbs; macro mean metrics should be read together with fold-level cluster sizes.
- Thresholded F1 is low under cluster-held-out evaluation; this supports a harder generalization setting rather than a simple success claim.

## Mean Metrics

| Metric | Mean |
| --- | ---: |
| AUC | 0.889069 |
| AUPRC | 0.903219 |
| F1 | 0.176976 |
| MCC | 0.191914 |

## Fold Summary

| Fold | Holdout cluster | Heldout herbs | Test positives | Hidden eval positives | AUC | AUPRC | F1 | MCC |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 207 | 14977 | 14977 | 0.808161 | 0.830212 | 0.098053 | 0.157502 |
| 1 | 1 | 1 | 9 | 9 | 0.987654 | 0.988889 | 0.500000 | 0.447214 |
| 2 | 2 | 1 | 5 | 5 | 1.000000 | 1.000000 | 0.750000 | 0.654654 |
| 3 | 3 | 1 | 5 | 5 | 1.000000 | 1.000000 | 0.000000 | 0.000000 |
| 4 | 4 | 20 | 213 | 213 | 0.891490 | 0.911725 | 0.000000 | 0.000000 |
| 5 | 5 | 65 | 107 | 107 | 0.882435 | 0.901068 | 0.170940 | 0.221404 |
| 6 | 6 | 33 | 937 | 937 | 0.850245 | 0.871114 | 0.041797 | 0.103863 |
| 7 | 7 | 71 | 3294 | 3294 | 0.862943 | 0.875762 | 0.184920 | 0.227787 |
| 8 | 8 | 112 | 4186 | 4186 | 0.808398 | 0.830461 | 0.006192 | 0.039436 |
| 9 | 9 | 140 | 3329 | 3329 | 0.799364 | 0.822962 | 0.017862 | 0.067277 |
