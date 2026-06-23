#!/usr/bin/env python3
"""Download MSAT graph from Zenodo (Route A official data)."""

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'experiments_data_clean_final'
GRAPH_FILE = DEST / 'complete_hetero_graph.pt'
URL = 'https://zenodo.org/records/17933842/files/complete_hetero_graph.pt?download=1'


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    if GRAPH_FILE.exists():
        print(f'[OK] Already exists: {GRAPH_FILE} ({GRAPH_FILE.stat().st_size:,} bytes)')
        return

    print(f'[..] Downloading from Zenodo (~100MB)...')
    urllib.request.urlretrieve(URL, GRAPH_FILE)
    print(f'[OK] Saved: {GRAPH_FILE} ({GRAPH_FILE.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
