# PU-XMSAT Baseline Lock

**Locked date:** 2026-06-26
**Baseline branch:** `codex/fix-reproduction-protocol`
**Baseline tag:** `baseline/msat-reproduction-20260626`
**Development branch:** `codex/pu-xmsat-implementation`

## Baseline Metrics

| File | Meaning | Key result |
| --- | --- | --- |
| `results/summary.json` | Table 2 MSAT 1:1 | AUC 0.9793, AUPRC 0.9771, F1 0.9315, MCC 0.8625 |
| `results/baseline_summary.json` | Table 2 baselines | MSAT AUC highest |
| `results/summary_neg10.json` | Table 4 MSAT 1:10 | AUC 0.8710, F1 0.5604, MCC 0.5180 |
| `results/faers_only_coldstart_summary.json` | Fig.5a | MSAT beats GAT/HGT/Simple-HGN on Precision, MCC, AUC |
| `results/table5_summary.json` | Table 5 candidate validation | Current support 1/15; not paper-equivalent reproduction |

## Allowed Changes

New PU-XMSAT work may add files under `experiments/`, `inference/`, `scripts/`, `tests/`, and `results/`.

The first implementation round must not change the default behavior of:

- `train.py`
- `model.py`
- `experiments/feature_extractor.py`
- existing result JSON files used as the baseline

## Reporting Rule

The original MSAT baseline remains the comparison anchor. PU-XMSAT results must be written to new files whose names begin with `pu_` or `PU_XMSAT_`.
