# PU-XMSAT Overleaf Manuscript Draft

This folder is the Overleaf-ready LaTeX manuscript workspace for the PU-XMSAT paper.

The current manuscript is an English submission-oriented draft. Author names,
affiliations, conference/journal metadata, funding, and policy statements are
left as placeholders so that the student and supervisor can finalize them
collaboratively in Overleaf.

## Files

- `main.tex`: ACM-style English manuscript draft.
- `references.bib`: BibTeX references, including the original MSAT paper and core method references.
- `figures/*.pdf`: vector figures generated from `tools/build_figures.py`.
- `acmart.cls`: ACM class file copied from the provided template folder.
- `figures/`: place final figures here before Overleaf submission.
- `tools/build_figures.py`: reproducible figure builder for the current draft figures.

`main.pdf` is a local preview artifact and is not included in the Overleaf zip.
Use `PU-XMSAT-Overleaf.zip` for upload; Overleaf should compile the source files.

## Suggested Overleaf Setup

1. Upload the whole `PU-XMSAT-Overleaf` folder to Overleaf.
2. Set `main.tex` as the main document.
3. Compile with pdfLaTeX first. If the target venue requires another compiler, adjust after the draft compiles.
4. If the target venue is double-blind, add `anonymous` to the documentclass options:

```tex
\documentclass[manuscript,screen,review,anonymous]{acmart}
```

## Must-Fix Items Before Submission

See `MSAT/results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md` for the current machine-readable handoff checklist. The current package is compile/package-clean, but it is not final-submission-ready until the student and supervisor resolve those human blockers.

- Replace author, affiliation, email, conference, DOI, ISBN, and copyright placeholders.
- Check whether the current reference set is sufficient for the target venue and add domain-specific CMM safety references if requested by the supervisor.
- Verify ACM CCS concepts using the ACM CCS tool.
- Replace or polish the current vector figures if the supervisor wants journal-specific visual styling.
- Decide whether the `Declaration on Generative AI Assistance` wording matches the final venue policy.
- Keep the claims conservative: do not claim full Table 5/6 reproduction, confirmed external validation, SHAP-equivalent attribution, or causal effects.

## Template Compliance Notes

- The draft uses the provided ACM `acmart.cls` and the review manuscript mode recommended by the sample LaTeX template.
- The rendered PDF uses Letter paper and remains above the eight-page minimum in the provided checklist.
- All current figures and tables are referenced in the manuscript text.
- Figures contain English labels only and include ACM `\Description{}` text.
- The source files are kept ASCII-only for LaTeX portability.

## Current Scientific Claim Boundary

The draft supports this claim:

> Under the reproduced MSAT protocol, full-positive hybrid PU-XMSAT shows seed-robust gains over the reproduced MSAT baseline on AUC, F1, and MCC, with a stable positive but smaller AUPRC trend. The method also provides a conservative interpretation workflow combining mechanism subgraphs, local perturbation sensitivity, aggregate sensitivity ranking, evidence grading, and causal-bias claim boundaries.
