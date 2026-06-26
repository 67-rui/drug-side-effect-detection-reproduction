# PU-XMSAT Full MSAT Pilot Report

**Date:** 2026-06-26  
**Server:** AutoDL RTX 5090 32GB  
**Backend:** `full_msat_pu`  
**Fold:** 0  
**Sampling strategy:** hybrid  
**Weights:** positive `1.0`, reliable negative `0.8`, unlabeled `0.2`  
**Protocol guardrail:** baseline verifier passed before each run.

## Pilot Results

| Run | PU pairs | Epochs | Best epoch | Best val AUC | Test AUC | Test AUPRC | Test F1 | Test MCC | Final loss | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fold0_50e_384p` | 384 | 50 | 50 | 0.8536 | 0.8497 | 0.8402 | 0.6605 | 0.1234 | 0.0000647 | 27.7s |
| `fold0_100e_768p` | 768 | 100 | 100 | 0.8693 | 0.8643 | 0.8511 | 0.6543 | 0.0441 | 0.0000259 | 52.3s |
| `fold0_200e_1536p` | 1536 | 200 | 200 | 0.8878 | 0.8855 | 0.8745 | 0.6551 | 0.0607 | 0.0000184 | 101.9s |

## Interpretation

The full MSAT PU backend is now operational on GPU. AUC and AUPRC improve as epochs and PU pair count increase, and the best validation AUC occurs at the final epoch for all three runs. This suggests the pilot has not yet reached a clear plateau.

Threshold-dependent metrics need care. Recall is nearly 1.0 at the fixed `0.5` threshold, while precision and MCC remain weak. Before a formal 10-fold run, the PU runner should support validation-threshold calibration for F1/MCC reporting, while keeping AUC/AUPRC as the primary threshold-free metrics.

## Recommendation

Do not start a 10-fold formal run yet. First add a PU-specific validation threshold option, then run a fold0 comparison across `hybrid`, `low_score`, and `random` with the same epoch/pair budget. If `hybrid` remains strongest and AUC/AUPRC continue improving, proceed to a bounded 10-fold pilot.

## Raw Artifacts

The raw JSON summaries are available locally and on the server but are ignored by git to avoid result-artifact pollution:

- `results/pu_training_summary_fold0_50e_384p.json`
- `results/pu_training_summary_fold0_100e_768p.json`
- `results/pu_training_summary_fold0_200e_1536p.json`

