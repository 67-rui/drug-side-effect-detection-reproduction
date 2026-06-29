import zipfile
from pathlib import Path

from scripts.audit_manuscript_package import (
    audit_manuscript_package,
    parse_pdfinfo,
    write_audit_outputs,
)


def _write_minimal_manuscript(root: Path) -> tuple[Path, Path]:
    manuscript = root / "Template" / "PU-XMSAT-Overleaf"
    figures = manuscript / "figures"
    figures.mkdir(parents=True)
    (manuscript / "tools").mkdir()
    (figures / "method_overview.pdf").write_bytes(b"%PDF-1.4\n")
    (figures / "metric_delta.pdf").write_bytes(b"%PDF-1.4\n")
    (manuscript / "main.tex").write_text(
        "\n".join(
            [
                r"\documentclass[manuscript,screen,review]{acmart}",
                r"% TODO before formal submission: replace author metadata and CCS placeholders.",
                r"\begin{document}",
                r"\begin{figure}",
                r"\includegraphics{figures/method_overview.pdf}",
                r"\Description{Method overview.}",
                r"\end{figure}",
                r"\begin{figure}",
                r"\includegraphics{figures/metric_delta.pdf}",
                r"\Description{Metric delta chart.}",
                r"\end{figure}",
                r"\ccsdesc[500]{TODO CCS placeholder}",
                r"\author{First Author}",
                r"\affiliation{\institution{Institution Placeholder}}",
                r"\email{email@example.edu}",
                r"\end{document}",
            ]
        )
    )
    (manuscript / "references.bib").write_text("@article{unit,title={Unit}}\n")
    (manuscript / "acmart.cls").write_text("% class\n")
    (manuscript / "README.md").write_text("README\n")
    (manuscript / "tools" / "build_figures.py").write_text("print('ok')\n")

    archive = root / "Template" / "PU-XMSAT-Overleaf.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for path in [
            "main.tex",
            "references.bib",
            "acmart.cls",
            "README.md",
            "figures/method_overview.pdf",
            "figures/metric_delta.pdf",
            "tools/build_figures.py",
        ]:
            zf.write(manuscript / path, path)
    return manuscript, archive


def test_parse_pdfinfo_extracts_page_count_and_letter_size():
    parsed = parse_pdfinfo("Pages: 12\nPage size: 612 x 792 pts (letter)\n")

    assert parsed["pages"] == 12
    assert parsed["page_size"] == "612 x 792 pts (letter)"
    assert parsed["is_letter"] is True


def test_audit_manuscript_package_passes_structure_and_records_pending_items(tmp_path):
    manuscript, archive = _write_minimal_manuscript(tmp_path)

    audit = audit_manuscript_package(
        manuscript_dir=manuscript,
        zip_path=archive,
        pdfinfo_text="Pages: 12\nPage size: 612 x 792 pts (letter)\n",
        log_text="This is a clean LaTeX log.\n",
    )

    assert audit["ok"] is True
    assert audit["summary"]["page_count"] == 12
    assert audit["summary"]["zip_entry_count"] == 7
    assert any(item["name"] == "documentclass_acm_review" and item["status"] == "pass" for item in audit["checks"])
    assert any(item["name"] == "figure_descriptions" and item["status"] == "pass" for item in audit["checks"])
    assert "confirm_author_affiliation_email" in audit["pending_human_items"]
    assert "confirm_acm_ccs" in audit["pending_human_items"]


def test_audit_manuscript_package_fails_when_zip_contains_preview_pdf(tmp_path):
    manuscript, archive = _write_minimal_manuscript(tmp_path)
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("main.pdf", b"%PDF-1.4\n")

    audit = audit_manuscript_package(
        manuscript_dir=manuscript,
        zip_path=archive,
        pdfinfo_text="Pages: 12\nPage size: 612 x 792 pts (letter)\n",
        log_text="This is a clean LaTeX log.\n",
    )

    assert audit["ok"] is False
    assert any(item["name"] == "zip_forbidden_entries" and item["status"] == "fail" for item in audit["checks"])


def test_audit_manuscript_package_reports_missing_main_tex(tmp_path):
    manuscript = tmp_path / "Template" / "PU-XMSAT-Overleaf"
    manuscript.mkdir(parents=True)
    archive = tmp_path / "Template" / "PU-XMSAT-Overleaf.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("README.md", "README\n")

    audit = audit_manuscript_package(
        manuscript_dir=manuscript,
        zip_path=archive,
        pdfinfo_text="",
        log_text="",
    )

    assert audit["ok"] is False
    assert any(item["name"] == "main_tex_exists" and item["status"] == "fail" for item in audit["checks"])


def test_audit_manuscript_package_resolves_graphicspath_figures(tmp_path):
    manuscript, archive = _write_minimal_manuscript(tmp_path)
    main_tex = (manuscript / "main.tex").read_text()
    main_tex = main_tex.replace(
        r"\begin{document}",
        "\n".join([r"\graphicspath{{figures/}}", r"\begin{document}"]),
    )
    main_tex = main_tex.replace("figures/method_overview.pdf", "method_overview.pdf")
    main_tex = main_tex.replace("figures/metric_delta.pdf", "metric_delta.pdf")
    (manuscript / "main.tex").write_text(main_tex)

    audit = audit_manuscript_package(
        manuscript_dir=manuscript,
        zip_path=archive,
        pdfinfo_text="Pages: 12\nPage size: 612 x 792 pts (letter)\n",
        log_text="This is a clean LaTeX log.\n",
    )

    assert audit["ok"] is True
    assert any(item["name"] == "figure_files" and item["status"] == "pass" for item in audit["checks"])
    assert any(item["name"] == "zip_required_entries" and item["status"] == "pass" for item in audit["checks"])


def test_write_audit_outputs_preserves_submission_boundaries(tmp_path):
    manuscript, archive = _write_minimal_manuscript(tmp_path)
    audit = audit_manuscript_package(
        manuscript_dir=manuscript,
        zip_path=archive,
        pdfinfo_text="Pages: 12\nPage size: 612 x 792 pts (letter)\n",
        log_text="This is a clean LaTeX log.\n",
    )

    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    write_audit_outputs(audit, output_json, output_md)

    rendered = output_md.read_text()
    assert "## Claim Boundaries To Preserve" in rendered
    assert "full Table 5/6 reproduction" in rendered
    assert "## Packaging Rule" in rendered
    assert "LaTeX auxiliary files" in rendered
