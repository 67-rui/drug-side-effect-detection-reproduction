import csv
import json
from pathlib import Path

from scripts.fetch_table5_literature_evidence import DEFAULT_PROVIDERS, run


def test_default_providers_keep_crossref_opt_in():
    assert DEFAULT_PROVIDERS == ['pubmed', 'openalex']


def test_run_uses_cached_records_and_writes_review_candidates(tmp_path: Path):
    input_csv = tmp_path / 'table5_top15.csv'
    out_csv = tmp_path / 'evidence.csv'
    out_json = tmp_path / 'evidence.json'
    cache_path = tmp_path / 'cache.json'

    with input_csv.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                'rank',
                'herb_id',
                'pinyin',
                'latin',
                'chinese',
                'adr_id',
                'adr_pt',
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                'rank': '2',
                'herb_id': '237',
                'pinyin': 'YE CAO MEI',
                'latin': 'Fragaria vesca?L.',
                'chinese': '野草莓',
                'adr_id': '3989',
                'adr_pt': 'Altered state of consciousness',
            }
        )

    cache_path.write_text(
        json.dumps(
            {
                'queries': {
                    'pubmed::"Fragaria vesca L." "Altered state of consciousness"': {
                        'provider': 'pubmed',
                        'query': '"Fragaria vesca L." "Altered state of consciousness"',
                        'records': [
                            {
                                'provider': 'pubmed',
                                'title': 'Fragaria vesca and altered state of consciousness',
                                'url': 'https://pubmed.ncbi.nlm.nih.gov/123456/',
                                'year': '2024',
                                'source': 'Journal of Herbal Safety',
                                'doi': '10.1234/herb.2024.1',
                                'pmid': '123456',
                                'abstract': 'Altered state of consciousness was described as an adverse reaction.',
                            },
                            {
                                'provider': 'pubmed',
                                'title': 'Aloe vera toxicity review',
                                'url': 'https://pubmed.ncbi.nlm.nih.gov/654321/',
                                'year': '2023',
                                'source': 'Journal of Herbal Safety',
                                'doi': '10.1234/herb.2023.9',
                                'pmid': '654321',
                                'abstract': 'This unrelated paper discusses adverse effects without the queried herb.',
                            }
                        ],
                    }
                }
            }
        ),
        encoding='utf-8',
    )

    summary = run(
        input_path=input_csv,
        out_csv=out_csv,
        out_json=out_json,
        cache_path=cache_path,
        providers=['pubmed'],
        max_query_variants=1,
        max_results_per_provider=5,
        timeout=1,
        email=None,
        offline=True,
    )

    assert summary['rows_written'] == 1
    assert summary['support_candidates'] == 1
    rows = list(csv.DictReader(out_csv.open(encoding='utf-8')))
    assert rows[0]['provider'] == 'pubmed'
    assert rows[0]['manual_review_required'] == 'True'
    assert rows[0]['verified_support'] == 'False'

    payload = json.loads(out_json.read_text(encoding='utf-8'))
    assert payload['rows'][0]['support_candidate'] is True
