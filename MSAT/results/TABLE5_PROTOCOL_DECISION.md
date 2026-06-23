# Table 5 Protocol Decision

Last updated: 2026-06-23

## Current Decision

Use two Table 5 modes and label them explicitly:

| Mode | Purpose | Command | Citation status |
| --- | --- | --- | --- |
| `paper_3.5.6_global_top15_oof` | Closest paper-style diagnostic from 10-fold held-out predictions | `python scripts/run_table5_validation.py --summary results/summary.json` | Use for protocol comparison only |
| `predictor_global_top15` | Full-graph deployment-style ranking from one explicit checkpoint | `python scripts/run_table5_validation.py --use-predictor --checkpoint saved_models/best_model_for_prediction.pt` | Use for downstream case/table regeneration after checkpoint audit |

The current committed `table5_summary.json` is marked stale and must not be cited until regenerated with one of the modes above.

## Candidate Pool

Default pool: `exclude_all_graph_positives`.

Rationale: Table 5 is meant to surface high-confidence unknown CMM-ADR associations. Excluding all graph positives is stricter than excluding FAERS-only positives and avoids re-ranking known supervised edges.

Legacy diagnostic pool: `exclude_faers_only`.

Use this only when comparing against older internal runs. It is less strict and can mix known non-FAERS graph positives into the candidate set.

## Evidence Standard

The current reproduction cannot claim the paper's `13/15` Table 5 support unless the same validation evidence definition is available.

Allowed evidence labels:

- `database_verified`: only from an explicit local cache or source record that can be inspected.
- `mechanistic_support`: graph path evidence such as CMM -> compound -> target <- ADR.
- `paper_reference_diagnostic`: comparison against manually encoded paper rows, not independent validation.

Do not treat `mechanistic_support` alone as equivalent to TCMDA validation. It is useful explanatory support, not the same evidence channel.

## Output Requirements

Every regenerated Table 5 JSON must contain:

- `artifact_status.stale: false`
- `scoring_mode`
- `candidate_pool`
- `checkpoint` manifest when `--use-predictor` is used
- `input_summary` manifest when OOF summary mode is used
- `source_summary`
- `database_check`

The audit command should be run after regeneration:

```bash
python scripts/audit_reproduction_state.py --out results/reproduction_state_audit.json
```

## Publication Rule

For a paper-style report:

- Cite Table 2 and Fig.5a only from non-stale summaries.
- Cite Table 5 as a reproduction gap unless `database_verified` evidence is regenerated with an explicit source.
- Cite Table 6 only as downstream of the accepted Table 5 mode.
