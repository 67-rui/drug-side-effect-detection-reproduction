# PU-XMSAT Manuscript Claim Audit

**Generated:** 2026-06-30
**Manuscript source:** `Template/PU-XMSAT-Overleaf/main.tex`
**Claim boundary:** PU-XMSAT should be presented as a positive-unlabeled CMM-ADR prediction framework with checkpoint-aware mechanism triage and evidence-aware candidate prioritization.

## Section-Level Review

| Section | Audit result | Required boundary |
| --- | --- | --- |
| Abstract | Revised to state PU learning, checkpoint-aware mechanism triage, and evidence-aware candidate prioritization. | Do not imply case-level external validation or causal effect estimation. |
| Introduction | Supported after retaining the reproduced MSAT anchor and incomplete-label motivation. | Do not claim complete Table 5/6 reproduction or clinical validation. |
| Research Questions | Revised RQ4/RQ5 to mechanism triage and manual evidence prioritization. | Keep strongest claims on RQ1/RQ2; keep RQ4/RQ5 as triage/review boundaries. |
| Methods | Supported. PU construction, cluster-heldout, perturbation sensitivity, evidence grading, and causal-bias limits are separated. | Perturbation scores are local sensitivity only. |
| Results | Supported with boundaries. Main performance, cluster-heldout stress test, mechanism coverage, and case triage are separated. | Do not upgrade top30 literature signals to validation. |
| Discussion | Supported. Practical use is framed as risk prioritization and manual review support. | No strong mechanism proof, no SHAP-equivalent explanation, no causal attribution. |
| Limitations | Supported and explicit. | Keep compound/target IDs as graph-local unless an original mapping is recovered. |
| Conclusion | Revised to the unified manuscript line. | Conclusion must remain conservative and match evidence sources. |

## Claim-to-Evidence Matrix

| Claim | Status | Evidence source file | Allowed wording | Forbidden wording |
| --- | --- | --- | --- | --- |
| PU-XMSAT improves incomplete-label supervision. | supported | `results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md`; `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`; `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv` | "PU-XMSAT mitigates the closed-world negative-label assumption by separating observed positives, reliable negatives, and down-weighted unlabeled pairs under the reproduced MSAT protocol." | "PU-XMSAT proves all unobserved pairs are mislabeled" or "PU-XMSAT eliminates label noise." |
| Hybrid strategy improves over random PU sampling. | supported | `results/pu_xmsat_hybrid_vs_random_seed2026_comparison.csv`; `results/PU_XMSAT_PUBLICATION_EVIDENCE_CONSOLIDATION.md` | "The full-positive hybrid strategy outperformed the random PU comparator on AUC, F1, and MCC in the seed-2026 strategy comparison; AUPRC was positive but smaller." | "Hybrid is universally superior to all negative-sampling strategies." |
| Two-seed robustness. | supported | `results/pu_xmsat_hybrid_seed_robustness_summary.csv`; `results/pu_xmsat_hybrid_seed2026_baseline_comparison.csv`; `results/pu_xmsat_hybrid_seed1337_baseline_comparison.csv` | "Hybrid PU-XMSAT showed stable two-seed performance, with consistent AUC/F1/MCC gains and a positive but smaller AUPRC trend." | "The method is fully insensitive to random seeds" or "all stochastic variation has been exhausted." |
| Cluster-heldout stress test. | partially supported | `results/PU_XMSAT_CLUSTER_HOLDOUT_GENERALIZATION.md`; `results/cluster_holdout_generalization_summary.json` | "Cluster-heldout evaluation retained ranking signal but showed weak thresholded F1/MCC, so it is a stricter new-cluster stress test." | "PU-XMSAT generalizes successfully to all unseen CMM clusters" or "cluster-heldout is external clinical validation." |
| Mechanism-path extraction and perturbation sensitivity. | partially supported | `results/PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY_TOP5000_RANDOM_CONTROLS.md`; `results/PU_XMSAT_CONTRIBUTION_QUANTIFICATION_TOP5000_RANDOM_CONTROLS.md`; `results/PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY_TOP5000_RANDOM_CONTROLS.md`; `results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER_TOP5000_RANDOM_CONTROLS.md` | "The final checkpoint top5000 export produced 391 explicit-path candidates, and 20 mechanism-supported cases were quantified with local node/path perturbation sensitivity and random controls." | "Strong mechanistic validation", "causal contribution", "SHAP-like explanation", or "confirmed biological mechanism." |
| Evidence-aware candidate prioritization. | supported | `results/PU_XMSAT_EVIDENCE_AWARE_MECHANISM_CANDIDATE_QUEUE.md`; `results/PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`; `results/PU_XMSAT_TOP30_MANUAL_EVIDENCE_REVIEW.md`; `results/top30_manual_evidence_review.csv` | "The 391 explicit-path pool was reranked into an evidence-aware top30 manual-review queue; current evidence supports prioritization, not confirmation." | "The top30 queue is externally validated" or "automated PubMed hits are Grade A/B evidence." |
| External validation boundary. | supported as a negative/boundary claim | `results/PU_XMSAT_TOP20_EXTERNAL_EVIDENCE_REVIEW.md`; `results/PU_XMSAT_EVIDENCE_AWARE_LITERATURE_SIGNAL_REVIEW.md`; `results/PU_XMSAT_CASE_STUDY_TRIAGE_TABLE.md`; `results/PU_XMSAT_TOP30_MANUAL_EVIDENCE_REVIEW.md` | "No current case provides a complete externally validated herb-compound-target-ADR chain; Polypodium is moderate indirect GI-direction evidence, Marchantia liver injury is direction-conflict evidence, and Fragaria is a boundary case." | "Clinical external validation", "confirmed ADR case", "Table 5/6 equivalent reproduction", or "direct species-target-ADR validation." |
| Causal/confounding boundary. | supported as a limitation | `results/PU_XMSAT_CAUSAL_BIAS_FRAMEWORK.md`; `Template/PU-XMSAT-Overleaf/main.tex` | "Current graph data support incomplete-label mitigation but not adjustment for co-medication, indication, exposure denominator, dose, preparation quality, or reporting propensity." | "Causal effect", "patient-level causal adjustment", "controlled confounding", or "causal transportability." |

## Manuscript Wording Decision

Use this manuscript line consistently:

> PU-XMSAT is a positive-unlabeled CMM-ADR prediction framework with checkpoint-aware mechanism triage and evidence-aware candidate prioritization.

Do not replace it with stronger terms such as "mechanistic validation", "clinical validation", "SHAP explanation", "causal effect estimation", or "confirmed compound/target mechanism".
