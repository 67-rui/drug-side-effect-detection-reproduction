#!/usr/bin/env bash
# Paper-aligned fresh retrain after validation/test edge hiding + leakage fixes.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOG="${LOG_DIR:-results/phase8_logs}/paper_retrain.log"
CKPT="${CKPT:-saved_models/best_model_for_prediction.pt}"
mkdir -p results/phase8_logs results
exec > >(tee -a "$LOG") 2>&1

echo "=== Paper retrain started $(date) ==="
echo "Protocol: validation/test-positive graph removal; ML CMM-ADR edge_attr excluded"
echo "Python: $PY"
echo "Downstream checkpoint: $CKPT"

echo "=== Table 2 MSAT 10-fold CV ==="
"$PY" -u train.py 2>&1 | tee results/phase8_logs/paper_retrain_msat.log

echo "=== Table 2 ML baselines (1:1) ==="
"$PY" -u scripts/run_baselines.py --ml 2>&1 | tee results/phase8_logs/paper_retrain_ml.log

echo "=== Table 2 GNN baselines (1:1) ==="
"$PY" -u scripts/run_baselines.py --gnn 2>&1 | tee results/phase8_logs/paper_retrain_gnn.log

echo "=== Table 3 ablation (w/o + only) ==="
"$PY" -u scripts/run_ablation.py --all 2>&1 | tee results/phase8_logs/paper_retrain_ablation_wo.log
"$PY" -u scripts/run_ablation.py --only 2>&1 | tee results/phase8_logs/paper_retrain_ablation_only.log
"$PY" -u scripts/run_ablation.py --aggregate-only 2>&1 | tee results/phase8_logs/paper_retrain_ablation_summary.log

echo "=== Table 4 MSAT 1:10 ==="
"$PY" -u scripts/run_imbalanced.py 2>&1 | tee results/phase8_logs/paper_retrain_neg10.log

echo "=== Table 4 baselines 1:10 ==="
"$PY" -u scripts/run_baselines.py --neg-ratio 10 --all 2>&1 | tee results/phase8_logs/paper_retrain_baselines_neg10.log

echo "=== Fig.6 sweep ==="
"$PY" -u scripts/run_imbalance_sweep.py --all 2>&1 | tee results/phase8_logs/paper_retrain_fig6_msat.log
for ratio in 2 5 10; do
  for model in hgt simple_hgn gat; do
    "$PY" -u scripts/run_imbalance_sweep.py --ratio "$ratio" --model "$model" \
      2>&1 | tee "results/phase8_logs/paper_retrain_fig6_${model}_r${ratio}.log"
  done
done
"$PY" scripts/run_imbalance_sweep.py --aggregate-only

echo "=== Phase 9 paper downstream ==="
CKPT="$CKPT" RUN_FAERS_ONLY_TRAIN=1 RUN_LEGACY_COLDSTART=0 bash scripts/server_phase9_run.sh \
  2>&1 | tee results/phase8_logs/paper_retrain_phase9.log

echo "=== Final artifact audit ==="
"$PY" scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json --fail-on-error \
  2>&1 | tee results/phase8_logs/paper_retrain_audit.log

echo "=== Paper retrain COMPLETE $(date) ==="
