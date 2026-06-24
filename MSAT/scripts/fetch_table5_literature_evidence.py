#!/usr/bin/env python3
"""Fetch public literature candidates for current Table 5 predictions.

This script queries public literature APIs and writes review candidates. It does
not mark any row as verified support; Table 5 support claims still require human
review of the source article/database entry.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.literature_evidence import (  # noqa: E402
    LiteratureRecord,
    annotate_relevance,
    build_query_variants,
    fetch_provider_records,
)


SUPPORTED_PROVIDERS = ['pubmed', 'openalex', 'crossref']
DEFAULT_PROVIDERS = ['pubmed', 'openalex']
OUTPUT_FIELDS = [
    'rank',
    'herb_id',
    'herb_latin',
    'herb_chinese',
    'herb_pinyin',
    'adr_id',
    'adr_pt',
    'provider',
    'query_kind',
    'query',
    'from_cache',
    'title',
    'year',
    'source',
    'url',
    'doi',
    'pmid',
    'herb_match',
    'adr_match',
    'toxicity_context',
    'support_candidate',
    'manual_review_required',
    'verified_support',
    'match_reason',
    'abstract_snippet',
]


def _load_cache(path: Path) -> dict:
    if not path.is_file():
        return {'queries': {}}
    payload = json.loads(path.read_text(encoding='utf-8'))
    payload.setdefault('queries', {})
    return payload


def _write_cache(path: Path, payload: dict) -> None:
    payload['updated_at'] = datetime.now().isoformat()
    payload['note'] = (
        'Raw public literature query cache for Table 5 evidence screening. '
        'Cached records are candidates only, not verified support.'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def _records_from_cache(entry: dict) -> list[LiteratureRecord]:
    return [LiteratureRecord(**record) for record in entry.get('records', [])]


def _cache_key(provider: str, plain_query: str) -> str:
    return f'{provider}::{plain_query}'


def _fetch_or_load(
    cache: dict,
    provider: str,
    plain_query: str,
    fetch_fn,
    offline: bool,
) -> tuple[list[LiteratureRecord], bool, str | None]:
    key = _cache_key(provider, plain_query)
    entry = cache['queries'].get(key)
    if entry is not None:
        return _records_from_cache(entry), True, entry.get('error')
    if offline:
        return [], False, 'offline and query not present in cache'

    try:
        records = fetch_fn()
    except Exception as exc:  # pragma: no cover - depends on live network.
        cache['queries'][key] = {
            'provider': provider,
            'query': plain_query,
            'records': [],
            'error': f'{type(exc).__name__}: {exc}',
            'fetched_at': datetime.now().isoformat(),
        }
        return [], False, cache['queries'][key]['error']

    cache['queries'][key] = {
        'provider': provider,
        'query': plain_query,
        'records': [record.to_dict() for record in records],
        'error': None,
        'fetched_at': datetime.now().isoformat(),
    }
    return records, False, None


def _dedupe(rows: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for row in sorted(
        rows,
        key=lambda r: (
            int(r.get('rank') or 0),
            not bool(r.get('support_candidate')),
            str(r.get('provider') or ''),
            str(r.get('year') or ''),
            str(r.get('title') or ''),
        ),
    ):
        key = (
            row.get('rank'),
            row.get('provider'),
            row.get('url') or row.get('doi') or row.get('title'),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _passes_relevance_filter(row: dict) -> bool:
    return bool(row.get('herb_match') or row.get('adr_match'))


def run(
    input_path: Path,
    out_csv: Path,
    out_json: Path,
    cache_path: Path,
    providers: list[str],
    max_query_variants: int,
    max_results_per_provider: int,
    timeout: int,
    email: str | None,
    offline: bool = False,
    sleep_seconds: float = 0.0,
    include_toxicity_fallback: bool = False,
) -> dict:
    rows = list(csv.DictReader(input_path.open(encoding='utf-8')))
    cache = _load_cache(cache_path)
    annotated_rows: list[dict] = []
    errors: list[dict] = []
    filtered_out = 0

    for row in rows:
        variants = build_query_variants(
            row,
            max_variants=max_query_variants,
            include_toxicity_fallback=include_toxicity_fallback,
        )
        for provider in providers:
            for variant in variants:
                records, from_cache, error = _fetch_or_load(
                    cache,
                    provider,
                    variant.plain_query,
                    lambda provider=provider, variant=variant: fetch_provider_records(
                        provider,
                        variant,
                        max_results_per_provider,
                        timeout,
                        email,
                    ),
                    offline=offline,
                )
                if error:
                    errors.append(
                        {
                            'rank': row.get('rank'),
                            'provider': provider,
                            'query': variant.plain_query,
                            'error': error,
                        }
                    )
                for record in records:
                    annotated = annotate_relevance(row, record)
                    annotated['query_kind'] = variant.query_kind
                    annotated['query'] = variant.plain_query
                    annotated['from_cache'] = from_cache
                    if not _passes_relevance_filter(annotated):
                        filtered_out += 1
                        continue
                    annotated_rows.append(annotated)
                if sleep_seconds and not from_cache and not offline:
                    time.sleep(sleep_seconds)

    final_rows = _dedupe(annotated_rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(final_rows)

    summary = {
        'created_at': datetime.now().isoformat(),
        'input': str(input_path),
        'providers': providers,
        'cache': str(cache_path),
        'offline': offline,
        'include_toxicity_fallback': include_toxicity_fallback,
        'rows_written': len(final_rows),
        'support_candidates': sum(1 for row in final_rows if row['support_candidate']),
        'filtered_out_low_relevance': filtered_out,
        'manual_review_required': True,
        'verified_support_count': 0,
        'errors': errors,
        'csv': str(out_csv),
        'rows': final_rows,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    _write_cache(cache_path, cache)
    return summary


def parse_providers(value: str) -> list[str]:
    providers = [v.strip().lower() for v in value.split(',') if v.strip()]
    invalid = [p for p in providers if p not in SUPPORTED_PROVIDERS]
    if invalid:
        raise argparse.ArgumentTypeError(f'unsupported providers: {", ".join(invalid)}')
    return providers


def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch Table 5 public literature candidates')
    parser.add_argument(
        '--input',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table5_top15.csv',
    )
    parser.add_argument(
        '--out-csv',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table5_literature_evidence_candidates.csv',
    )
    parser.add_argument(
        '--out-json',
        type=Path,
        default=MSAT_ROOT / 'results' / 'table5_literature_evidence_candidates.json',
    )
    parser.add_argument(
        '--cache',
        type=Path,
        default=MSAT_ROOT / 'data' / 'table5_literature_cache.json',
    )
    parser.add_argument('--providers', type=parse_providers, default=DEFAULT_PROVIDERS)
    parser.add_argument('--max-query-variants', type=int, default=2)
    parser.add_argument('--max-results-per-provider', type=int, default=5)
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--email', default=None, help='Optional contact email for API etiquette')
    parser.add_argument(
        '--offline',
        action='store_true',
        help='Use only cached query responses; do not call public APIs',
    )
    parser.add_argument(
        '--include-toxicity-fallback',
        action='store_true',
        help='Also query herb toxicity/adverse-effect literature; these rows are not verified ADR support.',
    )
    parser.add_argument('--sleep-seconds', type=float, default=0.2)
    args = parser.parse_args()

    summary = run(
        input_path=args.input,
        out_csv=args.out_csv,
        out_json=args.out_json,
        cache_path=args.cache,
        providers=args.providers,
        max_query_variants=args.max_query_variants,
        max_results_per_provider=args.max_results_per_provider,
        timeout=args.timeout,
        email=args.email,
        offline=args.offline,
        sleep_seconds=args.sleep_seconds,
        include_toxicity_fallback=args.include_toxicity_fallback,
    )
    print(f'[SAVED] {args.out_csv}')
    print(f'[SAVED] {args.out_json}')
    print(f'[CACHE] {args.cache}')
    print(
        '[candidates] '
        f'{summary["support_candidates"]}/{summary["rows_written"]} '
        'rows match herb+ADR terms; all require manual review'
    )
    if summary['errors']:
        print(f'[WARN] {len(summary["errors"])} query errors recorded in JSON summary')


if __name__ == '__main__':
    main()
