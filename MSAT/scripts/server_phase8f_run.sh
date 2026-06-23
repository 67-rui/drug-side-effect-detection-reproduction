#!/usr/bin/env bash
# Phase 8F wrap-up on server (skip entity rebuild; use conda python).
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOG="${LOG:-results/phase8_logs/phase8f.log}"
mkdir -p results/phase8_logs

exec > >(tee -a "$LOG") 2>&1
echo "=== Phase 8F started $(date) ==="

echo "=== validate entity mapping ==="
"$PY" scripts/validate_entity_mapping.py

echo "=== cold-start eval (skip if no per-pair predictions in summary) ==="
if "$PY" scripts/run_coldstart_eval.py --model-name MSAT 2>/dev/null; then
  for f in results/baseline_gat.json results/baseline_hgt.json results/baseline_simple_hgn.json; do
    if [[ -f "$f" ]]; then
      "$PY" scripts/run_coldstart_eval.py --summary "$f" --model-name "$(basename "$f" .json)" || true
    fi
  done
else
  echo "WARN: cold-start skipped (baseline summaries lack herb_indices); use analyze_stratified.py separately"
fi

echo "=== Table 5 ==="
"$PY" scripts/run_table5_validation.py

echo "=== Table 6 ==="
"$PY" scripts/run_table6_mapping.py

echo "=== case study (枳实) ==="
"$PY" scripts/run_case_zhishi.py

echo "=== aggregate summaries ==="
"$PY" scripts/run_ablation.py --aggregate-only
"$PY" scripts/run_baselines.py --neg-ratio 10 --aggregate-only

echo "=== Phase 8F COMPLETE $(date) ==="
