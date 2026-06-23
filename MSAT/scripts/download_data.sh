#!/usr/bin/env bash
# Wrapper — use Python downloader (curl may fail on some networks)
set -euo pipefail
python3 "$(dirname "$0")/download_data.py"
