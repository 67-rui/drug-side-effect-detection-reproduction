#!/usr/bin/env python3
"""Audit local reproduction artifacts for stale or non-citable outputs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]

DOWNSTREAM_PROVENANCE = {
    'table5_summary.json': ('checkpoint', 'input_summary'),
    'case_zhishi_diarrhoea.json': ('checkpoint',),
    'table6_mapping.json': ('input_manifest',),
}
ML_BASELINES = {'lr', 'rf', 'xgb'}


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return {'_json_error': str(exc)}


def add_issue(issues: list[dict], severity: str, code: str, file: str, message: str) -> None:
    issues.append({
        'severity': severity,
        'code': code,
        'file': file,
        'message': message,
    })


def artifact_is_stale(payload: dict | None) -> tuple[bool, str | None]:
    if not isinstance(payload, dict):
        return False, None
    status = payload.get('artifact_status')
    if not isinstance(status, dict):
        return False, None
    return bool(status.get('stale')), status.get('reason')


def has_any_provenance(payload: dict, keys: tuple[str, ...]) -> bool:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict) and value.get('exists') is not False:
            return True
    return False


def fig6_winners(payload: dict | None) -> dict[str, dict]:
    if not isinstance(payload, dict):
        return {}
    winners: dict[str, dict] = {}
    for row in payload.get('rows', []):
        if 'ratio' not in row or 'model' not in row or 'auc' not in row:
            continue
        ratio = str(row['ratio'])
        current = winners.get(ratio)
        if current is None or float(row['auc']) > float(current['auc']):
            winners[ratio] = {
                'model': str(row['model']).lower(),
                'auc': float(row['auc']),
                'source': row.get('source'),
            }
    return winners


def audit_results(results_dir: str | Path) -> dict:
    results_path = Path(results_dir)
    issues: list[dict] = []
    stale_files: list[str] = []
    missing_files: list[str] = []

    for filename, provenance_keys in DOWNSTREAM_PROVENANCE.items():
        payload = load_json(results_path / filename)
        if payload is None:
            missing_files.append(filename)
            continue
        if '_json_error' in payload:
            add_issue(issues, 'error', 'invalid_json', filename, payload['_json_error'])
            continue
        stale, reason = artifact_is_stale(payload)
        if stale:
            stale_files.append(filename)
            add_issue(
                issues,
                'error',
                'stale_artifact',
                filename,
                reason or 'artifact is marked stale',
            )
        elif not has_any_provenance(payload, provenance_keys):
            add_issue(
                issues,
                'error',
                'missing_provenance',
                filename,
                f'missing one of provenance keys: {", ".join(provenance_keys)}',
            )

    baseline = load_json(results_path / 'baseline_neg10_summary.json')
    suspicious_ml: list[dict] = []
    if isinstance(baseline, dict):
        for row in baseline.get('models', []):
            model = str(row.get('model', '')).lower()
            auc = row.get('auc')
            if model in ML_BASELINES and auc is not None and float(auc) >= 0.99:
                item = {'model': model.upper(), 'auc': float(auc), 'source': row.get('source')}
                suspicious_ml.append(item)
                add_issue(
                    issues,
                    'error',
                    'suspicious_ml_auc',
                    'baseline_neg10_summary.json',
                    f"{item['model']} AUC={item['auc']:.6f}; likely pre-fix leakage result",
                )

    winners = fig6_winners(load_json(results_path / 'fig6_summary.json'))
    for ratio, winner in sorted(winners.items(), key=lambda x: int(x[0])):
        if winner['model'] != 'msat':
            add_issue(
                issues,
                'warning',
                'fig6_msat_not_winner',
                'fig6_summary.json',
                f"ratio {ratio} winner is {winner['model']} AUC={winner['auc']:.6f}",
            )

    return {
        'created_at': datetime.now().isoformat(),
        'results_dir': str(results_path),
        'summary': {
            'stale_artifacts': stale_files,
            'missing_artifacts': missing_files,
            'suspicious_ml_baselines': suspicious_ml,
            'fig6_winners': winners,
        },
        'issues': issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit MSAT reproduction result state')
    parser.add_argument(
        '--results-dir',
        type=Path,
        default=MSAT_ROOT / 'results',
    )
    parser.add_argument(
        '--out',
        type=Path,
        default=None,
        help='Optional JSON output path',
    )
    parser.add_argument(
        '--fail-on-error',
        action='store_true',
        help='Exit non-zero if any error-severity issue is found',
    )
    args = parser.parse_args()

    audit = audit_results(args.results_dir)
    text = json.dumps(audit, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')

    if args.fail_on_error and any(i['severity'] == 'error' for i in audit['issues']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
