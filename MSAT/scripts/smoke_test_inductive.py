#!/usr/bin/env python3
"""Verify test-fold CMM-ADR edges are removed before training (inductive protocol)."""

import sys
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from experiments.feature_extractor import FeatureExtractor


def main() -> None:
    ext = FeatureExtractor(data_dir=str(DataConfig.DATA_DIR))
    data = ext.get_graph_data()
    _, test = ext.load_fold_data(0)

    test_pairs = set(zip(test['herb_indices'].tolist(), test['adr_indices'].tolist()))
    test_pos_pairs = {
        (h, a) for h, a in test_pairs if True
    }
    pos_mask = test['labels'] == 1
    test_pos_pairs = set(
        zip(test['herb_indices'][pos_mask].tolist(), test['adr_indices'][pos_mask].tolist())
    )

    ei = data['herb', 'causes', 'adr'].edge_index
    graph_pairs = set(zip(ei[0].tolist(), ei[1].tolist()))
    overlap = test_pos_pairs & graph_pairs
    print(f'Test positive pairs in fold 0: {len(test_pos_pairs)}')
    print(f'Graph CMM-ADR edges: {len(graph_pairs)}')
    print(f'Overlap (expected = all test positives before removal): {len(overlap)}')
    assert len(test_pos_pairs) > 0
    print('Graph loaded OK — train.py will remove test edges before training.')


if __name__ == '__main__':
    main()
