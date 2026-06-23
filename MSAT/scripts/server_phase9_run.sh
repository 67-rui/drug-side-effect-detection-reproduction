#!/usr/bin/env bash
# Phase 9: paper-aligned downstream eval (§3.5.4–§3.5.6)
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-/root/miniconda3/bin/python}"
LOG="${LOG:-results/phase8_logs/phase9.log}"
mkdir -p results/phase8_logs
exec > >(tee -a "$LOG") 2>&1
echo "=== Phase 9 started $(date) ==="

echo "=== §4.5.1 case study ==="
"$PY" scripts/run_case_zhishi.py

echo "=== Table 5 global Top-15 (paper §3.5.6, exclude all 27062 positives) ==="
"$PY" scripts/run_table5_validation.py

echo "=== Table 6 TCM mapping (paper Table 6 reference) ==="
"$PY" scripts/run_table6_mapping.py

echo "=== Fig.5a FAERS-only cold-start (paper §3.5.4) ==="
if [[ "${RUN_FAERS_ONLY_TRAIN:-1}" == "1" ]]; then
  "$PY" scripts/run_faers_literature_coldstart.py
  "$PY" scripts/run_faers_only_coldstart_train.py
  "$PY" scripts/run_faers_only_coldstart_gnn.py
else
  echo "SKIP FAERS-only Fig.5a (set RUN_FAERS_ONLY_TRAIN=1 to enable)"
fi

echo "=== NON-PAPER legacy (10-fold CV cold-start proxy) ==="
if [[ "${RUN_LEGACY_COLDSTART:-0}" == "1" ]]; then
  "$PY" scripts/run_coldstart_eval.py
  "$PY" scripts/run_coldstart_gnn.py --models gat hgt simple_hgn
else
  echo "SKIP legacy 10-fold coldstart (set RUN_LEGACY_COLDSTART=1 to enable)"
fi

echo "=== Phase 9 COMPLETE $(date) ==="
