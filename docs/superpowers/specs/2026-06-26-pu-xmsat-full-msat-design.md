# PU-XMSAT Full MSAT Backend Design

## Context

The PU-XMSAT prototype currently has a complete local and server smoke loop, but the training backend is `weighted_embedding_smoke`. It verifies PU pair construction, reliable negative sampling, sample weights, reporting, and server environment setup. It does not train the paper-aligned `MSATTCMFSFinal` GNN, so it cannot support a claim that PU-XMSAT improves the reproduced MSAT main experiment.

The reproduction baseline remains frozen:

- Baseline branch: `codex/fix-reproduction-protocol`
- Baseline tag: `baseline/msat-reproduction-20260626`
- Development branch: `codex/pu-xmsat-implementation`
- Protocol version: `2026-06-23-val-test-edge-hidden`

## Goal

Add a `full_msat_pu` backend that trains the real `MSATTCMFSFinal` model on PU-weighted CMM-ADR pairs while preserving the default MSAT reproduction behavior and all baseline artifacts.

## Non-Goals

- Do not change default `MSAT/train.py` behavior.
- Do not overwrite `results/summary.json`, `results/table5_summary.json`, or baseline checkpoints.
- Do not claim PU-XMSAT outperforms MSAT until full GNN metrics are generated and compared.
- Do not add new dependencies beyond the current project stack.
- Do not replace the existing `weighted_embedding_smoke` backend; it remains the fast environment smoke test.

## Architecture

The upgrade adds a separate full-training module under `MSAT/experiments/` and wires it into `MSAT/experiments/run_pu_msat_experiment.py` behind a `--backend` argument.

`weighted_embedding_smoke` continues to use the lightweight pair-embedding scorer and logits-based weighted PU BCE. `full_msat_pu` uses `MSATTCMFSFinal`, the existing `FeatureExtractor`, the paper-aligned validation/test edge hiding rules, and PU sample weights. It writes independent PU outputs and optional PU-specific checkpoints.

## Components

### Probability-Safe PU Loss

`MSATTCMFSFinal.forward()` returns sigmoid probabilities, not raw logits. The existing `weighted_pu_bce_loss()` expects logits and must remain available for the smoke backend. The full backend therefore needs a probability-safe weighted BCE helper that clamps probabilities and applies sample weights without a second sigmoid transform.

### Full MSAT PU Training Module

Create `MSAT/experiments/full_msat_pu_training.py` with focused helpers:

- build validation/train split from official fold data using the same seed convention as `train.py`;
- build PU arrays for training pairs only;
- remove validation/test positive CMM-ADR edges from the message-passing graph;
- initialize `MSATTCMFSFinal` with existing model config;
- train with sample-weighted probability BCE;
- evaluate on validation and official test data using existing metrics;
- return per-fold metrics, predictions, loss history, protocol metadata, and optional PU checkpoint path.

The module may import stable helper functions from `train.py` such as `_evaluation_positive_pair_set`, `_remove_cmm_adr_pairs`, `evaluate`, `find_optimal_threshold`, `prediction_payload`, and `_state_dict_to_cpu`. It must not call `run_10fold_cv()` or alter global training defaults.

### Runner CLI

Extend `run_pu_msat_experiment.py`:

- add `--backend {weighted_embedding_smoke,full_msat_pu}`;
- keep the default backend as `weighted_embedding_smoke`;
- use `full_msat_pu` only when explicitly requested;
- keep output default configurable and independent from baseline files;
- include backend, fold count, epoch count, loss, metrics, runtime, and protocol metadata in `pu_training_summary.json`.

### Server Script

Make `server_pu_xmsat_run.sh` environment-configurable and safe for pilot runs:

- `PU_XMSAT_BACKEND`, default `full_msat_pu`;
- `PU_XMSAT_MAX_FOLDS`, default `1`;
- `PU_XMSAT_MAX_EPOCHS`, default `5`;
- `PU_XMSAT_MAX_PAIRS`, default `384`;
- `PU_XMSAT_OUTPUT`, default `results/pu_training_summary.json`.

These defaults are intentionally pilot-sized. Full 10-fold training should be launched by overriding environment variables after the pilot passes.

### Report And Verification

The report summarizer should read `results/pu_training_summary.json` when present and state whether the backend is smoke or full MSAT. The final verifier should accept the existing smoke artifacts and optionally report full backend metrics if `pu_training_summary.json` exists.

## Data Flow

1. Load the official heterogeneous graph and official fold split.
2. Split the fold development data into train and validation using `TrainingConfig.TRAIN_VAL_SPLIT` and `TrainingConfig.RANDOM_STATE + fold_idx`.
3. Hide validation/test positive CMM-ADR edges from message passing.
4. Build PU training arrays from train positives, reliable negatives, and unlabeled pairs.
5. Train `MSATTCMFSFinal` with weighted probability BCE.
6. Select the best epoch by validation AUC.
7. Evaluate the selected model on the official test pairs.
8. Write independent PU results and report artifacts.

## Testing Strategy

Use TDD and keep tests lightweight:

- unit test probability-safe weighted BCE;
- unit test that full backend config records `training_backend: full_msat_pu`;
- unit test that the weighted full training step uses probability outputs and backpropagates;
- unit test that runner CLI backend selection dispatches correctly without starting full graph training;
- unit test that server script uses safe pilot defaults and never references baseline output paths before PU output paths;
- final verification with full test suite, baseline verifier, and final PU verifier.

The first real GNN execution should be a pilot:

```bash
python experiments/run_pu_msat_experiment.py \
  --backend full_msat_pu \
  --sampling-strategy hybrid \
  --max-folds 1 \
  --max-epochs 1 \
  --max-pairs 96 \
  --output /tmp/pu_xmsat_full_msat_pilot.json
```

If the pilot is too slow locally, run it on the AutoDL RTX 5090 server before attempting longer training.

## Success Criteria

- Existing smoke backend still passes unchanged tests.
- New `full_msat_pu` backend can execute at least one fold and one epoch with finite loss and finite validation/test metrics.
- Default MSAT training behavior remains unchanged.
- Baseline verifier remains `ok: true`.
- Final verifier remains `ok: true`.
- Server script defaults to a bounded full-backend pilot, not an accidental 10-fold long run.

