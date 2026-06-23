#!/usr/bin/env bash
# Paper-aligned retrain after §3.5.1 inductive fix + ML edge features (§3.5.2)
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOG="${LOG_DIR:-results/phase8_logs}/paper_retrain.log"
mkdir -p results/phase8_logs results
exec > >(tee -a "$LOG") 2>&1

echo "=== Paper retrain started $(date) ==="
echo "Protocol: test-positive-only graph removal; ML +6 edge dims"

echo "=== Table 2 MSAT 10-fold CV ==="
"$PY" -u train.py 2>&1 | tee results/phase8_logs/paper_retrain_msat.log

echo "=== Table 2 ML baselines (1:1) ==="
"$PY" -u scripts/run_baselines.py --models lr rf xgb 2>&1 | tee results/phase8_logs/paper_retrain_ml.log

echo "=== Table 2 GNN baselines (1:1) ==="
"$PY" -u scripts/run_baselines.py --models gcn gat rgcn hgt hetnn simple_hgn 2>&1 | tee results/phase8_logs/paper_retrain_gnn.log

echo "=== Table 3 ablation (w/o + only) ==="
"$PY" -u scripts/run_ablation.py 2>&1 | tee results/phase8_logs/paper_retrain_ablation.log

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
RUN_FAERS_ONLY_TRAIN=1 RUN_LEGACY_COLDSTART=0 bash scripts/server_phase9_run.sh \
  2>&1 | tee results/phase8_logs/paper_retrain_phase9.log

echo "=== Paper retrain COMPLETE $(date) ==="
