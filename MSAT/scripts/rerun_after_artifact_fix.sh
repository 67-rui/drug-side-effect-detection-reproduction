#!/usr/bin/env bash
# Partial rerun helper for legacy artifact/provenance fixes only.
set -euo pipefail

cd "$(dirname "$0")/.."
PY="${PY:-python}"
LOG_DIR="${LOG_DIR:-results/phase8_logs}"
CKPT="${CKPT:-saved_models/best_model_for_prediction.pt}"
mkdir -p "$LOG_DIR" results

if [[ "${ALLOW_PARTIAL_RERUN:-0}" != "1" ]]; then
  echo "[ERROR] This partial helper is no longer sufficient after the validation-edge protocol fix."
  echo "[ERROR] Run a full corrected retrain instead: PY=$PY bash scripts/server_paper_retrain.sh"
  echo "[ERROR] To intentionally run only this legacy partial chain, set ALLOW_PARTIAL_RERUN=1."
  exit 2
fi

echo "=== Rerun after artifact fix $(date) ==="
echo "[INFO] python=$PY"
echo "[INFO] checkpoint=$CKPT"

echo "=== Corrected Table 4 ML baselines, 1:10 ==="
for model in lr rf xgb; do
  echo "[RUN] corrected neg10 $model"
  "$PY" -u scripts/run_baselines.py --neg-ratio 10 --model "$model" \
    2>&1 | tee "$LOG_DIR/rerun_after_artifact_fix_${model}_neg10.log"
done
"$PY" -u scripts/run_baselines.py --neg-ratio 10 --aggregate-only \
  2>&1 | tee "$LOG_DIR/rerun_after_artifact_fix_baseline_neg10_summary.log"

echo "=== Refresh main predictor checkpoint if needed ==="
if [[ ! -f "$CKPT" ]]; then
  echo "[ERROR] checkpoint not found: $CKPT"
  echo "Run main MSAT training first: $PY -u train.py"
  exit 2
fi

echo "=== Regenerate Table 5, Table 6, and Zhishi case with explicit checkpoint ==="
"$PY" -u scripts/run_table5_validation.py --use-predictor --checkpoint "$CKPT" \
  2>&1 | tee "$LOG_DIR/rerun_after_artifact_fix_table5.log"
"$PY" -u scripts/run_table6_mapping.py \
  2>&1 | tee "$LOG_DIR/rerun_after_artifact_fix_table6.log"
"$PY" -u scripts/run_case_zhishi.py --checkpoint "$CKPT" \
  2>&1 | tee "$LOG_DIR/rerun_after_artifact_fix_case.log"

echo "=== Rerun after artifact fix complete $(date) ==="
