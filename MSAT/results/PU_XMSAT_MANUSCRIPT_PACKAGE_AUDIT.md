# PU-XMSAT Manuscript Package Audit

**Date:** 2026-06-29
**Purpose:** Preserve the current paper package state outside the chat context and make the Overleaf manuscript handoff auditable.

## Package Location

The current English ACM-style manuscript source is:

- `Template/PU-XMSAT-Overleaf/main.tex`
- `Template/PU-XMSAT-Overleaf/references.bib`
- `Template/PU-XMSAT-Overleaf/acmart.cls`
- `Template/PU-XMSAT-Overleaf/figures/*.pdf`
- `Template/PU-XMSAT-Overleaf/tools/build_figures.py`
- `Template/PU-XMSAT-Overleaf/README.md`

The current Overleaf upload archive is:

- `Template/PU-XMSAT-Overleaf.zip`

The zip intentionally excludes `main.pdf` and LaTeX auxiliary files. Overleaf should compile `main.tex` from source.

## Current Manuscript State

The manuscript is an English ACM review-style draft using the provided `acmart.cls` template. It integrates:

1. the reproduced MSAT baseline and protocol boundary;
2. full-positive hybrid PU-XMSAT two-seed results;
3. PU weight sensitivity;
4. case evidence grading;
5. mechanism subgraph, local node/path perturbation, and aggregate sensitivity ranking;
6. causal-bias and validity boundaries.

Current strongest supported claim:

> Under the reproduced MSAT protocol, full-positive hybrid PU-XMSAT shows seed-robust gains over the reproduced MSAT baseline on AUC, F1, and MCC, with a stable positive but smaller AUPRC trend. The method also provides a conservative interpretation workflow combining mechanism subgraphs, local perturbation sensitivity, aggregate sensitivity ranking, evidence grading, and causal-bias claim boundaries.

## Template Compliance Snapshot

Verified on 2026-06-29:

- `latexmk -pdf -interaction=nonstopmode main.tex` exits 0.
- Rendered PDF has 12 pages.
- Page size is Letter: `612 x 792 pts`.
- Final log check found no `LaTeX Error`, undefined citations/references, or overfull boxes.
- Rendered checks of pages 7-10 showed no obvious overlap, clipped table text, or figure placement issue around the updated mechanism section.
- All manuscript figures include ACM `\Description{}` entries.

Known environment-only noise:

- MiKTeX may print locale/update warnings. These are local environment messages and are not manuscript errors.
- `pdftoppm` may print a Fontconfig config warning while still rendering PNG pages.

## Still Required Before Submission

The manuscript is not a final submission package until the student and supervisor confirm:

1. author names, affiliations, and corresponding author details;
2. target conference/journal metadata;
3. double-blind setting (`anonymous` option if required);
4. ACM CCS concepts;
5. funding and acknowledgments;
6. final generative-AI assistance disclosure;
7. venue-specific citation, page, and policy requirements.

## Claim Boundaries To Preserve

Do not claim:

- full Table 5/6 reproduction;
- confirmed external validation of the current case studies;
- SHAP-equivalent or causal attribution from perturbation score drops;
- patient-level causal risk adjustment;
- final full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint is exported and used for re-scoring.

## Packaging Rule

Track the generated `Template/PU-XMSAT-Overleaf` source folder and `Template/PU-XMSAT-Overleaf.zip`.

Do not track:

- raw provided template files under `Template/文件*`;
- `.DS_Store`;
- `Template/PU-XMSAT-Overleaf/main.pdf`;
- LaTeX auxiliary files;
- unrelated shared archives such as `c8e3d252c197e482b037715c32fb3e70.zip`.
