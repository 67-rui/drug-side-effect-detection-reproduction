#!/usr/bin/env bash
# CPU-only Phase 9 tasks (parallel to GPU baselines on AutoDL)
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOGDIR="${LOG_DIR:-results/phase8_logs}"
mkdir -p "$LOGDIR" results

echo "=== Parallel CPU tasks started $(date) ===" | tee "$LOGDIR/parallel_cpu.log"

echo "[1/3] case study..." | tee -a "$LOGDIR/parallel_cpu.log"
"$PY" scripts/run_case_zhishi.py >> "$LOGDIR/parallel_case.log" 2>&1 \
  && echo "case study OK" | tee -a "$LOGDIR/parallel_cpu.log" \
  || echo "case study FAILED" | tee -a "$LOGDIR/parallel_cpu.log"

echo "[2/3] Table 5..." | tee -a "$LOGDIR/parallel_cpu.log"
TCMDA_ARGS=()
if [[ -f data/tcmda_cache.json ]]; then
  TCMDA_ARGS=(--tcmda-cache data/tcmda_cache.json)
fi
"$PY" scripts/run_table5_validation.py "${TCMDA_ARGS[@]}" >> "$LOGDIR/parallel_table5.log" 2>&1 \
  && echo "Table 5 OK" | tee -a "$LOGDIR/parallel_cpu.log" \
  || echo "Table 5 FAILED" | tee -a "$LOGDIR/parallel_cpu.log"

echo "[3/3] Table 6..." | tee -a "$LOGDIR/parallel_cpu.log"
"$PY" scripts/run_table6_mapping.py >> "$LOGDIR/parallel_table6.log" 2>&1 \
  && echo "Table 6 OK" | tee -a "$LOGDIR/parallel_cpu.log" \
  || echo "Table 6 FAILED" | tee -a "$LOGDIR/parallel_cpu.log"

echo "=== Parallel CPU tasks COMPLETE $(date) ===" | tee -a "$LOGDIR/parallel_cpu.log"
