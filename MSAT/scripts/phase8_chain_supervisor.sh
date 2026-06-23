#!/usr/bin/env bash
# Wait for Phase 8B (only ablation), then run 8C + 8D automatically.
set -euo pipefail

MSAT_ROOT="${MSAT_ROOT:-/root/autodl-tmp/MSAT}"
PYTHON="${PYTHON:-/root/miniconda3/bin/python}"
LOG_DIR="$MSAT_ROOT/results/phase8_logs"
mkdir -p "$LOG_DIR"
cd "$MSAT_ROOT"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/supervisor.log"; }

wait_for_ablation() {
  log "Waiting for run_ablation.py --only to finish..."
  while pgrep -f "scripts/run_ablation.py --only" >/dev/null 2>&1; do
    tail -1 "$LOG_DIR/ablation_only.log" 2>/dev/null | tee -a "$LOG_DIR/supervisor.log" || true
    sleep 120
  done
  for f in summary_only_esa.json summary_only_hsp.json summary_only_hci.json; do
    if [[ ! -f "$MSAT_ROOT/results/$f" ]]; then
      log "WARN: missing results/$f after ablation exit"
    else
      log "OK: results/$f"
    fi
  done
  "$PYTHON" scripts/run_ablation.py --aggregate-only 2>&1 | tee -a "$LOG_DIR/supervisor.log"
}

run_8c() {
  log "=== Phase 8C: Table 4 baselines @ 1:10 ==="
  "$PYTHON" -u scripts/run_baselines.py --neg-ratio 10 --all 2>&1 | tee "$LOG_DIR/baselines_neg10.log"
}

run_8d() {
  log "=== Phase 8D: Fig.6 MSAT sweep ==="
  "$PYTHON" -u scripts/run_imbalance_sweep.py --all 2>&1 | tee "$LOG_DIR/fig6_msat.log"
  for ratio in 2 5 10; do
    for model in hgt simple_hgn gat; do
      log "Fig.6 $model testneg=$ratio"
      "$PYTHON" -u scripts/run_imbalance_sweep.py --ratio "$ratio" --model "$model" \
        2>&1 | tee "$LOG_DIR/fig6_${model}_r${ratio}.log"
    done
  done
  "$PYTHON" scripts/run_imbalance_sweep.py --aggregate-only | tee -a "$LOG_DIR/supervisor.log"
}

log "Phase 8 supervisor started (PID $$)"
wait_for_ablation
run_8c
run_8d
log "Phase 8 GPU chain COMPLETE"
