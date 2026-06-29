# PU-XMSAT Evidence-Aware Literature Signal Review

**Generated:** 2026-06-29
**Scope:** PubMed-only first-pass signal screen for the top-30 evidence-aware mechanism candidates selected from the 391 explicit-path PU-XMSAT candidate pool.

## Executive Conclusion

The 391-candidate expansion is useful, but it still does not produce strong complete-chain validation.

Current status:

- Explicit-path candidate pool: 391
- Evidence-aware queue size: 30
- Unique herbs in queue: 8
- PubMed exact-query cache entries: 30
- PubMed rows retained after herb/ADR text matching: 2
- Unique candidate with PubMed signal: 1
- Manually verified strong complete-chain evidence: 0

The new signal is:

> `Marchantia polymorpha` -> `Liver injury`

This should be treated as a biological-relevance or direction-conflicting manual-review candidate, not as adverse-reaction validation. The two retained PubMed records study hepatoprotective effects of `Marchantia polymorpha` material in chemically induced liver-injury models. That means the herb and liver-injury concept co-occur, but the direction is closer to protection/treatment in preclinical models than to an observed adverse liver-injury event.

## PubMed Signal Rows

| Candidate | PubMed PMID | Year | Title | Direction for manuscript |
| --- | --- | ---: | --- | --- |
| `Marchantia polymorpha` -> `Liver injury` | 33128532 | 2022 | Marchantia polymorpha L. flavonoids protect liver from CCl4-induced injury | Biological relevance; direction-conflicting hepatoprotective evidence |
| `Marchantia polymorpha` -> `Liver injury` | 37273612 | 2023 | Metabolic profiling of Marchantia polymorpha and hepatoprotective activity in paracetamol-induced liver injury | Biological relevance; direction-conflicting hepatoprotective evidence |

Sources:

- PubMed 33128532: https://pubmed.ncbi.nlm.nih.gov/33128532/
- PubMed 37273612: https://pubmed.ncbi.nlm.nih.gov/37273612/
- Open-access PMC record for PMID 37273612: https://pmc.ncbi.nlm.nih.gov/articles/PMC10233839/

## Interpretation

This result improves the explanation layer in a limited but real way:

1. It shows that expanding from 20 deep-quantified candidates to 391 explicit-path candidates can surface new review targets.
2. It identifies a candidate where the herb and adverse-event concept are externally connected.
3. It also demonstrates why text-match evidence cannot be treated as validation: the direction may conflict with the predicted adverse-event interpretation.

Therefore, the manuscript should still describe the explanation layer as evidence-aware mechanism triage. The strongest defensible statement is:

> PU-XMSAT expands high-scoring predictions into an explicit-path mechanism pool and reranks candidates for manual evidence review. The evidence-aware queue can surface biologically relevant literature signals, but current evidence remains insufficient for strong complete-chain external validation.

## Recommended Manual Review Shortlist

| Priority | Candidate | Why review next | Current boundary |
| ---: | --- | --- | --- |
| 1 | `Polypodium glycyrrhiza` -> `Watery diarrhoea` | Highest perturbation-supported top-20 case; broad GI-direction support already found | Related-species/related-material support only; no confirmed compound/target identity |
| 2 | `Marchantia polymorpha` -> `Liver injury` | New evidence-aware PubMed signal; herb and liver-injury concept co-occur | Direction appears hepatoprotective/preclinical, not adverse-event validation |
| 3 | `Marchantia polymorpha` -> `Dry cough` / `Jaundice` / `Proteinuria` | High evidence-aware score and multiple explicit paths | No exact PubMed herb+ADR signal in this first-pass screen |
| 4 | `Woodfordia fruticosa`, `Semen Astragali Complati`, `Davallia mariesii` liver/GI/cough candidates | Queue adds herb diversity beyond previous top-20 | Need manual database/literature review; no automatic support claim |

## Claim Boundary

Do not write that any new top-30 evidence-aware candidate is externally validated. The new queue supports prioritization, not confirmation.
