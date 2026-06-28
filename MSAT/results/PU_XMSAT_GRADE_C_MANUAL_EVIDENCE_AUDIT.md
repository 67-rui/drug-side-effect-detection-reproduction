# PU-XMSAT Grade C Manual Evidence Audit

**Date:** 2026-06-28  
**Purpose:** Manually review the two Grade C rows in `PU_XMSAT_CASE_EVIDENCE_REPORT.md` and decide whether either can be promoted to direct external evidence.

## Summary

Neither Grade C case should be upgraded to Grade B/A at this stage.

| Case | Current Grade | Manual Review Result | Paper Use |
| --- | :---: | --- | --- |
| `Fragaria vesca L.` -> Altered state of consciousness | C | External evidence not supportive | Do not use as a positive evidence case |
| `Citrus aurantium L.` -> Watery diarrhoea | C | Mechanistically relevant but direction-conflicting | Use only as hypothesis-generating mechanism discussion |

## Case 1. Fragaria vesca L. -> Altered State of Consciousness

Local source:

- `table5_top15` rank 2.
- Internal graph path: `Fragaria vesca L. -> Compound #1073 -> Target #2586 <- Altered state of consciousness`.
- Local exact PubMed/OpenAlex cache contains no direct records for `"Fragaria vesca L." "Altered state of consciousness"`.

External review:

- The European Medicines Agency page for wild strawberry leaf says the HMPC traditional-use conclusions cover urinary-tract use and mild diarrhoea, not neurological adverse reactions. It also states that no side effects had been reported at the time of assessment. Source: [EMA Fragariae folium](https://www.ema.europa.eu/en/medicines/herbal/fragariae-folium).
- The available automated PubMed/OpenAlex records for this case are toxicity or general plant-biology records; none match the target ADR term.

Decision:

- Keep as Grade C only because the internal graph has a short mechanism path.
- External evidence status: `not_supported`.
- Recommended paper use: negative screening example, not a positive case study.

## Case 2. Citrus aurantium L. -> Watery Diarrhoea

Local source:

- Curated Zhishi case: `case_zhishi_diarrhoea`.
- Internal mechanism paths include `Citrus aurantium L. -> nobiletin (CID 72344) -> Target #8967/#8101 -> Watery diarrhoea`.
- Curated contribution hints: `nobiletin_cid=72344`, `ABCG2 (BCRP)`.

External review:

- A 2018 study reports that *Citrus aurantium* and its flavonoids, including nobiletin, alleviated TNBS-induced IBD-related diarrhoea in rats and inhibited isolated jejunum contraction. This supports gut/diarrhoea relevance but points toward anti-inflammatory or anti-diarrhoeal regulation, not adverse diarrhoea induction. Source: [He et al., 2018](https://www.mdpi.com/1422-0067/19/10/3057).
- A PubMed-indexed case report describes an adverse reaction after an unripe *Citrus aurantium* extract, also known as Zhi shi or bitter orange, but the indexed adverse theme is adrenergic/tachycardia rather than diarrhoea. Source: [Firenzuoli et al., 2005](https://pubmed.ncbi.nlm.nih.gov/15830849/).
- A 2022 systematic review/meta-analysis focuses mainly on p-synephrine cardiovascular safety and does not provide direct support for watery diarrhoea as an adverse reaction. Source: [Koncz et al., 2022](https://www.mdpi.com/2072-6643/14/19/4019).
- ABCG2/BCRP is a broad xenobiotic efflux transporter with gastrointestinal expression, supporting plausibility for transporter-mediated pharmacokinetic mechanisms. Source: [GeneCards ABCG2](https://www.genecards.org/card/ABCG2).
- Flavonoids can inhibit BCRP/ABCG2-mediated transport in vitro, which supports the broad flavonoid-transporter link but is not nobiletin-specific and not diarrhoea-specific. Source: [Zhang et al., 2004](https://doi.org/10.1124/mol.65.5.1208).

Decision:

- Keep as Grade C.
- External evidence status: `mechanism_relevant_direction_conflicting`.
- Recommended paper use: hypothesis-generating mechanistic case only. The manuscript should explicitly state that the current evidence does not prove *Citrus aurantium* causes watery diarrhoea.

## Manuscript Boundary

Use this audit to strengthen the discussion of evidence quality:

> The case-level audit did not identify manually verified direct evidence for the two Grade C candidates. One case was externally unsupported, while the other showed gastrointestinal and transporter-related mechanistic relevance but with direction-conflicting evidence. Therefore, current case evidence should be framed as hypothesis generation and manual-screening support rather than confirmed external validation.

Do not write:

- "The Grade C cases are externally validated."
- "The Citrus aurantium case proves a diarrhoea adverse reaction."
- "The Fragaria vesca case has literature support for altered consciousness."

