from __future__ import annotations

import argparse
import json
import re
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANUSCRIPT_DIR = REPO_ROOT / "Template" / "PU-XMSAT-Overleaf"
DEFAULT_ZIP_PATH = REPO_ROOT / "Template" / "PU-XMSAT-Overleaf.zip"

REQUIRED_BASE_ENTRIES = {
    "README.md",
    "acmart.cls",
    "main.tex",
    "references.bib",
    "tools/build_figures.py",
}
FORBIDDEN_ZIP_SUFFIXES = (
    ".aux",
    ".bbl",
    ".blg",
    ".cut",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdfsync",
    ".synctex.gz",
)
FORBIDDEN_ZIP_NAMES = {"main.pdf", "comment.cut"}
LOG_ERROR_PATTERNS = [
    "LaTeX Error",
    "Undefined control sequence",
    "undefined citations",
    "undefined references",
    "Overfull",
]


def _check(name: str, status: str, details: str = "") -> dict[str, str]:
    return {"name": name, "status": status, "details": details}


def parse_pdfinfo(text: str) -> dict[str, Any]:
    pages = None
    page_size = ""
    for line in text.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
        if line.startswith("Page size:"):
            page_size = line.split(":", 1)[1].strip()
    return {
        "pages": pages,
        "page_size": page_size,
        "is_letter": "letter" in page_size.lower() or "612 x 792" in page_size,
    }


def _run_pdfinfo(pdf_path: Path) -> str:
    if not pdf_path.exists():
        return ""
    completed = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout if completed.returncode == 0 else ""


def _read_optional(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def _included_figures(main_tex: str) -> list[str]:
    return re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", main_tex)


def _graphicspath_dirs(main_tex: str) -> list[str]:
    paths: list[str] = []
    for match in re.finditer(r"\\graphicspath\{((?:\{[^{}]+\})+)\}", main_tex):
        paths.extend(re.findall(r"\{([^{}]+)\}", match.group(1)))
    return paths


def _resolved_figure_entries(manuscript_dir: Path, main_tex: str) -> list[str]:
    entries: list[str] = []
    search_dirs = ["", *_graphicspath_dirs(main_tex)]
    for figure in _included_figures(main_tex):
        candidates = [figure] if "/" in figure else [f"{base}{figure}" for base in search_dirs]
        resolved = next((candidate for candidate in candidates if (manuscript_dir / candidate).exists()), candidates[0])
        entries.append(resolved)
    return entries


def _description_count(main_tex: str) -> int:
    return len(re.findall(r"\\Description\{", main_tex))


def _pending_items(main_tex: str) -> list[str]:
    pending = []
    first_line = main_tex.splitlines()[0] if main_tex.splitlines() else ""
    if re.search(r"First Author|Affiliation Placeholder|Institution Placeholder|email@example|TODO before formal submission", main_tex):
        pending.append("confirm_author_affiliation_email")
    if re.search(r"TODO CCS|CCS placeholder|\\ccsdesc\[500\]\{TODO", main_tex):
        pending.append("confirm_acm_ccs")
    if re.search(r"Conference Placeholder|DOI|ISBN|copyright", main_tex, re.IGNORECASE):
        pending.append("confirm_venue_metadata")
    if "Declaration on Generative AI Assistance" in main_tex:
        pending.append("confirm_ai_assistance_disclosure")
    if "TODO: Add funding" in main_tex:
        pending.append("confirm_funding_and_acknowledgments")
    if "anonymous" not in first_line:
        pending.append("confirm_double_blind_requirement")
    return pending


def _audit_source(manuscript_dir: Path, main_tex: str, checks: list[dict[str, str]]) -> dict[str, Any]:
    documentclass = re.search(r"\\documentclass\[([^\]]+)\]\{acmart\}", main_tex)
    if documentclass:
        options = {option.strip() for option in documentclass.group(1).split(",")}
        required = {"manuscript", "screen", "review"}
        missing = sorted(required - options)
        checks.append(
            _check(
                "documentclass_acm_review",
                "pass" if not missing else "fail",
                f"options={sorted(options)}" if not missing else f"missing={missing}",
            )
        )
    else:
        checks.append(_check("documentclass_acm_review", "fail", "missing acmart documentclass"))

    required_files = [
        manuscript_dir / "main.tex",
        manuscript_dir / "references.bib",
        manuscript_dir / "acmart.cls",
        manuscript_dir / "README.md",
        manuscript_dir / "tools" / "build_figures.py",
    ]
    missing_files = [str(path.relative_to(manuscript_dir)) for path in required_files if not path.exists()]
    checks.append(
        _check(
            "required_source_files",
            "pass" if not missing_files else "fail",
            "all required source files present" if not missing_files else f"missing={missing_files}",
        )
    )

    figures = _included_figures(main_tex)
    figure_entries = _resolved_figure_entries(manuscript_dir, main_tex)
    missing_figures = [figure for figure in figure_entries if not (manuscript_dir / figure).exists()]
    checks.append(
        _check(
            "figure_files",
            "pass" if figure_entries and not missing_figures else "fail",
            f"figures={len(figure_entries)}" if not missing_figures else f"missing={missing_figures}",
        )
    )

    descriptions = _description_count(main_tex)
    checks.append(
        _check(
            "figure_descriptions",
            "pass" if figures and descriptions >= len(figures) else "fail",
            f"includegraphics={len(figures)}, descriptions={descriptions}",
        )
    )
    return {"figure_count": len(figures), "description_count": descriptions}


def _audit_zip(
    manuscript_dir: Path,
    zip_path: Path,
    main_tex: str,
    checks: list[dict[str, str]],
) -> dict[str, Any]:
    if not zip_path.exists():
        checks.append(_check("zip_exists", "fail", str(zip_path)))
        return {"zip_entry_count": 0, "zip_entries": []}
    with zipfile.ZipFile(zip_path) as zf:
        entries = sorted(info.filename for info in zf.infolist())
    checks.append(_check("zip_exists", "pass", str(zip_path)))

    figure_entries = set(_resolved_figure_entries(manuscript_dir, main_tex))
    required_entries = REQUIRED_BASE_ENTRIES | figure_entries
    missing_entries = sorted(required_entries - set(entries))
    checks.append(
        _check(
            "zip_required_entries",
            "pass" if not missing_entries else "fail",
            f"entries={len(entries)}" if not missing_entries else f"missing={missing_entries}",
        )
    )

    forbidden = [
        entry
        for entry in entries
        if Path(entry).name in FORBIDDEN_ZIP_NAMES or entry.endswith(FORBIDDEN_ZIP_SUFFIXES)
    ]
    checks.append(
        _check(
            "zip_forbidden_entries",
            "pass" if not forbidden else "fail",
            "no preview/auxiliary files" if not forbidden else f"forbidden={forbidden}",
        )
    )
    return {"zip_entry_count": len(entries), "zip_entries": entries}


def _audit_pdf(pdfinfo_text: str, checks: list[dict[str, str]]) -> dict[str, Any]:
    parsed = parse_pdfinfo(pdfinfo_text) if pdfinfo_text else {"pages": None, "page_size": "", "is_letter": False}
    pages = parsed["pages"]
    checks.append(
        _check(
            "pdf_page_count",
            "pass" if isinstance(pages, int) and pages >= 8 else "warn",
            f"pages={pages}" if pages else "main.pdf or pdfinfo unavailable",
        )
    )
    checks.append(
        _check(
            "pdf_letter_paper",
            "pass" if parsed["is_letter"] else "warn",
            parsed["page_size"] or "main.pdf or pdfinfo unavailable",
        )
    )
    return parsed


def _audit_log(log_text: str, checks: list[dict[str, str]]) -> None:
    if not log_text:
        checks.append(_check("latex_log_clean", "warn", "main.log unavailable; compile before final submission"))
        return
    matches = [pattern for pattern in LOG_ERROR_PATTERNS if pattern.lower() in log_text.lower()]
    checks.append(
        _check(
            "latex_log_clean",
            "pass" if not matches else "fail",
            "no LaTeX errors, undefined refs/citations, or overfull boxes" if not matches else f"matched={matches}",
        )
    )


def audit_manuscript_package(
    manuscript_dir: str | Path = DEFAULT_MANUSCRIPT_DIR,
    zip_path: str | Path = DEFAULT_ZIP_PATH,
    pdfinfo_text: str | None = None,
    log_text: str | None = None,
) -> dict[str, Any]:
    manuscript_dir = Path(manuscript_dir)
    zip_path = Path(zip_path)
    main_tex_path = manuscript_dir / "main.tex"
    main_tex = _read_optional(main_tex_path)
    checks: list[dict[str, str]] = []

    if not main_tex:
        checks.append(_check("main_tex_exists", "fail", str(main_tex_path)))
        main_tex = ""
    else:
        checks.append(_check("main_tex_exists", "pass", str(main_tex_path)))

    source_summary = _audit_source(manuscript_dir, main_tex, checks)
    zip_summary = _audit_zip(manuscript_dir, zip_path, main_tex, checks)
    pdf_summary = _audit_pdf(
        pdfinfo_text if pdfinfo_text is not None else _run_pdfinfo(manuscript_dir / "main.pdf"),
        checks,
    )
    _audit_log(log_text if log_text is not None else _read_optional(manuscript_dir / "main.log"), checks)

    pending = _pending_items(main_tex)
    checks.append(
        _check(
            "human_submission_items",
            "warn" if pending else "pass",
            ", ".join(pending) if pending else "no obvious placeholders found",
        )
    )

    failed = [check for check in checks if check["status"] == "fail"]
    warnings = [check for check in checks if check["status"] == "warn"]
    return {
        "created_at": datetime.now().isoformat(),
        "ok": not failed,
        "manuscript_dir": str(manuscript_dir),
        "zip_path": str(zip_path),
        "summary": {
            **source_summary,
            **zip_summary,
            "page_count": pdf_summary["pages"],
            "page_size": pdf_summary["page_size"],
            "failed_check_count": len(failed),
            "warning_check_count": len(warnings),
        },
        "pending_human_items": pending,
        "checks": checks,
    }


def write_audit_outputs(audit: dict[str, Any], output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2))

    lines = [
        "# PU-XMSAT Manuscript Package Audit",
        "",
        f"**Generated at:** {audit['created_at']}",
        f"**Overall status:** {'OK' if audit['ok'] else 'Needs fixes'}",
        "",
        "## Package Location",
        "",
        f"- Manuscript source: `{audit['manuscript_dir']}`",
        f"- Overleaf zip: `{audit['zip_path']}`",
        "",
        "## Summary",
        "",
        f"- Figures: {audit['summary'].get('figure_count')}",
        f"- Figure descriptions: {audit['summary'].get('description_count')}",
        f"- Zip entries: {audit['summary'].get('zip_entry_count')}",
        f"- PDF pages: {audit['summary'].get('page_count')}",
        f"- PDF page size: {audit['summary'].get('page_size')}",
        f"- Failed checks: {audit['summary'].get('failed_check_count')}",
        f"- Warning checks: {audit['summary'].get('warning_check_count')}",
        "",
        "## Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    for check in audit["checks"]:
        details = str(check.get("details", "")).replace("|", "\\|")
        lines.append(f"| `{check['name']}` | {check['status']} | {details} |")

    lines.extend(["", "## Pending Human Items", ""])
    if audit["pending_human_items"]:
        lines.extend(f"- `{item}`" for item in audit["pending_human_items"])
    else:
        lines.append("- None detected.")

    lines.extend(
        [
            "",
            "## Claim Boundaries To Preserve",
            "",
            "Do not claim:",
            "",
            "- full Table 5/6 reproduction;",
            "- confirmed external validation of the current case studies;",
            "- SHAP-equivalent or causal attribution from perturbation score drops;",
            "- patient-level causal risk adjustment;",
            "- final full-positive hybrid PU-XMSAT checkpoint attribution unless an explicit PU predictor checkpoint is exported and used for re-scoring.",
            "",
            "## Packaging Rule",
            "",
            "Track the generated `Template/PU-XMSAT-Overleaf` source folder, `Template/PU-XMSAT-Overleaf.zip`, and this audit output.",
            "",
            "Do not track:",
            "",
            "- raw provided template files under `Template/文件*`;",
            "- `.DS_Store`;",
            "- `Template/PU-XMSAT-Overleaf/main.pdf`;",
            "- LaTeX auxiliary files;",
            "- unrelated shared archives such as `c8e3d252c197e482b037715c32fb3e70.zip`.",
            "",
            "## Claim Boundary",
            "",
            "This audit verifies package structure and template-facing checks only. It does not replace supervisor review, target-venue policy checks, or final author/metadata confirmation.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the PU-XMSAT Overleaf manuscript package")
    parser.add_argument("--manuscript-dir", default=str(DEFAULT_MANUSCRIPT_DIR))
    parser.add_argument("--zip-path", default=str(DEFAULT_ZIP_PATH))
    parser.add_argument("--output-json", default="results/manuscript_package_audit.json")
    parser.add_argument("--output-md", default="results/PU_XMSAT_MANUSCRIPT_PACKAGE_AUDIT.md")
    args = parser.parse_args()

    audit = audit_manuscript_package(args.manuscript_dir, args.zip_path)
    write_audit_outputs(audit, Path(args.output_json), Path(args.output_md))
    print(json.dumps({"ok": audit["ok"], "summary": audit["summary"]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if audit["ok"] else 1)


if __name__ == "__main__":
    main()
