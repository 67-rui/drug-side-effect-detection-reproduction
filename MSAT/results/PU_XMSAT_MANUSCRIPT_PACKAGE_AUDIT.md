# PU-XMSAT Manuscript Package Audit

**Generated at:** 2026-06-29T22:41:53.201583
**Overall status:** OK

## Package Location

- Manuscript source: `/Users/a67_2024/Desktop/drug-detect/Template/PU-XMSAT-Overleaf`
- Overleaf zip: `/Users/a67_2024/Desktop/drug-detect/Template/PU-XMSAT-Overleaf.zip`

## Summary

- Figures: 3
- Figure descriptions: 3
- Zip entries: 11
- PDF pages: 15
- PDF page size: 612 x 792 pts (letter)
- Failed checks: 0
- Warning checks: 1

## Checks

| Check | Status | Details |
| --- | --- | --- |
| `main_tex_exists` | pass | /Users/a67_2024/Desktop/drug-detect/Template/PU-XMSAT-Overleaf/main.tex |
| `documentclass_acm_review` | pass | options=['manuscript', 'review', 'screen'] |
| `required_source_files` | pass | all required source files present |
| `figure_files` | pass | figures=3 |
| `figure_descriptions` | pass | includegraphics=3, descriptions=3 |
| `zip_exists` | pass | /Users/a67_2024/Desktop/drug-detect/Template/PU-XMSAT-Overleaf.zip |
| `zip_required_entries` | pass | entries=11 |
| `zip_forbidden_entries` | pass | no preview/auxiliary files |
| `pdf_page_count` | pass | pages=15 |
| `pdf_letter_paper` | pass | 612 x 792 pts (letter) |
| `latex_log_clean` | pass | no LaTeX errors, undefined refs/citations, or overfull boxes |
| `human_submission_items` | warn | confirm_author_affiliation_email, confirm_acm_ccs, confirm_venue_metadata, confirm_ai_assistance_disclosure, confirm_funding_and_acknowledgments, confirm_double_blind_requirement |

## Pending Human Items

- `confirm_author_affiliation_email`
- `confirm_acm_ccs`
- `confirm_venue_metadata`
- `confirm_ai_assistance_disclosure`
- `confirm_funding_and_acknowledgments`
- `confirm_double_blind_requirement`

## Claim Boundaries To Preserve

Do not claim:

- full Table 5/6 reproduction;
- confirmed external validation of the current case studies;
- SHAP-equivalent or causal attribution from perturbation score drops;
- patient-level causal risk adjustment;
- broad mechanism validation beyond the final-checkpoint top-prediction cases that have explicit mechanism paths.

## Packaging Rule

Track the generated `Template/PU-XMSAT-Overleaf` source folder, `Template/PU-XMSAT-Overleaf.zip`, and this audit output.

Do not track:

- raw provided template files under `Template/文件*`;
- `.DS_Store`;
- `Template/PU-XMSAT-Overleaf/main.pdf`;
- LaTeX auxiliary files;
- unrelated shared archives such as `c8e3d252c197e482b037715c32fb3e70.zip`.

## Claim Boundary

This audit verifies package structure and template-facing checks only. It does not replace supervisor review, target-venue policy checks, or final author/metadata confirmation.
