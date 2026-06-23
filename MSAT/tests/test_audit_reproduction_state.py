import json

from scripts.audit_reproduction_state import audit_results


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding='utf-8')


def test_audit_detects_stale_artifacts_suspicious_ml_and_fig6_mismatch(tmp_path):
    results = tmp_path / 'results'
    results.mkdir()
    write_json(
        results / 'table5_summary.json',
        {
            'artifact_status': {
                'stale': True,
                'reason': 'old checkpoint',
            }
        },
    )
    write_json(
        results / 'baseline_neg10_summary.json',
        {
            'models': [
                {'model': 'MSAT', 'auc': 0.871},
                {'model': 'LR', 'auc': 0.99999},
                {'model': 'RF', 'auc': 0.88},
            ]
        },
    )
    write_json(
        results / 'fig6_summary.json',
        {
            'rows': [
                {'ratio': 2, 'model': 'msat', 'auc': 0.82},
                {'ratio': 2, 'model': 'hgt', 'auc': 0.83},
                {'ratio': 10, 'model': 'msat', 'auc': 0.84},
                {'ratio': 10, 'model': 'hgt', 'auc': 0.82},
            ]
        },
    )

    audit = audit_results(results)

    codes = [issue['code'] for issue in audit['issues']]
    assert 'stale_artifact' in codes
    assert 'suspicious_ml_auc' in codes
    assert 'fig6_msat_not_winner' in codes
    assert audit['summary']['fig6_winners']['2']['model'] == 'hgt'
    assert audit['summary']['fig6_winners']['10']['model'] == 'msat'


def test_audit_requires_provenance_for_fresh_downstream_artifacts(tmp_path):
    results = tmp_path / 'results'
    results.mkdir()
    write_json(results / 'table5_summary.json', {'artifact_status': {'stale': False}})
    write_json(results / 'case_zhishi_diarrhoea.json', {'artifact_status': {'stale': False}})
    write_json(results / 'table6_mapping.json', {'artifact_status': {'stale': False}})

    audit = audit_results(results)

    missing = [
        issue for issue in audit['issues']
        if issue['code'] == 'missing_provenance'
    ]
    assert {issue['file'] for issue in missing} == {
        'table5_summary.json',
        'case_zhishi_diarrhoea.json',
        'table6_mapping.json',
    }
