from inference.literature_evidence import (
    LiteratureRecord,
    annotate_relevance,
    build_query_variants,
    parse_pubmed_xml,
    reconstruct_openalex_abstract,
)


def test_build_query_variants_prefers_clean_latin_name():
    row = {
        'latin': 'Fragaria vesca?L.',
        'pinyin': 'YE CAO MEI',
        'chinese': '野草莓',
        'adr_pt': 'Altered state of consciousness',
    }

    variants = build_query_variants(row)

    assert variants[0].herb_term == 'Fragaria vesca L.'
    assert variants[0].adr_term == 'Altered state of consciousness'
    assert 'Fragaria vesca L.' in variants[0].plain_query
    assert 'Altered state of consciousness' in variants[0].plain_query
    assert len({v.plain_query for v in variants}) == len(variants)


def test_build_query_variants_can_add_toxicity_fallback():
    row = {
        'latin': 'Fragaria vesca?L.',
        'pinyin': 'YE CAO MEI',
        'chinese': '野草莓',
        'adr_pt': 'Altered state of consciousness',
    }

    variants = build_query_variants(row, max_variants=1, include_toxicity_fallback=True)

    assert [v.query_kind for v in variants] == ['adr_exact', 'toxicity_fallback']
    assert 'toxicity' in variants[1].plain_query
    assert 'Altered state of consciousness' not in variants[1].plain_query


def test_pubmed_xml_parser_extracts_core_metadata():
    xml = '''
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>123456</PMID>
          <Article>
            <Journal><Title>Journal of Herbal Safety</Title></Journal>
            <ArticleTitle>Fragaria vesca and altered state of consciousness</ArticleTitle>
            <Abstract>
              <AbstractText>Case evidence describes altered state of consciousness after exposure.</AbstractText>
            </Abstract>
            <ArticleDate><Year>2024</Year></ArticleDate>
            <ELocationID EIdType="doi">10.1234/herb.2024.1</ELocationID>
          </Article>
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>
    '''

    records = parse_pubmed_xml(xml)

    assert records == [
        LiteratureRecord(
            provider='pubmed',
            title='Fragaria vesca and altered state of consciousness',
            url='https://pubmed.ncbi.nlm.nih.gov/123456/',
            year='2024',
            source='Journal of Herbal Safety',
            doi='10.1234/herb.2024.1',
            pmid='123456',
            abstract='Case evidence describes altered state of consciousness after exposure.',
        )
    ]


def test_relevance_annotation_marks_evidence_as_candidate_not_verified():
    row = {
        'rank': 2,
        'latin': 'Fragaria vesca L.',
        'pinyin': 'YE CAO MEI',
        'chinese': '野草莓',
        'adr_pt': 'Altered state of consciousness',
    }
    record = LiteratureRecord(
        provider='openalex',
        title='Fragaria vesca toxicity and altered state of consciousness',
        url='https://openalex.org/W123',
        year='2025',
        source='OpenAlex Test Journal',
        doi='10.5555/example',
        pmid=None,
        abstract='The report discusses altered state of consciousness as an adverse reaction.',
    )

    annotated = annotate_relevance(row, record)

    assert annotated['rank'] == 2
    assert annotated['provider'] == 'openalex'
    assert annotated['herb_match'] is True
    assert annotated['adr_match'] is True
    assert annotated['support_candidate'] is True
    assert annotated['manual_review_required'] is True
    assert annotated['verified_support'] is False


def test_reconstruct_openalex_abstract_orders_tokens_by_position():
    inverted = {
        'Fragaria': [0],
        'vesca': [1],
        'toxicity': [2],
        'case': [4],
        'report': [3],
    }

    assert reconstruct_openalex_abstract(inverted) == 'Fragaria vesca toxicity report case'
