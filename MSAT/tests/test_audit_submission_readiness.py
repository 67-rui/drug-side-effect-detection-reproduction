import json
from pathlib import Path

from scripts.audit_submission_readiness import (
    audit_submission_readiness,
    write_readiness_outputs,
)


def _write_minimal_manuscript(root: Path) -> Path:
    manuscript = root / "Template" / "PU-XMSAT-Overleaf"
    manuscript.mkdir(parents=True)
    (manuscript / "main.tex").write_text(
        "\n".join(
            [
                r"\documentclass[manuscript,screen,review]{acmart}",
                r"% TODO before formal submission: replace metadata and CCS placeholders.",
                r"\acmConference[Conference Placeholder '26]{Proceedings Placeholder}{Month DD--DD, 2026}{City, Country}",
                r"\acmBooktitle{Proceedings Placeholder}",
                r"\acmDOI{10.1145/0000000.0000000}",
                r"\acmISBN{978-1-4503-0000-0/26/06}",
                r"\author{First Author}",
                r"\affiliation{\institution{Institution Placeholder}}",
                r"\email{first.author@example.com}",
                r"\ccsdesc[500]{Computing methodologies~Machine learning}",
                r"\keywords{positive-unlabeled learning, pharmacovigilance}",
                r"\begin{document}",
                r"\maketitle",
                r"\section*{Declaration on Generative AI Assistance}",
                r"This statement should be revised to match the final venue policy before submission.",
                r"\begin{acks}",
                r"TODO: Add funding, institutional support, and supervisor acknowledgements if appropriate.",
                r"\end{acks}",
                r"\end{document}",
            ]
        )
    )
    return manuscript


def test_audit_submission_readiness_keeps_human_blockers_separate_from_package_ok(tmp_path):
    manuscript = _write_minimal_manuscript(tmp_path)
    package_audit = {
        "ok": True,
        "summary": {
            "failed_check_count": 0,
            "warning_check_count": 1,
            "page_count": 12,
            "page_size": "612 x 792 pts (letter)",
        },
    }

    audit = audit_submission_readiness(manuscript, package_audit)

    assert audit["ready_for_submission"] is False
    assert audit["summary"]["package_ok"] is True
    assert audit["summary"]["machine_fail_count"] == 0
    assert audit["summary"]["human_blocker_count"] >= 6
    blocker_ids = {item["id"] for item in audit["human_blockers"]}
    assert "author_metadata" in blocker_ids
    assert "venue_metadata" in blocker_ids
    assert "ccs_confirmation" in blocker_ids
    assert "funding_acknowledgments" in blocker_ids
    assert "ai_disclosure_policy" in blocker_ids
    assert "double_blind_policy" in blocker_ids


def test_write_readiness_outputs_preserves_submission_handoff_language(tmp_path):
    manuscript = _write_minimal_manuscript(tmp_path)
    audit = audit_submission_readiness(manuscript, {"ok": True, "summary": {}})
    output_json = tmp_path / "readiness.json"
    output_md = tmp_path / "readiness.md"

    write_readiness_outputs(audit, output_json, output_md)

    assert json.loads(output_json.read_text())["ready_for_submission"] is False
    rendered = output_md.read_text()
    assert "Submission Readiness Audit" in rendered
    assert "Ready for submission: no" in rendered
    assert "`author_metadata`" in rendered
    assert "student/supervisor" in rendered
