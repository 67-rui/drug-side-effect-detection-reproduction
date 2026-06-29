# PU-XMSAT Submission Readiness Audit

**Generated at:** 2026-06-29T16:21:50.350959
Ready for submission: no

## Summary

- Package audit OK: True
- Machine check failures: 0
- Human blockers: 7

## Machine Checks

| Check | Status | Owner | Evidence | Action |
| --- | --- | --- | --- | --- |
| `package_audit_ok` | pass | codex | failed=0, warnings=1 | Run scripts/audit_manuscript_package.py and fix package failures. |
| `acm_review_documentclass` | pass | codex | options=['manuscript', 'review', 'screen'] | Use the provided acmart review manuscript documentclass. |
| `keywords_present` | pass | codex | keywords command found | Add target-venue appropriate keywords. |
| `ai_disclosure_section_present` | pass | codex | AI assistance section found | Add or confirm the venue-required AI assistance disclosure. |
| `acks_section_present` | pass | codex | acks environment found | Use the ACM acknowledgments environment if funding or institutional support is declared. |

## Human Blockers

| Item | Status | Owner | Evidence | Action |
| --- | --- | --- | --- | --- |
| `author_metadata` | blocked | student/supervisor | author, institution, or example email placeholders remain | Replace names, affiliations, cities/countries, emails, corresponding-author details, and shortauthors after supervisor confirmation. |
| `venue_metadata` | blocked | student/supervisor | conference/proceedings/DOI/ISBN placeholders remain | Fill venue, dates, location, DOI, ISBN, copyright, and ACM reference metadata from the target venue. |
| `ccs_confirmation` | blocked | student/supervisor | source still asks to verify ACM CCS concepts | Confirm CCS concepts with the ACM CCS tool and supervisor before submission. |
| `funding_acknowledgments` | blocked | student/supervisor | acknowledgments still contain TODO text | Replace the acknowledgments placeholder with final funding, institutional support, and supervisor acknowledgments, or remove it if not applicable. |
| `ai_disclosure_policy` | blocked | student/supervisor | AI assistance statement explicitly says it needs final venue-policy revision | Confirm whether the target venue requires, forbids, or provides specific wording for AI assistance disclosure. |
| `double_blind_policy` | blocked | student/supervisor | documentclass does not include anonymous; target review policy is not confirmed | If the target venue is double-blind, add anonymous and remove identifying metadata from the review version. |
| `reference_and_figure_scope` | blocked | student/supervisor | source TODO asks for target-venue figure/reference confirmation | Confirm whether references, figure styling, and scope satisfy supervisor and target-venue expectations. |

## Boundary

This audit separates machine-verifiable package checks from student/supervisor submission decisions. A clean package is not the same as final submission readiness.
