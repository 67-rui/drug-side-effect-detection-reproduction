#!/usr/bin/env bash
# Resume/fresh paper retrain. Defaults to rerun because pre-fix outputs are stale.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOG="${LOG_DIR:-results/phase8_logs}/paper_retrain_resume.log"
FORCE_RERUN="${FORCE_RERUN:-1}"
mkdir -p results/phase8_logs results
exec > >(tee -a "$LOG") 2>&1

echo "=== Paper retrain RESUME $(date) ==="
echo "FORCE_RERUN=$FORCE_RERUN"

run_if_missing() {
  local marker="$1"
  shift
  if [[ "$FORCE_RERUN" != "1" && -f "$marker" ]]; then
    echo "[SKIP] $marker exists"
  else
    echo "[RUN] $*"
    "$@"
  fi
}

run_if_missing results/summary.json \
  "$PY" -u train.py

run_if_missing results/baseline_lr.json \
  "$PY" -u scripts/run_baselines.py --ml

run_if_missing results/baseline_gcn.json \
  "$PY" -u scripts/run_baselines.py --gnn

if [[ "$FORCE_RERUN" != "1" && -f results/ablation_summary.json ]]; then
  echo "[SKIP] results/ablation_summary.json exists"
else
  "$PY" -u scripts/run_ablation.py --all
  "$PY" -u scripts/run_ablation.py --only
  "$PY" -u scripts/run_ablation.py --aggregate-only
fi

run_if_missing results/summary_neg10.json \
  "$PY" -u scripts/run_imbalanced.py

echo "=== Table 4 baselines 1:10 (per-model, skip if json exists) ==="
for model in lr rf xgb gcn gat rgcn hgt hetnn simple_hgn; do
  out="results/baseline_${model}_neg10.json"
  if [[ "$FORCE_RERUN" != "1" && -f "$out" ]]; then
    echo "[SKIP] $out"
  else
    echo "[RUN] neg10 $model"
    "$PY" -u scripts/run_baselines.py --neg-ratio 10 --model "$model"
  fi
done
"$PY" -u scripts/run_baselines.py --neg-ratio 10 --aggregate-only

run_if_missing results/summary_testneg10.json \
  "$PY" -u scripts/run_imbalance_sweep.py --all

for ratio in 2 5 10; do
  for model in hgt simple_hgn gat; do
    log="results/phase8_logs/paper_retrain_fig6_${model}_r${ratio}.log"
    if [[ "$FORCE_RERUN" != "1" && -f "$log" ]] && grep -q SAVED "$log" 2>/dev/null; then
      echo "[SKIP] fig6 $model r$ratio"
    else
      "$PY" -u scripts/run_imbalance_sweep.py --ratio "$ratio" --model "$model"
    fi
  done
done
"$PY" scripts/run_imbalance_sweep.py --aggregate-only 2>/dev/null || true

echo "=== Phase 9 (skip FAERS-only if summary exists) ==="
export RUN_LEGACY_COLDSTART=0
if [[ -f results/faers_only_coldstart_summary.json ]]; then
  export RUN_FAERS_ONLY_TRAIN=0
  echo "[SKIP] FAERS-only Fig.5a (existing faers_only_coldstart_summary.json)"
else
  export RUN_FAERS_ONLY_TRAIN=1
fi
bash scripts/server_phase9_run.sh

"$PY" scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error

echo "=== Paper retrain RESUME COMPLETE $(date) ==="
