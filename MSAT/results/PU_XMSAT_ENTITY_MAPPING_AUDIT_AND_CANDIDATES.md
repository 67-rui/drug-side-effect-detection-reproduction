# PU-XMSAT Entity Mapping Audit and Candidate Report

**Generated:** 2026-06-29
**Scope:** top-20 mechanism-supported PU-XMSAT candidates from `batch_mechanism_interpretability_top5000_random_controls`.

## Executive Conclusion

The current top-20 interpretability layer has a clear mapping gap:

- Compound nodes in the top-20 mechanism queue: 20
- Target nodes in the top-20 mechanism queue: 39
- Confirmed compound/target names available from local MSAT artifacts: 0
- Unmapped graph-local compound/target nodes: 59

Therefore, the paper should not claim that PU-XMSAT has already recovered confirmed compound or target identities for these mechanism paths. The current defensible claim is:

> PU-XMSAT extracts checkpoint-aware key mechanism subgraphs and quantifies local perturbation sensitivity at component, target, and pathway levels. Compound and target nodes remain MSAT graph-local IDs unless a separately documented source confirms their names.

## Why Direct Name Recovery Is Not Currently Defensible

Local inspection and public-source checks agree on the same boundary:

- `complete_hetero_graph.pt` stores `herb`, `adr`, `target`, and `compound` node feature matrices and edges, but no compound names, target names, SMILES, PubChem CIDs, HGNC IDs, UniProt IDs, or source IDs.
- `MSAT/data/entity_names.json` currently contains `meta`, `herbs`, and `adrs` only. It has no `compounds` or `targets` sections.
- `MSAT/scripts/build_entity_mapping.py` only builds herb and ADR mappings.
- `MSAT/results/top20_entity_mapping_queue.json` reports `mapped_count = 0` and `unmapped_count = 59`.
- The public MSAT Zenodo/GitHub/Frontiers release documents graph scale and sources, but no stable local node ID dictionary for compound/target nodes.

The graph-local IDs such as `compound:821` and `target:15721` should be treated as local row indices, not as external database identifiers.

## Generated Mapping Artifacts

The following artifacts were generated to make the mapping gap explicit and to support later manual curation:

- `results/top20_entity_mapping_queue.json`
- `results/top20_entity_mapping_queue.csv`
- `results/PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md`
- `results/top20_target_name_candidates.json`
- `results/top20_target_name_candidates.csv`
- `results/PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md`

## Target Candidate Mapping

Because target node features are BioBERT embeddings, we generated HGNC-based candidate labels by comparing each top-20 target node vector against HGNC symbol/name text embeddings.

This is useful for triage, but it is not a confirmed original mapping. The generated status is therefore `candidate_only`.

Candidate source:

- HGNC complete set: https://www.genenames.org/download/
- Download used by script: https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt

Summary:

- Top-20 target nodes with candidates: 39
- HGNC candidates screened: 44,997
- Top-hit margin below 1.0: 11 / 39
- Top-hit margin at least 3.0: 12 / 39

Representative top candidates:

| Target | Top HGNC candidate | Name | Score | Margin | Use |
| --- | --- | --- | ---: | ---: | --- |
| `target:15721` | VHLL | VHL like | 52.653 | 0.275 | Low-margin candidate only; do not use as confirmed identity |
| `target:11486` | APC | APC regulator of Wnt signaling pathway | 77.906 | 6.444 | Candidate worth manual review |
| `target:7802` | OPRK1 | opioid receptor kappa 1 | 39.858 | 0.511 | Low-margin candidate only |
| `target:469` | ZC3H7A | zinc finger CCCH-type containing 7A | 61.289 | 1.174 | Candidate only |
| `target:2432` | HYMAI | hydatidiform mole associated and imprinted | 30.647 | 3.473 | Candidate worth manual review |
| `target:19336` | ALMS1 | ALMS1 centrosome and basal body associated protein | 85.610 | 3.051 | Candidate worth manual review |
| `target:2586` | OPRK1 | opioid receptor kappa 1 | 46.511 | 1.312 | Candidate only |
| `target:1774` | OPRK1 | opioid receptor kappa 1 | 45.212 | 9.418 | Candidate worth manual review |
| `target:15692` | RTCA | RNA 3'-terminal phosphate cyclase | 54.408 | 5.416 | Candidate worth manual review |
| `target:7213` | RASGRP2 | RAS guanyl releasing protein 2 | 28.907 | 0.260 | Low-margin candidate only |

## Compound Mapping Boundary

Compound nodes are harder than targets because the current artifact does not provide a SMILES/name/source-ID table. ChemBERTa-like vectors cannot be inverted into reliable compound identities.

Current compound status:

- `compound:761`, `compound:821`, `compound:480`, `compound:1073`, and other top-20 compound nodes remain graph-local IDs.
- No generated compound name should be used in the manuscript unless it is manually supported by an original ccTCM/ETCM/compound source row or another stable ID bridge.

Potential external resources for future manual curation:

- ccTCM: https://www.cctcm.org.cn/
- ETCM: https://academic.oup.com/nar/article/47/D1/D976/5144966
- PubChem PUG-REST: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest

These sources can support candidate search or external evidence, but they cannot by themselves prove that `compound:<local_id>` equals a specific molecule without a local ID bridge.

## Manuscript Use

Safe wording:

- "We extracted key mechanism subgraphs and quantified local sensitivity after masking component, target, and pathway features."
- "Compound and target IDs are graph-local identifiers. Human-readable target candidates were generated for manual triage using HGNC/BioBERT similarity, and are not treated as confirmed graph ID mappings."
- "External evidence review is performed only for selected candidates and does not upgrade evidence grade unless direct literature or database support is manually verified."

Unsafe wording:

- "PU-XMSAT identifies the exact active compound and target."
- "Target #15721 is VHLL."
- "Compound #821 is a known Crocus constituent."
- "The perturbation contribution proves the biological mechanism."

## Next Action

Use this audit to guide external evidence review:

1. Prioritize high-perturbation cases.
2. Prefer cases whose target candidates have higher margins and plausible biomedical relevance.
3. Do not select a case for a strong manuscript example solely because the perturbation score is high.
4. Keep at least one boundary case to explain why PU-XMSAT interpretability is mechanism triage rather than mechanism proof.
