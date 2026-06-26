#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
tail -n 80 results/phase_pu_xmsat_logs/pu_training.log
