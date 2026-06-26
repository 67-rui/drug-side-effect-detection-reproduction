#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PY="${PY:-python}"
PU_XMSAT_BACKEND="${PU_XMSAT_BACKEND:-full_msat_pu}"
PU_XMSAT_SAMPLING_STRATEGY="${PU_XMSAT_SAMPLING_STRATEGY:-hybrid}"
PU_XMSAT_UNLABELED_WEIGHT="${PU_XMSAT_UNLABELED_WEIGHT:-0.2}"
PU_XMSAT_RELIABLE_NEGATIVE_WEIGHT="${PU_XMSAT_RELIABLE_NEGATIVE_WEIGHT:-0.8}"
PU_XMSAT_MAX_FOLDS="${PU_XMSAT_MAX_FOLDS:-1}"
PU_XMSAT_MAX_EPOCHS="${PU_XMSAT_MAX_EPOCHS:-5}"
PU_XMSAT_MAX_PAIRS="${PU_XMSAT_MAX_PAIRS:-384}"
PU_XMSAT_OUTPUT="${PU_XMSAT_OUTPUT:-results/pu_training_summary.json}"

mkdir -p results/phase_pu_xmsat_logs

"$PY" scripts/verify_pu_xmsat_baseline.py

"$PY" experiments/run_pu_msat_experiment.py \
  --backend "$PU_XMSAT_BACKEND" \
  --sampling-strategy "$PU_XMSAT_SAMPLING_STRATEGY" \
  --unlabeled-weight "$PU_XMSAT_UNLABELED_WEIGHT" \
  --reliable-negative-weight "$PU_XMSAT_RELIABLE_NEGATIVE_WEIGHT" \
  --max-folds "$PU_XMSAT_MAX_FOLDS" \
  --max-epochs "$PU_XMSAT_MAX_EPOCHS" \
  --max-pairs "$PU_XMSAT_MAX_PAIRS" \
  --output "$PU_XMSAT_OUTPUT" \
  2>&1 | tee results/phase_pu_xmsat_logs/pu_training.log

"$PY" scripts/run_explanation_case_study.py \
  --output results/explanation_case_studies.json

"$PY" scripts/build_evidence_screening_table.py \
  --output-json results/evidence_screening_summary.json \
  --output-csv results/evidence_screening_table.csv

"$PY" scripts/summarize_pu_xmsat_results.py \
  --pu "$PU_XMSAT_OUTPUT" \
  --output results/PU_XMSAT_EXPERIMENT_REPORT.md
