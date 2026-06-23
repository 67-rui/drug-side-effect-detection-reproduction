#!/usr/bin/env bash
# Phase 8 GPU experiment runbook — execute on remote server from MSAT repo root.
set -euo pipefail

cd "$(dirname "$0")/.."
LOG_DIR="${LOG_DIR:-results/phase8_logs}"
mkdir -p "$LOG_DIR"

echo "=== Phase 8B: Table 3 Only ablation ==="
python -u scripts/run_ablation.py --only 2>&1 | tee "$LOG_DIR/ablation_only.log"

echo "=== Phase 8C: Table 4 baselines @ 1:10 ==="
python -u scripts/run_baselines.py --neg-ratio 10 --all 2>&1 | tee "$LOG_DIR/baselines_neg10.log"

echo "=== Phase 8D: Fig.6 MSAT sweep (train 1:1, test 1:R) ==="
python -u scripts/run_imbalance_sweep.py --all 2>&1 | tee "$LOG_DIR/fig6_msat.log"

for ratio in 2 5 10; do
  for model in hgt simple_hgn gat; do
    echo "=== Fig.6 $model testneg=$ratio ==="
    python -u scripts/run_imbalance_sweep.py --ratio "$ratio" --model "$model" \
      2>&1 | tee "$LOG_DIR/fig6_${model}_r${ratio}.log"
  done
done

python scripts/run_imbalance_sweep.py --aggregate-only

echo "=== Done. Pull results/*.json and $LOG_DIR back to local ==="
