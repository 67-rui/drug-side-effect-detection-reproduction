#!/usr/bin/env bash
# Phase 8 CPU / local steps — run after GPU results are synced back.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Phase 8A: entity mapping (if not done) ==="
python3 scripts/build_entity_mapping.py
python3 scripts/validate_entity_mapping.py

echo "=== Phase 8E: cold-start metrics from summaries ==="
python3 scripts/run_coldstart_eval.py --model-name MSAT
for f in results/baseline_{gat,hgt,simple_hgn}.json; do
  if [[ -f "$f" ]]; then
    python3 scripts/run_coldstart_eval.py --summary "$f" --model-name "$(basename "$f" .json)"
  fi
done

echo "=== Phase 8F: Table 5 / 6 / case study ==="
python3 scripts/run_table5_validation.py
python3 scripts/run_table6_mapping.py
python3 scripts/run_case_zhishi.py

echo "=== Aggregate ablation (after GPU) ==="
python3 scripts/run_ablation.py --aggregate-only
python3 scripts/run_baselines.py --neg-ratio 10 --aggregate-only

echo "=== Done local Phase 8F + aggregates ==="
