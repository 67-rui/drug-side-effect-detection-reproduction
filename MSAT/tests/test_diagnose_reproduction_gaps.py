from scripts.diagnose_reproduction_gaps import table5_diagnostics


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
