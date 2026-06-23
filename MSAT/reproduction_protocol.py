"""Shared reproduction protocol metadata for generated result files."""

from __future__ import annotations


PROTOCOL_VERSION = '2026-06-23-val-test-edge-hidden'


def protocol_metadata() -> dict:
    return {
        'version': PROTOCOL_VERSION,
        'inductive_edge_removal': 'validation_and_test_positive_cmm_adr',
        'validation_and_test_positive_edges_hidden': True,
        'prediction_checkpoint_selection_metric': 'best_val_auc',
    }
