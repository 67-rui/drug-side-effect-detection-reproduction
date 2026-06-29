# PU-XMSAT Top-20 External Evidence Review

**Generated:** 2026-06-29
**Scope:** first-pass manual/web evidence screen for the top-20 mechanism-supported PU-XMSAT candidates.

## Executive Conclusion

No top-20 mechanism candidate currently qualifies as strong external validation of a complete herb-compound-target-ADR chain.

The current evidence status is:

- Strong complete-chain evidence: 0 / 20
- Moderate indirect support: 1 / 20
- Weak or boundary support: 2 / 20
- No direct support found in first-pass screen: 17 / 20

This does not invalidate the interpretability experiment. It changes the manuscript claim:

> The explanation layer should be presented as mechanism triage: PU-XMSAT identifies sensitive local mechanism paths and prioritizes them for external review, but current public evidence does not confirm complete biological mechanisms for the top candidates.

## Best Case Candidates For Manuscript Discussion

| Priority | Candidate | Evidence level | Support type | Manuscript use |
| ---: | --- | --- | --- | --- |
| 1 | `Polypodium glycyrrhiza` -> `Watery diarrhoea`; optionally discuss `Anorectal discomfort` as same GI direction | Moderate, indirect | Herb/GI-direction support only; no confirmed target or compound identity | Best positive triage example, but write as GI-direction plausibility, not mechanism proof |
| 2 | `Crocus antalyensis cv` -> `Altered state of consciousness` | Weak | Genus-level Crocus/saffron safety and CNS-related background only; species differs | Use only as weak hypothesis-generating example if needed |
| 3 | `Fragaria vesca L.` -> `Altered state of consciousness` | Weak to negative boundary | Sparse, confounded pharmacovigilance signal; EMA wild-strawberry leaf record does not support notable adverse effects | Better used as a boundary/negative case showing why external review is necessary |

## Evidence Notes

### Polypodium GI-Direction Candidate

PU-XMSAT ranked `Polypodium glycyrrhiza` -> `Watery diarrhoea` with the largest perturbation-sensitive path:

- Top path: `target:15721`
- Priority score: 0.00117439
- Target candidate label: VHLL by HGNC/BioBERT, but with low margin; do not use as confirmed identity.

External evidence supports only a broad gastrointestinal direction. EMA's Polypodii rhizoma page reports a mild laxative effect for polypody rhizome medicines when used for coughs and colds. The EMA assessment report for `Polypodium vulgare L., rhizoma` also discusses traditional use for occasional constipation and states that a mild laxative effect may be considered a minor adverse reaction in the cough/cold indication.

Boundary:

- Evidence is for `Polypodium vulgare` / polypody rhizome, not a direct `Polypodium glycyrrhiza` adverse-event case.
- It supports GI plausibility, not a confirmed watery-diarrhoea mechanism.
- No compound or target identity is confirmed.

Sources:

- EMA Polypodii rhizoma page: https://www.ema.europa.eu/en/medicines/herbal/polypodii-rhizoma
- EMA assessment report PDF: https://www.ema.europa.eu/en/documents/herbal-report/assessment-report-polypodium-vulgare-l-rhizoma_en.pdf

### Crocus Candidate

PU-XMSAT repeatedly selected `Crocus antalyensis cv` paths involving `compound:821`, including altered state of consciousness, dry cough, proteinuria, and jaundice candidates.

The strongest usable external context is weak. PubMed records for exact `Crocus antalyensis` mainly concern in-vitro cytotoxicity/apoptosis, not dry cough or altered consciousness. Saffron (`Crocus sativus`) reviews report generally tolerable safety, with adverse events dominated by mild gastrointestinal symptoms, and some CNS-adjacent background such as sleep/drowsiness in saffron literature. Because the species differs, this cannot be used as strong evidence.

Boundary:

- Do not write `Crocus antalyensis cv` -> dry cough as supported.
- Do not transfer `Crocus sativus` evidence into a strong `Crocus antalyensis` claim.
- `compound:821` and target nodes remain graph-local IDs.

Sources:

- PubMed `Crocus antalyensis` article: https://pubmed.ncbi.nlm.nih.gov/22897477/
- Saffron adverse-events systematic review: https://pubmed.ncbi.nlm.nih.gov/42057871/
- Saffron sleep review: https://pmc.ncbi.nlm.nih.gov/articles/PMC10357048/

### Fragaria Boundary Candidate

PU-XMSAT contains several `Fragaria vesca L.` candidates, including leukopenia, altered state of consciousness, spina bifida, light anaesthesia, mucosal haemorrhage, and lymph node tenderness.

The EMA wild-strawberry leaf page states that `Fragaria vesca` leaf preparations are traditionally used for minor urinary complaints and mild diarrhoea, and that no side effects had been reported at the time of HMPC assessment. This argues against using the current `Fragaria vesca` candidates as positive external evidence.

openFDA contains sparse `FRAGARIA VESCA` reports, but they are too few, confounded, and not aligned to the top PU-XMSAT preferred terms strongly enough for manuscript validation.

Boundary:

- `Fragaria vesca L.` -> altered state of consciousness should remain a Grade C/boundary example.
- `Fragaria vesca L.` -> leukopenia, lymph node tenderness, mucosal haemorrhage, spina bifida, and light anaesthesia should not be written as supported.

Sources:

- EMA Fragariae folium page: https://www.ema.europa.eu/en/medicines/herbal/fragariae-folium
- openFDA query: https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:%22FRAGARIA%20VESCA%22&limit=2

### Lespedeza Candidate

PU-XMSAT includes `Lespedeza homoloba` candidates for liver injury and altered state of consciousness.

The first-pass screen found exact-species literature around metabolic, immunosuppressive, antioxidant, and phytochemical activity, but no direct support for liver injury or altered state of consciousness. These rows should not be upgraded.

Sources:

- PubMed `Lespedeza homoloba` article: https://pubmed.ncbi.nlm.nih.gov/39268403/
- Kew Plants of the World Online taxon page: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:502481-1

## Top-20 Evidence Screen

| Rank | Candidate | Top path | Evidence level | Decision |
| ---: | --- | --- | --- | --- |
| 1 | `Polypodium glycyrrhiza` -> `Watery diarrhoea` | `target:15721` | Moderate indirect | Use as GI-direction triage case only |
| 2 | `Crocus antalyensis cv` -> `Dry cough` | `compound:821;target:11486` | No direct support | Do not write as supported |
| 3 | `Polypodium glycyrrhiza` -> `Anorectal discomfort` | `compound:761;target:7802` | Weak indirect | Optional GI-boundary discussion |
| 4 | `Polypodium glycyrrhiza` -> `Sulphaemoglobinaemia` | `compound:761;target:19336` | No direct support | Do not write as supported |
| 5 | `Crocus antalyensis cv` -> `Proteinuria` | `compound:821;target:19336` | No direct support | Do not write as supported |
| 6 | `Crocus antalyensis cv` -> `Altered state of consciousness` | `compound:821;target:2586` | Weak genus-level | Hypothesis only, not validation |
| 7 | `Crocus antalyensis cv` -> `Jaundice` | `compound:821;target:2586` | No direct support | Do not write as supported |
| 8 | `Fragaria vesca L.` -> `Leukopenia` | `compound:1073;target:15692` | No direct support | Do not write as supported |
| 9 | `Marchantia polymorpha` -> `Dry cough` | `compound:480;target:11486` | No direct support in first-pass screen | Keep queued only |
| 10 | `Marchantia polymorpha` -> `Essential thrombocythaemia` | `compound:480;target:7213` | No direct support in first-pass screen | Keep queued only |
| 11 | `Marchantia polymorpha` -> `Altered state of consciousness` | `compound:480;target:1933` | No direct support in first-pass screen | Keep queued only |
| 12 | `Marchantia polymorpha` -> `Proteinuria` | `compound:480;target:13438` | No direct support in first-pass screen | Keep queued only |
| 13 | `Marchantia polymorpha` -> `Jaundice` | `compound:480;target:2586` | No direct support in first-pass screen | Keep queued only |
| 14 | `Fragaria vesca L.` -> `Light anaesthesia` | `compound:1073;target:20703` | No direct support | Do not write as supported |
| 15 | `Fragaria vesca L.` -> `Spina bifida` | `compound:1073;target:7260` | No direct support | Do not write as supported |
| 16 | `Fragaria vesca L.` -> `Altered state of consciousness` | `compound:1073;target:7213` | Weak to negative boundary | Preserve as Grade C/boundary case |
| 17 | `Fragaria vesca L.` -> `Mucosal haemorrhage` | `compound:745;target:19336` | No direct support | Do not write as supported |
| 18 | `Lespedeza homoloba` -> `Liver injury` | `compound:610;target:11486` | No direct support | Do not write as supported |
| 19 | `Fragaria vesca L.` -> `Lymph node tenderness` | `compound:745;target:19336` | No direct support | Do not write as supported |
| 20 | `Lespedeza homoloba` -> `Altered state of consciousness` | `compound:610;target:7213` | No direct support | Do not write as supported |

## Manuscript Recommendation

Use a two-case interpretability discussion:

1. `Polypodium glycyrrhiza` / GI-direction case as the main positive triage example.
2. `Fragaria vesca L.` / altered-state case as a boundary example showing why perturbation sensitivity alone is insufficient.

Avoid presenting `Crocus antalyensis cv`, `Lespedeza homoloba`, or `Marchantia polymorpha` rows as externally validated mechanisms until stronger source evidence is found.
