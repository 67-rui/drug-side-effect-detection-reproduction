# Table 5 Protocol Decision

Last updated: 2026-06-24

## Current Decision

Table 5 must be reported as a **separate external-validation task**, not as a pure training metric. The current code can generate ranked predictions, but the paper's `13/15` support rate depends on two evidence channels from §3.5.6:

1. TCMDA database verification.
2. Literature or mechanistic support.

The current committed `table5_summary.json` is valid and non-stale, but it **does not reproduce the paper's support rate**:

| File | Mode | Candidate pool | Current support |
| --- | --- | --- | --- |
| `results/table5_summary.json` | `predictor` | `exclude_all_graph_positives` | `1/15 = 6.7%` |
| `results/table5_literature_evidence_candidates.json` | PubMed/OpenAlex candidate scan | current Top-15 | `63` review candidates, `0` exact herb+ADR hits |

Therefore Table 5 should be cited as a reproduction gap until the evidence cache is filled from explicit database/literature sources.

## Accepted Table 5 Modes

| Mode | Purpose | Command | Citation status |
| --- | --- | --- | --- |
| `oof_pooled` | Paper-style held-out diagnostic from `summary.json` fold predictions | `python scripts/run_table5_validation.py --summary results/summary.json` | Use for protocol diagnostics |
| `predictor` | Deployment-style full graph ranking from an explicit checkpoint | `python scripts/run_table5_validation.py --use-predictor --checkpoint saved_models/best_model_for_prediction.pt` | Use for the current downstream Table 5/6 workflow |

The current result uses `predictor` mode because Phase 9 downstream artifacts require a concrete checkpoint manifest.

## Candidate Pool

Default pool: `exclude_all_graph_positives`.

Rationale: Table 5 should surface high-confidence CMM-ADR associations absent from the full supervision graph. Excluding all graph positives is stricter than excluding only FAERS positives and avoids re-ranking known supervised edges.

Legacy pool: `exclude_faers_only`.

Use this only as a diagnostic when comparing older runs. It can include literature-positive graph edges and is less conservative.

## Evidence Standard

Allowed evidence labels:

| Label | Required source |
| --- | --- |
| `database_verified` | A row in `data/tcmda_cache.json` whose `adverse_phenotypes` matches the predicted MedDRA PT or a documented synonym |
| `mechanistic_support` | A visible graph path such as CMM -> compound -> target <- ADR, or a manually cited literature mechanism recorded in `notes` |
| `literature_candidate` | A PubMed/OpenAlex/Crossref record in `results/table5_literature_evidence_candidates.*`; this is only a screening candidate until manually reviewed |
| `paper_reference_diagnostic` | Comparison against `data/paper_table5_reference.json`; useful for diagnosis but not independent validation |

Do not treat mechanistic graph paths alone as equivalent to TCMDA. For a paper-style claim, each supported row must expose the evidence source in the JSON/CSV output.

Do not treat `literature_candidate` rows as verified support by default. The current automated scan keeps records that match the herb or ADR text and marks every row with `manual_review_required: true` and `verified_support: false`.

## Step-by-Step Reproduction

1. Generate the current Top-15 candidate list:

```bash
cd /Users/a67_2024/Desktop/drug-detect/MSAT
python scripts/run_table5_validation.py \
  --use-predictor \
  --checkpoint saved_models/best_model_for_prediction.pt
```

Expected outputs:

- `results/table5_top15.csv`
- `results/table5_summary.json`

2. Create or refresh the manual TCMDA cache template from the Top-15:

```bash
python scripts/import_tcmda_cache.py \
  --input results/table5_top15.csv \
  --out data/tcmda_cache.json
```

This produces one cache row per Table 5 prediction. For each row, inspect TCMDA and write the observed adverse phenotypes into `adverse_phenotypes`.

3. Generate public literature screening candidates:

```bash
python scripts/fetch_table5_literature_evidence.py \
  --max-query-variants 1 \
  --max-results-per-provider 5 \
  --include-toxicity-fallback
```

Expected outputs:

- `results/table5_literature_evidence_candidates.csv`
- `results/table5_literature_evidence_candidates.json`
- `data/table5_literature_cache.json`

Use `--offline` to rebuild the output from the cached API responses without hitting PubMed/OpenAlex again. Crossref is supported but opt-in because it can be slow:

```bash
python scripts/fetch_table5_literature_evidence.py \
  --providers pubmed,openalex,crossref \
  --include-toxicity-fallback
```

Current scan result: 63 retained candidates, all requiring manual review; 0 records matched both herb text and the predicted ADR PT.

4. For each row in `data/tcmda_cache.json`, fill these fields:

```json
{
  "herb_query": "野草莓",
  "herb_aliases": ["野草莓", "Fragaria vesca?L.", "YE CAO MEI"],
  "adverse_phenotypes": ["Altered state of consciousness", "意识状态改变"],
  "source_url": "https://organchem.csdb.cn/scdb/Tcm_Multi/Tox_eff_query2.asp",
  "notes": "Manual TCMDA lookup; match accepted as direct PT/synonym support.",
  "predicted_adr_pt": "Altered state of consciousness",
  "verified_at": "2026-06-24",
  "verified_by": "manual_tcmda_review"
}
```

Use the actual TCMDA phenotype text. If no database support is found, leave `adverse_phenotypes` empty and record the query in `notes`.

5. Re-run Table 5 using the filled cache:

```bash
python scripts/run_table5_validation.py \
  --use-predictor \
  --checkpoint saved_models/best_model_for_prediction.pt \
  --tcmda-cache data/tcmda_cache.json
```

6. Regenerate Table 6 from the accepted Table 5 CSV:

```bash
python scripts/run_table6_mapping.py \
  --input results/table5_top15.csv \
  --out results/table6_mapping.csv
```

7. Audit the artifacts:

```bash
python scripts/audit_reproduction_state.py \
  --out results/reproduction_state_audit.json \
  --fail-on-error
```

Expected audit condition:

- `issues: []`
- `table5_summary.json` has `artifact_status.stale: false`
- `table5_summary.json` has `checkpoint.exists: true`
- `table5_summary.json` has `database_check` pointing to the cache path

8. Report the result honestly:

- If support remains far below `13/15`, report Table 5 as **not reproduced** and include the current support rate.
- If support approaches the paper claim, attach the cache and note which rows were database-supported, mechanistically supported, or unsupported.

## Publication Rule

For a paper-style report:

- Cite Table 2, Table 4 MSAT, Fig.5a, and Fig.6 AUC/AUPRC from non-stale summaries.
- Cite Table 5 only after evidence rows are manually or programmatically inspectable.
- Cite Table 6 as downstream of the accepted Table 5 mode and include the mapping rules.
