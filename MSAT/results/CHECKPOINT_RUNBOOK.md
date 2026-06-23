# Checkpoint Runbook

Last updated: 2026-06-23

## Problem

Earlier scripts wrote multiple experiment families to the same file:

```text
saved_models/best_model_for_prediction.pt
```

This means the final local checkpoint may have come from the main Table 2 run, the 1:10 run, ablation, or Fig.6. Current code prevents future tagged runs from overwriting the main predictor checkpoint and tagged fold checkpoints, but existing server files still need audit.

The prediction checkpoint is now selected by validation AUC (`best_val_auc`), not by test AUC. Any checkpoint selected by the older test-AUC rule should be treated as stale for downstream deployment-style Table 5 or case-study use.

## Current Naming

| Run type | Checkpoint |
| --- | --- |
| Main Table 2 run | `saved_models/best_model_for_prediction.pt` |
| Tagged run, e.g. Fig.6 `testneg10` | `saved_models/best_model_for_prediction_testneg10.pt` |
| Main fold checkpoints | `saved_models/best_model_fold{fold}.pt` |
| Tagged fold checkpoints | `saved_models/best_model_fold{fold}_{tag}.pt` |

## How To Restore A Clean Main Predictor

Preferred route:

```bash
cd /root/autodl-tmp/MSAT
git pull
PY=/root/miniconda3/bin/python
$PY -u train.py
```

This regenerates `results/summary.json` and `saved_models/best_model_for_prediction.pt` from the corrected main Table 2 protocol. The corrected protocol removes validation and test positive CMM-ADR edges from the message-passing graph before early stopping, threshold selection, and test evaluation.

If retraining is unavailable but a trusted main-run checkpoint exists, copy it explicitly:

```bash
cp saved_models/<trusted-main-checkpoint>.pt saved_models/best_model_for_prediction.pt
```

Then regenerate downstream artifacts with an explicit checkpoint:

```bash
CKPT=saved_models/best_model_for_prediction.pt PY=/root/miniconda3/bin/python bash scripts/server_phase9_run.sh
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error
```

For a full paper-table refresh after the protocol fix, prefer:

```bash
PY=/root/miniconda3/bin/python bash scripts/server_paper_retrain.sh
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
