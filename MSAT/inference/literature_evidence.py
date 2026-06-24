"""Public literature evidence helpers for Table 5 review.

The helpers in this module deliberately produce review candidates, not verified
Table 5 support. A human still needs to read the source before promoting a row
to a confirmed database/literature claim.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Iterable


PUBMED_ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
PUBMED_EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
OPENALEX_WORKS = 'https://api.openalex.org/works'
CROSSREF_WORKS = 'https://api.crossref.org/works'
USER_AGENT = 'MSAT-reproduction-literature-evidence/1.0 (Table 5 audit)'

TOXICITY_TERMS = (
    'adverse',
    'toxicity',
    'toxic',
    'poison',
    'poisoning',
    'side effect',
    'side-effect',
    'reaction',
    'hepatotoxic',
    'neurotoxic',
)


@dataclass(frozen=True)
class QueryVariant:
    herb_term: str
    adr_term: str
    plain_query: str
    pubmed_query: str
    query_kind: str = 'adr_exact'


@dataclass(frozen=True)
class LiteratureRecord:
    provider: str
    title: str
    url: str
    year: str | None
    source: str | None
    doi: str | None
    pmid: str | None
    abstract: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def clean_term(value: object) -> str:
    if value is None:
        return ''
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return ''
    text = text.replace('?', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.;:])', r'\1', text)
    return text.strip()


def _dedupe_terms(values: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        term = clean_term(value)
        if not term:
            continue
        key = _norm(term)
        if key in seen:
            continue
        seen.add(key)
        out.append(term)
    return out


def build_query_variants(
    row: dict,
    max_variants: int = 3,
    include_toxicity_fallback: bool = False,
) -> list[QueryVariant]:
    adr_term = clean_term(row.get('adr_pt'))
    herb_terms = _dedupe_terms(
        [
            row.get('latin'),
            row.get('chinese'),
            row.get('pinyin'),
        ]
    )
    variants: list[QueryVariant] = []
    for herb_term in herb_terms[:max_variants]:
        plain = f'"{herb_term}" "{adr_term}"'
        pubmed = f'"{herb_term}"[Title/Abstract] AND "{adr_term}"[Title/Abstract]'
        variants.append(
            QueryVariant(
                herb_term=herb_term,
                adr_term=adr_term,
                plain_query=plain,
                pubmed_query=pubmed,
                query_kind='adr_exact',
            )
        )
        if include_toxicity_fallback:
            fallback_plain = f'"{herb_term}" toxicity adverse effects'
            fallback_pubmed = (
                f'"{herb_term}"[Title/Abstract] AND '
                '(toxicity[Title/Abstract] OR adverse[Title/Abstract] OR '
                '"side effects"[Title/Abstract])'
            )
            variants.append(
                QueryVariant(
                    herb_term=herb_term,
                    adr_term=adr_term,
                    plain_query=fallback_plain,
                    pubmed_query=fallback_pubmed,
                    query_kind='toxicity_fallback',
                )
            )
    return variants


def _norm(text: str | None) -> str:
    if not text:
        return ''
    lowered = text.lower()
    lowered = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', ' ', lowered)
    return ' '.join(lowered.split())


def _english_tokens(text: str) -> list[str]:
    return [t for t in re.findall(r'[a-z0-9]+', _norm(text)) if len(t) >= 3]


def _contains_alias(text_norm: str, alias: str) -> bool:
    alias_norm = _norm(alias)
    if not alias_norm:
        return False
    if alias_norm in text_norm:
        return True
    tokens = [t for t in _english_tokens(alias) if t not in {'var', 'subsp'}]
    if not tokens:
        return False
    # Ignore one-token botanical authority markers such as "L."; requiring the
    # genus/species tokens makes literature title matches less brittle.
    tokens = [t for t in tokens if len(t) > 1]
    return bool(tokens) and all(t in text_norm for t in tokens[:2])


def _row_aliases(row: dict) -> list[str]:
    return _dedupe_terms([row.get('latin'), row.get('chinese'), row.get('pinyin')])


def annotate_relevance(row: dict, record: LiteratureRecord) -> dict:
    combined = ' '.join(
        x
        for x in [record.title, record.abstract or '', record.source or '']
        if x
    )
    combined_norm = _norm(combined)
    aliases = _row_aliases(row)
    adr_pt = clean_term(row.get('adr_pt'))

    herb_match = any(_contains_alias(combined_norm, alias) for alias in aliases)
    adr_match = _contains_alias(combined_norm, adr_pt)
    toxicity_context = any(term in combined_norm for term in TOXICITY_TERMS)
    support_candidate = bool(herb_match and adr_match)

    reasons: list[str] = []
    if herb_match:
        reasons.append('herb term matched')
    if adr_match:
        reasons.append('ADR PT matched')
    if toxicity_context:
        reasons.append('toxicity/adverse context present')
    if not reasons:
        reasons.append('weak text match; retain only for manual screening')

    abstract = record.abstract or ''
    snippet = abstract[:500] + ('...' if len(abstract) > 500 else '')

    return {
        'rank': int(row.get('rank', 0) or 0),
        'herb_id': row.get('herb_id'),
        'herb_latin': clean_term(row.get('latin')),
        'herb_chinese': clean_term(row.get('chinese')),
        'herb_pinyin': clean_term(row.get('pinyin')),
        'adr_id': row.get('adr_id'),
        'adr_pt': adr_pt,
        'provider': record.provider,
        'title': record.title,
        'year': record.year,
        'source': record.source,
        'url': record.url,
        'doi': record.doi,
        'pmid': record.pmid,
        'herb_match': herb_match,
        'adr_match': adr_match,
        'toxicity_context': toxicity_context,
        'support_candidate': support_candidate,
        'manual_review_required': True,
        'verified_support': False,
        'match_reason': '; '.join(reasons),
        'abstract_snippet': snippet,
    }


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ''
    return ' '.join(''.join(node.itertext()).split())


def _first_text(root: ET.Element, paths: Iterable[str]) -> str:
    for path in paths:
        value = _text(root.find(path))
        if value:
            return value
    return ''


def parse_pubmed_xml(xml_text: str) -> list[LiteratureRecord]:
    root = ET.fromstring(xml_text)
    records: list[LiteratureRecord] = []
    for article in root.findall('.//PubmedArticle'):
        pmid = _first_text(article, ['.//MedlineCitation/PMID'])
        title = _first_text(article, ['.//ArticleTitle'])
        abstract_parts = [_text(n) for n in article.findall('.//Abstract/AbstractText')]
        abstract = ' '.join(p for p in abstract_parts if p) or None
        source = _first_text(article, ['.//Journal/Title', './/MedlineJournalInfo/MedlineTA']) or None
        year = _first_text(
            article,
            [
                './/ArticleDate/Year',
                './/JournalIssue/PubDate/Year',
                './/DateCompleted/Year',
            ],
        ) or None
        doi = None
        for doi_node in article.findall('.//ELocationID'):
            if doi_node.attrib.get('EIdType', '').lower() == 'doi':
                doi = _text(doi_node)
                break
        if doi is None:
            for id_node in article.findall('.//ArticleId'):
                if id_node.attrib.get('IdType', '').lower() == 'doi':
                    doi = _text(id_node)
                    break
        if not title:
            continue
        url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else ''
        records.append(
            LiteratureRecord(
                provider='pubmed',
                title=title,
                url=url,
                year=year,
                source=source,
                doi=doi,
                pmid=pmid or None,
                abstract=abstract,
            )
        )
    return records


def reconstruct_openalex_abstract(inverted_index: dict | None) -> str | None:
    if not inverted_index:
        return None
    positions: list[tuple[int, str]] = []
    for token, indexes in inverted_index.items():
        for idx in indexes:
            positions.append((int(idx), token))
    if not positions:
        return None
    return ' '.join(token for _, token in sorted(positions))


def parse_openalex_json(payload: dict) -> list[LiteratureRecord]:
    records: list[LiteratureRecord] = []
    for item in payload.get('results', []):
        title = clean_term(item.get('title') or item.get('display_name'))
        if not title:
            continue
        doi = clean_term(item.get('doi')).replace('https://doi.org/', '') or None
        records.append(
            LiteratureRecord(
                provider='openalex',
                title=title,
                url=item.get('id') or item.get('doi') or '',
                year=str(item.get('publication_year')) if item.get('publication_year') else None,
                source=(item.get('primary_location') or {})
                .get('source', {})
                .get('display_name'),
                doi=doi,
                pmid=None,
                abstract=reconstruct_openalex_abstract(item.get('abstract_inverted_index')),
            )
        )
    return records


def parse_crossref_json(payload: dict) -> list[LiteratureRecord]:
    records: list[LiteratureRecord] = []
    for item in payload.get('message', {}).get('items', []):
        title_values = item.get('title') or []
        title = clean_term(title_values[0] if title_values else '')
        if not title:
            continue
        year = None
        date_parts = (item.get('published-print') or item.get('published-online') or {}).get('date-parts') or []
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
        records.append(
            LiteratureRecord(
                provider='crossref',
                title=title,
                url=item.get('URL') or (f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else ''),
                year=year,
                source=(item.get('container-title') or [None])[0],
                doi=item.get('DOI'),
                pmid=None,
                abstract=_strip_crossref_markup(item.get('abstract')),
            )
        )
    return records


def _strip_crossref_markup(value: str | None) -> str | None:
    if not value:
        return None
    stripped = re.sub(r'<[^>]+>', ' ', value)
    return ' '.join(stripped.split()) or None


def _read_url(url: str, params: dict, timeout: int, email: str | None = None) -> bytes:
    if email:
        params = {**params, 'email': email}
    full_url = f'{url}?{urllib.parse.urlencode(params)}'
    request = urllib.request.Request(full_url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_pubmed_records(
    variant: QueryVariant,
    max_results: int,
    timeout: int,
    email: str | None = None,
) -> list[LiteratureRecord]:
    search_payload = json.loads(
        _read_url(
            PUBMED_ESEARCH,
            {
                'db': 'pubmed',
                'term': variant.pubmed_query,
                'retmode': 'json',
                'retmax': str(max_results),
                'sort': 'relevance',
            },
            timeout,
            email,
        ).decode('utf-8')
    )
    ids = search_payload.get('esearchresult', {}).get('idlist', [])
    if not ids:
        return []
    xml_text = _read_url(
        PUBMED_EFETCH,
        {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'xml',
        },
        timeout,
        email,
    ).decode('utf-8')
    return parse_pubmed_xml(xml_text)


def fetch_openalex_records(
    variant: QueryVariant,
    max_results: int,
    timeout: int,
    email: str | None = None,
) -> list[LiteratureRecord]:
    params = {
        'search': variant.plain_query,
        'per-page': str(max_results),
    }
    if email:
        params['mailto'] = email
    payload = json.loads(_read_url(OPENALEX_WORKS, params, timeout).decode('utf-8'))
    return parse_openalex_json(payload)


def fetch_crossref_records(
    variant: QueryVariant,
    max_results: int,
    timeout: int,
    email: str | None = None,
) -> list[LiteratureRecord]:
    params = {
        'query': variant.plain_query,
        'rows': str(max_results),
    }
    if email:
        params['mailto'] = email
    payload = json.loads(_read_url(CROSSREF_WORKS, params, timeout).decode('utf-8'))
    return parse_crossref_json(payload)


def fetch_provider_records(
    provider: str,
    variant: QueryVariant,
    max_results: int,
    timeout: int,
    email: str | None = None,
) -> list[LiteratureRecord]:
    if provider == 'pubmed':
        return fetch_pubmed_records(variant, max_results, timeout, email)
    if provider == 'openalex':
        return fetch_openalex_records(variant, max_results, timeout, email)
    if provider == 'crossref':
        return fetch_crossref_records(variant, max_results, timeout, email)
    raise ValueError(f'Unsupported literature provider: {provider}')
