# PU-XMSAT Original Author Mapping Request

**Prepared:** 2026-06-29
**Purpose:** request the missing compound/target node mapping needed to interpret MSAT graph-local identifiers.

## Why This Is Needed

The public MSAT artifacts currently allow model reproduction and graph-level mechanism-path extraction, but they do not include a stable mapping from graph-local compound/target row indices to source entities.

The released `complete_hetero_graph.pt` contains:

- `herb.x`: 651 x 768 feature matrix
- `adr.x`: 5,974 x 768 feature matrix
- `target.x`: 21,393 x 768 feature matrix
- `compound.x`: 1,498 x 768 feature matrix
- typed edges such as `herb -> contains -> compound`, `target -> binds -> compound`, and `adr -> causes -> target`

However, the node stores contain only `x` tensors. They do not contain names, SMILES, PubChem CIDs, HGNC symbols, UniProt IDs, Open Targets IDs, or source database IDs.

Therefore graph-local identifiers such as `compound:761` and `target:15721` cannot be safely written as confirmed biological entities without the original node dictionary.

## Public Search Summary

- Zenodo record `10.5281/zenodo.17933842` currently lists only `complete_hetero_graph.pt`.
- GitHub repository `BowenShiGDPU/MSAT` currently lists code and `data/10fold_cv_split.pkl`; it does not include compound/target dictionaries.
- The Frontiers paper explains the source databases and embedding construction, but the public article page does not expose a compound/target local-index mapping file.

## Requested Files

The minimum useful files would be:

1. Compound node mapping:
   - local `compound` row index, zero-based if possible;
   - compound name;
   - PubChem CID;
   - canonical SMILES used for ChemBERTa embedding;
   - source database ID(s), such as ccTCM/ETCM/TCMSP if applicable.

2. Target node mapping:
   - local `target` row index, zero-based if possible;
   - HGNC symbol and/or approved name;
   - UniProt ID, Ensembl ID, Open Targets ID, or source database ID if available;
   - text string used for BioBERT embedding if applicable.

3. Optional but helpful:
   - herb and ADR mapping files used to create the final graph;
   - raw edge table before conversion to PyG `HeteroData`;
   - a note confirming whether node row order in `complete_hetero_graph.pt` matches the row order of the original entity tables.

## Additional Files Needed For Table 5 And Table 6 Reproduction

The same mapping gap also affects the paper's auxiliary validation and interpretation tables. To reproduce Table 5 and Table 6 as paper-equivalent artifacts, the following materials would be needed.

### Table 5

Table 5 is described as the Top-15 high-confidence CMM-ADR predictions absent from labeled positives and supported by external database/literature/mechanistic evidence. The currently public code does not include the exact Table 5 export workflow, so the following would be needed:

1. Exact Table 5 export script or notebook:
   - candidate enumeration;
   - candidate filtering;
   - ranking/sorting rule;
   - whether scores are from fold-level OOF predictions, a final full-graph predictor checkpoint, or another inference protocol.

2. Exact checkpoint/provenance:
   - checkpoint file(s) used to generate Table 5 predictions;
   - random seed and fold/protocol metadata;
   - whether the model used for Table 5 is one of the 10-fold checkpoints or a separately trained predictor checkpoint.

3. Candidate pool definition:
   - exact meaning of "not included among labeled positives";
   - whether exclusion removes FAERS positives only, all CMM-ADR graph positives, fold-specific train positives, or another label subset;
   - whether known literature/TCMDA edges are excluded from the candidate pool.

4. Row-level Table 5 data:
   - herb local ID, herb Chinese name, Latin name, and pinyin;
   - ADR local ID, MedDRA PT, MedDRA SOC if used;
   - prediction score and global rank;
   - database/literature/mechanistic support labels;
   - the exact source record or citation supporting each "supported" row.

5. Evidence verification materials:
   - TCMDA query terms and matched adverse phenotype strings;
   - literature search queries, URLs/PMIDs/DOIs, and manual review decisions;
   - mechanism-path evidence used to mark a row as mechanistically supported;
   - if applicable, supplementary validation sets for ranks 21-100 and 101-200.

### Table 6

Table 6 depends on Table 5 candidates and maps ADR terms to TCM functional systems. To reproduce it, the following would be needed:

1. Exact Table 6 input:
   - the final Table 5 rows used as input;
   - the ADR PT/SOC fields used for each row;
   - any normalization applied to MedDRA terms.

2. TCM functional-system mapping rules:
   - PT/SOC -> TCM functional system mapping table;
   - expert rule definitions for Zang-Fu/body-system assignments;
   - handling of ADRs that map to multiple systems;
   - MedDRA version used.

3. Table 6 script or notebook:
   - rule application order;
   - fallback behavior when a PT/SOC is not explicitly mapped;
   - final row-level TCM system labels.

4. If Table 6 uses case-level mechanistic interpretation:
   - compound and target mappings for the mechanism paths used in the discussion;
   - for the `Citrus aurantium` / Zhishi discussion, the graph-local compound node corresponding to nobiletin, the PubChem CID/SMILES, and the graph-local target node(s) corresponding to ABCG2/BCRP if applicable.

## Draft GitHub Issue

Title:

```text
Request for compound/target node mapping for complete_hetero_graph.pt
```

Body:

```markdown
Dear MSAT authors,

Thank you for releasing the MSAT code and Zenodo graph artifact. We are using the public `complete_hetero_graph.pt` to reproduce and extend the MSAT experiment, especially the mechanism-path interpretation layer.

We can load the graph and inspect the node/edge structure successfully. However, the public graph stores only feature tensors for `compound` and `target` nodes. For example:

- `compound.x`: 1,498 x 768
- `target.x`: 21,393 x 768
- node stores contain `x` only
- typed edges are available, but no source entity IDs are attached

For interpretation, we need to map graph-local identifiers such as `compound:761` and `target:15721` back to their original biological entities. The current Zenodo record appears to provide only `complete_hetero_graph.pt`, and the GitHub `data/` directory appears to provide only `10fold_cv_split.pkl`.

Would it be possible to share the entity mapping tables used to construct the graph?

The most useful files would be:

1. `compound` local row index -> compound name, PubChem CID, canonical SMILES, and source database ID(s).
2. `target` local row index -> HGNC symbol/name, UniProt/Open Targets/Ensembl/source ID(s), and the text string used for BioBERT embedding if available.
3. If available, the raw entity and edge tables before conversion into PyG `HeteroData`.

In addition, we are trying to understand the auxiliary Table 5 and Table 6 reproduction boundary. If possible, could you also share the materials used to generate those tables?

For Table 5:

- the exact export script or notebook;
- the checkpoint/protocol used for prediction;
- the precise candidate-pool definition for "not included among labeled positives";
- the row-level Top-15 data with herb IDs/names, ADR IDs/PTs, scores, ranks, and support labels;
- the evidence records behind database/literature/mechanistic support, including TCMDA query terms, matched phenotype strings, literature URLs/PMIDs/DOIs, and manual review decisions.

For Table 6:

- the exact Table 5 input rows used;
- the PT/SOC to TCM functional-system mapping table or rules;
- the MedDRA version used;
- the script/notebook applying the mapping;
- the final row-level TCM system labels.

If the Zhishi / `Citrus aurantium` case discussion uses specific graph nodes for nobiletin and ABCG2/BCRP, the corresponding compound and target local-node mappings would also be very helpful.

These mappings are important because without them we can only report compound/target IDs as graph-local row indices, not confirmed biological mechanisms.

Many thanks for your help and for making the MSAT resources available.
```

## Draft Email

Subject:

```text
Request for MSAT compound/target node mapping files
```

Body:

```text
Dear Professor Chen and Professor Yang,

I am working with the public MSAT code and Zenodo artifact for reproducing and extending the Chinese materia medica adverse-reaction prediction study. Thank you for making the model and graph artifact available.

I can load `complete_hetero_graph.pt` and reproduce the graph structure, including the compound and target node feature matrices and typed edges. However, I could not find the mapping from graph-local compound/target row indices to original biological entities in the public Zenodo record or GitHub repository.

For mechanism interpretation, this mapping is essential. At the moment, identifiers such as `compound:761` and `target:15721` can only be reported as local row indices. To interpret them biologically, we would need the original node dictionaries.

Would it be possible to share the following files or clarify whether they are available?

1. Compound node index -> compound name, PubChem CID, canonical SMILES, and source database ID(s), such as ccTCM/ETCM/TCMSP.
2. Target node index -> HGNC symbol/name, UniProt/Open Targets/Ensembl/source ID(s), and the text string used for BioBERT embedding if available.
3. If available, the raw entity and edge tables before conversion to PyG `HeteroData`.

I would also like to ask about the auxiliary Table 5 and Table 6 materials, because these tables are difficult to reproduce exactly from the currently public code and graph artifact.

For Table 5, would it be possible to share:

- the exact export script or notebook used to generate the Top-15 predictions;
- the checkpoint/protocol used for those predictions;
- the precise candidate-pool definition for "not included among labeled positives";
- row-level data including herb IDs/names, ADR IDs/PTs, prediction scores, ranks, and support labels;
- the external evidence records behind the support labels, including TCMDA query terms, matched adverse phenotype strings, literature URLs/PMIDs/DOIs, and manual review decisions.

For Table 6, would it be possible to share:

- the exact Table 5 input rows used;
- the MedDRA PT/SOC to TCM functional-system mapping rules or table;
- the MedDRA version used;
- the script/notebook used to apply the mapping;
- the final row-level TCM system labels.

If the Zhishi / `Citrus aurantium` case discussion uses specific graph nodes for nobiletin and ABCG2/BCRP, the corresponding compound and target local-node mappings would also be very helpful.

We would of course cite the MSAT paper and Zenodo record appropriately. The purpose is to avoid over-interpreting graph-local IDs and to make the mechanism explanation layer scientifically accurate.

Thank you very much for your time.

Best regards,
```
