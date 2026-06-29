# PU-XMSAT Publication Evidence Consolidation

- Claim boundary: PU-XMSAT evidence supports incomplete-label mitigation and risk-prioritization under the reproduced MSAT protocol; it is not causal validation, clinical confirmation, or proof that unobserved pairs are true negatives.
- Supported metrics: auc, auprc, f1, mcc
- Ablation runs consolidated: 1
- Seed robustness max spread: 0.000297
- Weight sensitivity runs consolidated: 3

## Baseline

| Metric | Mean |
| --- | ---: |
| AUC | 0.979271 |
| AUPRC | 0.977095 |
| F1 | 0.931451 |
| MCC | 0.862520 |

## Main PU-XMSAT Runs

| Run | Metric | Mean | Delta vs baseline |
| --- | --- | ---: | ---: |
| hybrid_seed2026 | AUC | 0.980420 | +0.001149 |
| hybrid_seed2026 | AUPRC | 0.977929 | +0.000834 |
| hybrid_seed2026 | F1 | 0.935064 | +0.003613 |
| hybrid_seed2026 | MCC | 0.868409 | +0.005889 |
| hybrid_seed1337 | AUC | 0.980392 | +0.001121 |
| hybrid_seed1337 | AUPRC | 0.977983 | +0.000888 |
| hybrid_seed1337 | F1 | 0.934767 | +0.003316 |
| hybrid_seed1337 | MCC | 0.868331 | +0.005811 |
