#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PY="${PY:-python}"
mkdir -p results/phase_pu_xmsat_logs

"$PY" scripts/verify_pu_xmsat_baseline.py

"$PY" experiments/run_pu_msat_experiment.py \
  --sampling-strategy hybrid \
  --unlabeled-weight 0.2 \
  --reliable-negative-weight 0.8 \
  --max-folds 10 \
  --max-epochs 1000 \
  --output results/pu_training_summary.json \
  2>&1 | tee results/phase_pu_xmsat_logs/pu_training.log

"$PY" scripts/run_explanation_case_study.py \
  --output results/explanation_case_studies.json

"$PY" scripts/build_evidence_screening_table.py \
  --output-json results/evidence_screening_summary.json \
  --output-csv results/evidence_screening_table.csv

"$PY" scripts/summarize_pu_xmsat_results.py \
  --output results/PU_XMSAT_EXPERIMENT_REPORT.md
