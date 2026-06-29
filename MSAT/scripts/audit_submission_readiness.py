from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANUSCRIPT_DIR = REPO_ROOT / "Template" / "PU-XMSAT-Overleaf"
DEFAULT_PACKAGE_AUDIT = REPO_ROOT / "MSAT" / "results" / "manuscript_package_audit.json"
DEFAULT_OUTPUT_JSON = Path("results/submission_readiness_audit.json")
DEFAULT_OUTPUT_MD = Path("results/PU_XMSAT_SUBMISSION_READINESS_AUDIT.md")


def _read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def _status_item(item_id: str, status: str, owner: str, evidence: str, action: str) -> dict[str, str]:
    return {
        "id": item_id,
        "status": status,
        "owner": owner,
        "evidence": evidence,
        "action": action,
    }


def _documentclass_options(main_tex: str) -> set[str]:
    match = re.search(r"\\documentclass\[([^\]]+)\]\{acmart\}", main_tex)
    if not match:
        return set()
    return {option.strip() for option in match.group(1).split(",")}


def _load_package_audit(package_audit: dict[str, Any] | str | Path | None) -> dict[str, Any]:
    if isinstance(package_audit, dict):
        return package_audit
    path = Path(package_audit) if package_audit is not None else DEFAULT_PACKAGE_AUDIT
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _machine_checks(main_tex: str, package_audit: dict[str, Any]) -> list[dict[str, str]]:
    package_ok = bool(package_audit.get("ok"))
    package_summary = package_audit.get("summary", {})
    options = _documentclass_options(main_tex)
    required_options = {"manuscript", "screen", "review"}
    missing_options = sorted(required_options - options)

    return [
        _status_item(
            "package_audit_ok",
            "pass" if package_ok else "fail",
            "codex",
            f"failed={package_summary.get('failed_check_count')}, warnings={package_summary.get('warning_check_count')}",
            "Run scripts/audit_manuscript_package.py and fix package failures.",
        ),
        _status_item(
            "acm_review_documentclass",
            "pass" if options and not missing_options else "fail",
            "codex",
            f"options={sorted(options)}" if options else "missing acmart documentclass",
            "Use the provided acmart review manuscript documentclass.",
        ),
        _status_item(
            "keywords_present",
            "pass" if re.search(r"\\keywords\{[^}]+\}", main_tex) else "fail",
            "codex",
            "keywords command found" if "\\keywords{" in main_tex else "missing keywords command",
            "Add target-venue appropriate keywords.",
        ),
        _status_item(
            "ai_disclosure_section_present",
            "pass" if "Declaration on Generative AI Assistance" in main_tex else "fail",
            "codex",
            "AI assistance section found" if "Declaration on Generative AI Assistance" in main_tex else "missing AI assistance section",
            "Add or confirm the venue-required AI assistance disclosure.",
        ),
        _status_item(
            "acks_section_present",
            "pass" if "\\begin{acks}" in main_tex and "\\end{acks}" in main_tex else "warn",
            "codex",
            "acks environment found" if "\\begin{acks}" in main_tex else "acks environment missing",
            "Use the ACM acknowledgments environment if funding or institutional support is declared.",
        ),
    ]


def _human_blockers(main_tex: str) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if re.search(
        r"First Author|Second Author|Corresponding Author|Institution Placeholder|example\.com",
        main_tex,
    ):
        blockers.append(
            _status_item(
                "author_metadata",
                "blocked",
                "student/supervisor",
                "author, institution, or example email placeholders remain",
                "Replace names, affiliations, cities/countries, emails, corresponding-author details, and shortauthors after supervisor confirmation.",
            )
        )
    if re.search(
        r"Conference Placeholder|Proceedings Placeholder|Month DD|City, Country|0000000|978-1-4503-0000",
        main_tex,
    ):
        blockers.append(
            _status_item(
                "venue_metadata",
                "blocked",
                "student/supervisor",
                "conference/proceedings/DOI/ISBN placeholders remain",
                "Fill venue, dates, location, DOI, ISBN, copyright, and ACM reference metadata from the target venue.",
            )
        )
    if re.search(r"TODO[^\n]*CCS|verified ACM CCS|CCS placeholders?", main_tex, re.IGNORECASE):
        blockers.append(
            _status_item(
                "ccs_confirmation",
                "blocked",
                "student/supervisor",
                "source still asks to verify ACM CCS concepts",
                "Confirm CCS concepts with the ACM CCS tool and supervisor before submission.",
            )
        )
    if re.search(r"TODO: Add funding|Add funding|supervisor acknowledgements", main_tex):
        blockers.append(
            _status_item(
                "funding_acknowledgments",
                "blocked",
                "student/supervisor",
                "acknowledgments still contain TODO text",
                "Replace the acknowledgments placeholder with final funding, institutional support, and supervisor acknowledgments, or remove it if not applicable.",
            )
        )
    if re.search(r"should be revised to match the final venue policy|final venue policy", main_tex):
        blockers.append(
            _status_item(
                "ai_disclosure_policy",
                "blocked",
                "student/supervisor",
                "AI assistance statement explicitly says it needs final venue-policy revision",
                "Confirm whether the target venue requires, forbids, or provides specific wording for AI assistance disclosure.",
            )
        )

    options = _documentclass_options(main_tex)
    if "anonymous" not in options:
        blockers.append(
            _status_item(
                "double_blind_policy",
                "blocked",
                "student/supervisor",
                "documentclass does not include anonymous; target review policy is not confirmed",
                "If the target venue is double-blind, add anonymous and remove identifying metadata from the review version.",
            )
        )
    if "Confirm whether the current figures and references satisfy the target venue" in main_tex:
        blockers.append(
            _status_item(
                "reference_and_figure_scope",
                "blocked",
                "student/supervisor",
                "source TODO asks for target-venue figure/reference confirmation",
                "Confirm whether references, figure styling, and scope satisfy supervisor and target-venue expectations.",
            )
        )
    return blockers


def audit_submission_readiness(
    manuscript_dir: str | Path = DEFAULT_MANUSCRIPT_DIR,
    package_audit: dict[str, Any] | str | Path | None = None,
) -> dict[str, Any]:
    manuscript_dir = Path(manuscript_dir)
    main_tex_path = manuscript_dir / "main.tex"
    main_tex = _read_text(main_tex_path)
    package_payload = _load_package_audit(package_audit)
    machine_checks = _machine_checks(main_tex, package_payload)
    human_blockers = _human_blockers(main_tex)
    machine_fail_count = sum(1 for item in machine_checks if item["status"] == "fail")
    package_ok = bool(package_payload.get("ok"))
    ready = package_ok and machine_fail_count == 0 and not human_blockers
    return {
        "experiment": "submission_readiness_audit",
        "created_at": datetime.now().isoformat(),
        "manuscript_dir": str(manuscript_dir),
        "main_tex": str(main_tex_path),
        "ready_for_submission": ready,
        "summary": {
            "package_ok": package_ok,
            "machine_check_count": len(machine_checks),
            "machine_fail_count": machine_fail_count,
            "human_blocker_count": len(human_blockers),
        },
        "machine_checks": machine_checks,
        "human_blockers": human_blockers,
        "claim_boundary": (
            "This audit separates machine-verifiable package checks from "
            "student/supervisor submission decisions. A clean package is not the "
            "same as final submission readiness."
        ),
    }


def write_readiness_outputs(audit: dict[str, Any], output_json: str | Path, output_md: str | Path) -> None:
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2))

    ready_text = "yes" if audit["ready_for_submission"] else "no"
    lines = [
        "# PU-XMSAT Submission Readiness Audit",
        "",
        f"**Generated at:** {audit['created_at']}",
        f"Ready for submission: {ready_text}",
        "",
        "## Summary",
        "",
        f"- Package audit OK: {audit['summary']['package_ok']}",
        f"- Machine check failures: {audit['summary']['machine_fail_count']}",
        f"- Human blockers: {audit['summary']['human_blocker_count']}",
        "",
        "## Machine Checks",
        "",
        "| Check | Status | Owner | Evidence | Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in audit["machine_checks"]:
        lines.append(
            f"| `{item['id']}` | {item['status']} | {item['owner']} | {item['evidence']} | {item['action']} |"
        )

    lines.extend(
        [
            "",
            "## Human Blockers",
            "",
            "| Item | Status | Owner | Evidence | Action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if audit["human_blockers"]:
        for item in audit["human_blockers"]:
            lines.append(
                f"| `{item['id']}` | {item['status']} | {item['owner']} | {item['evidence']} | {item['action']} |"
            )
    else:
        lines.append("| None | pass | student/supervisor | no blockers detected | proceed to final venue checklist |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            audit["claim_boundary"],
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit final submission readiness for the PU-XMSAT manuscript")
    parser.add_argument("--manuscript-dir", default=str(DEFAULT_MANUSCRIPT_DIR))
    parser.add_argument("--package-audit", default=str(DEFAULT_PACKAGE_AUDIT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    audit = audit_submission_readiness(args.manuscript_dir, args.package_audit)
    write_readiness_outputs(audit, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "ready_for_submission": audit["ready_for_submission"],
                "summary": audit["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.fail_on_blocker and not audit["ready_for_submission"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
