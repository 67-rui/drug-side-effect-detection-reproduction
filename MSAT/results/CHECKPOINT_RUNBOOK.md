# Checkpoint Runbook

Last updated: 2026-06-23

## Problem

Earlier scripts wrote multiple experiment families to the same file:

```text
saved_models/best_model_for_prediction.pt
```

This means the final local checkpoint may have come from the main Table 2 run, the 1:10 run, ablation, or Fig.6. Current code prevents future tagged runs from overwriting the main predictor checkpoint, but existing server files still need audit.

## Current Naming

| Run type | Checkpoint |
| --- | --- |
| Main Table 2 run | `saved_models/best_model_for_prediction.pt` |
| Tagged run, e.g. Fig.6 `testneg10` | `saved_models/best_model_for_prediction_testneg10.pt` |
| Fold checkpoints | `saved_models/best_model_fold{fold}.pt` |

## How To Restore A Clean Main Predictor

Preferred route:

```bash
cd /root/autodl-tmp/MSAT
git pull
PY=/root/miniconda3/bin/python
$PY -u train.py
```

This regenerates `results/summary.json` and `saved_models/best_model_for_prediction.pt` from the main Table 2 protocol.

If retraining is unavailable but a trusted main-run checkpoint exists, copy it explicitly:

```bash
cp saved_models/<trusted-main-checkpoint>.pt saved_models/best_model_for_prediction.pt
```

Then regenerate downstream artifacts:

```bash
PY=/root/miniconda3/bin/python bash scripts/rerun_after_artifact_fix.sh
```

## How To Verify A Downstream Artifact

Inspect the JSON for provenance:

```bash
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json
```

A citable downstream artifact should not be stale and should include:

- `checkpoint.path`
- `checkpoint.sha256`
- `checkpoint.size_bytes`
- `checkpoint.mtime`

For OOF Table 5 mode, it should include `input_summary` instead of `checkpoint`.

## Do Not Cite

Do not cite downstream artifacts if:

- `artifact_status.stale` is `true`
- `checkpoint` is missing for predictor-mode outputs
- `input_summary` is missing for OOF outputs
- `audit_reproduction_state.py` reports `stale_artifact` or `missing_provenance`
