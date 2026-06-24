import json
from pathlib import Path

from scripts.diagnose_reproduction_gaps import (
    checkpoint_provenance,
    checkpoint_recovery_inventory,
    table5_diagnostics,
)


def test_table5_diagnostics_runs_and_flags_paper_seed_mode_as_diagnostic_only():
    diagnostics = table5_diagnostics()

    assert diagnostics['n_faers_pairs'] == 25734
    assert diagnostics['n_lit_pairs'] == 1328
    assert diagnostics['n_all_pos'] == 27062

    seed_block = diagnostics['paper_seed_top1_oof']
    assert seed_block['mode'] == 'paper_herb_top1_oof'
    assert seed_block['diagnostic_only'] is True
    assert seed_block['is_table5_reproduction_claim'] is False
    assert seed_block['n_rows'] == 15
    assert seed_block['adr_match_paper'] == 0

    coverage = diagnostics['paper_reference_pair_coverage']
    assert coverage['paper_rows'] == 15
    assert coverage['mapped_pairs'] == 14
    assert coverage['pairs_in_graph'] == 1
    assert coverage['pairs_in_oof_scores'] == 1
    assert coverage['unmapped_adr_pts'] == ['Small intestinal haemorrhage']


def test_checkpoint_provenance_detects_local_hash_mismatch(tmp_path: Path):
    local = tmp_path / 'best_model_for_prediction.pt'
    local.write_bytes(b'local-checkpoint')
    summary = tmp_path / 'table5_summary.json'
    summary.write_text(
        json.dumps(
            {
                'checkpoint': {
                    'path': '/remote/saved_models/best_model_for_prediction.pt',
                    'exists': True,
                    'sha256': 'not-the-local-sha',
                }
            }
        ),
        encoding='utf-8',
    )

    provenance = checkpoint_provenance(summary, local)

    assert provenance['expected_checkpoint_sha256'] == 'not-the-local-sha'
    assert provenance['local_checkpoint_exists'] is True
    assert provenance['local_checkpoint_matches_expected'] is False
    assert 'not the checkpoint that generated Table 5' in provenance['warning']


def test_checkpoint_recovery_inventory_finds_local_match_and_reports_bundle_absence(tmp_path: Path):
    model_dir = tmp_path / 'saved_models'
    model_dir.mkdir()
    match = model_dir / 'best_model_for_prediction.pt'
    match.write_bytes(b'target')
    other = model_dir / 'best_model_fold0.pt'
    other.write_bytes(b'other')
    bundle = tmp_path / 'results_only.tgz'
    bundle.write_bytes(b'not-a-tar')

    inventory = checkpoint_recovery_inventory(
        expected_sha256='34a04005bcaf206eec990bd9637d9fdb6725e0a0c0d4aebf003f17f4c956eb5c',
        model_dir=model_dir,
        result_bundle=bundle,
    )

    assert inventory['matching_local_checkpoints'] == [str(match)]
    assert inventory['result_bundle_contains_checkpoint'] is False
    assert inventory['minimum_supplemental_materials'][0].startswith('Original predictor checkpoint')
