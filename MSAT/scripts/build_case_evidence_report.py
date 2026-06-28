from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from scripts.build_evidence_screening_table import assign_evidence_grade


NO_EXPLICIT_PATH_MARKERS = (
    "未发现",
    "嵌入推断",
    "no explicit",
    "embedding",
)

CSV_FIELDS = [
    "rank",
    "source",
    "candidate_scope",
    "herb_id",
    "herb_latin",
    "herb_chinese",
    "herb_pinyin",
    "adr_id",
    "adr_pt",
    "prediction_score",
    "database_verified",
    "direct_literature_support",
    "mechanistic_support",
    "evidence_grade",
    "literature_record_count",
    "literature_support_candidate_count",
    "verified_literature_count",
    "manual_review_required",
    "mechanism_path_count",
    "top_mechanism_paths",
    "contribution_count",
    "top_contributions",
    "evidence_interpretation",
]


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _int_or_none(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(float(str(value)))


def _float_or_none(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(str(value))


def _clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("?", " ").strip()


def _key(row: dict) -> tuple[int, int]:
    return int(row["herb_id"]), int(row["adr_id"])


def _read_csv_rows(path: str | Path) -> list[dict]:
    src = Path(path)
    if not src.exists():
        return []
    with src.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _load_explanation_rows(path: str | Path) -> dict[tuple[int, int], dict]:
    src = Path(path)
    if not src.exists():
        return {}
    payload = json.loads(src.read_text())
    out: dict[tuple[int, int], dict] = {}
    for row in payload.get("rows", []):
        if "herb_id" not in row or "adr_id" not in row:
            continue
        out[(int(row["herb_id"]), int(row["adr_id"]))] = row
    return out


def _load_literature_stats(path: str | Path) -> dict[tuple[int, int], dict]:
    stats: dict[tuple[int, int], dict] = defaultdict(
        lambda: {
            "record_count": 0,
            "support_candidate_count": 0,
            "verified_support_count": 0,
            "top_titles": [],
        }
    )
    for row in _read_csv_rows(path):
        if not row.get("herb_id") or not row.get("adr_id"):
            continue
        key = (int(row["herb_id"]), int(row["adr_id"]))
        item = stats[key]
        item["record_count"] += 1
        if _truthy(row.get("support_candidate")):
            item["support_candidate_count"] += 1
        if _truthy(row.get("verified_support")):
            item["verified_support_count"] += 1
        title = _clean(row.get("title"))
        if title and len(item["top_titles"]) < 3:
            item["top_titles"].append(title)
    return dict(stats)


def _extract_path_texts(row: dict | None, fallback_path: str = "") -> list[str]:
    if not row:
        return [fallback_path] if fallback_path else []
    paths: list[str] = []
    for path in row.get("paths", []):
        if isinstance(path, dict):
            text = _clean(path.get("path") or path.get("template"))
        else:
            text = _clean(path)
        if text:
            paths.append(text)
    if not paths and fallback_path:
        paths.append(fallback_path)
    return paths


def _is_explicit_mechanism_path(path_text: str) -> bool:
    lowered = path_text.lower()
    return bool(path_text) and not any(
        marker.lower() in lowered for marker in NO_EXPLICIT_PATH_MARKERS
    )


def _format_number(value: object) -> str:
    number = _float_or_none(value)
    if number is None:
        return ""
    return f"{number:.6g}"


def _format_contributions(contributions: Iterable[dict], max_items: int = 3) -> str:
    formatted: list[str] = []
    for row in contributions:
        feature = _clean(row.get("feature"))
        if not feature:
            continue
        if row.get("score_drop") not in (None, ""):
            formatted.append(f"{feature}:{_format_number(row.get('score_drop'))}")
        elif row.get("value") not in (None, ""):
            formatted.append(f"{feature}={_clean(row.get('value'))}")
        else:
            formatted.append(feature)
        if len(formatted) >= max_items:
            break
    return " | ".join(formatted)


def _join_top(items: Iterable[str], max_items: int = 3) -> str:
    return " | ".join([item for item in items if item][:max_items])


def _grade_interpretation(grade: str) -> str:
    return {
        "A": "database or label-source support; usable as strong external evidence",
        "B": "manually verified direct literature support; usable as strong external evidence",
        "C": "mechanistic graph support only; useful for explanation, needs external review",
        "D": "prediction-only candidate; retain for manual screening, not evidence-backed",
    }[grade]


def _row_from_table5(
    table_row: dict,
    explanation_row: dict | None,
    literature_stats: dict,
) -> dict:
    score = _float_or_none(table_row.get("score_pct"))
    if score is not None:
        score /= 100.0
    elif explanation_row:
        score = _float_or_none(explanation_row.get("prediction_score"))

    path_texts = _extract_path_texts(
        explanation_row,
        fallback_path=_clean(table_row.get("path_hint")),
    )
    explicit_paths = [path for path in path_texts if _is_explicit_mechanism_path(path)]
    contributions = list((explanation_row or {}).get("contributions", []))
    mechanistic_support = (
        _truthy(table_row.get("mechanistic_support"))
        or bool(explicit_paths)
        or bool(contributions)
    )
    database_verified = _truthy(table_row.get("database_verified"))
    direct_literature_support = literature_stats.get("verified_support_count", 0) > 0
    grade = assign_evidence_grade(
        database_verified=database_verified,
        direct_literature_support=direct_literature_support,
        mechanistic_support=mechanistic_support,
    )

    return {
        "rank": _int_or_none(table_row.get("rank")),
        "source": "table5_top15",
        "candidate_scope": "legacy_msat_top15_case_candidate",
        "herb_id": int(table_row["herb_id"]),
        "herb_latin": _clean(table_row.get("latin") or table_row.get("herb_latin")),
        "herb_chinese": _clean(table_row.get("chinese") or table_row.get("herb_chinese")),
        "herb_pinyin": _clean(table_row.get("pinyin") or table_row.get("herb_pinyin")),
        "adr_id": int(table_row["adr_id"]),
        "adr_pt": _clean(table_row.get("adr_pt")),
        "prediction_score": score,
        "database_verified": database_verified,
        "direct_literature_support": direct_literature_support,
        "mechanistic_support": mechanistic_support,
        "evidence_grade": grade,
        "literature_record_count": literature_stats.get("record_count", 0),
        "literature_support_candidate_count": literature_stats.get(
            "support_candidate_count", 0
        ),
        "verified_literature_count": literature_stats.get("verified_support_count", 0),
        "manual_review_required": not direct_literature_support
        or literature_stats.get("support_candidate_count", 0)
        > literature_stats.get("verified_support_count", 0),
        "mechanism_path_count": len(explicit_paths),
        "top_mechanism_paths": _join_top(explicit_paths),
        "contribution_count": len(contributions),
        "top_contributions": _format_contributions(contributions),
        "evidence_interpretation": _grade_interpretation(grade),
    }


def _row_from_extra_explanation(explanation_row: dict, literature_stats: dict) -> dict:
    path_texts = _extract_path_texts(explanation_row)
    explicit_paths = [path for path in path_texts if _is_explicit_mechanism_path(path)]
    contributions = list(explanation_row.get("contributions", []))
    mechanistic_support = bool(explicit_paths or contributions)
    direct_literature_support = literature_stats.get("verified_support_count", 0) > 0
    grade = assign_evidence_grade(
        database_verified=False,
        direct_literature_support=direct_literature_support,
        mechanistic_support=mechanistic_support,
    )
    return {
        "rank": explanation_row.get("rank"),
        "source": _clean(explanation_row.get("source")) or "explanation_case_study",
        "candidate_scope": "curated_explanation_case_not_table5_reproduction",
        "herb_id": int(explanation_row["herb_id"]),
        "herb_latin": "",
        "herb_chinese": "",
        "herb_pinyin": "",
        "adr_id": int(explanation_row["adr_id"]),
        "adr_pt": "",
        "prediction_score": _float_or_none(explanation_row.get("prediction_score")),
        "database_verified": False,
        "direct_literature_support": direct_literature_support,
        "mechanistic_support": mechanistic_support,
        "evidence_grade": grade,
        "literature_record_count": literature_stats.get("record_count", 0),
        "literature_support_candidate_count": literature_stats.get(
            "support_candidate_count", 0
        ),
        "verified_literature_count": literature_stats.get("verified_support_count", 0),
        "manual_review_required": True,
        "mechanism_path_count": len(explicit_paths),
        "top_mechanism_paths": _join_top(explicit_paths),
        "contribution_count": len(contributions),
        "top_contributions": _format_contributions(contributions),
        "evidence_interpretation": _grade_interpretation(grade),
    }


def build_case_evidence_rows(
    table5_path: str | Path = "results/table5_top15.csv",
    explanation_path: str | Path = "results/explanation_case_studies.json",
    literature_path: str | Path = "results/table5_literature_evidence_candidates.csv",
    limit: int = 15,
    include_extra_explanation_cases: bool = True,
) -> list[dict]:
    table_rows = _read_csv_rows(table5_path)[: max(limit, 0)]
    explanations = _load_explanation_rows(explanation_path)
    literature = _load_literature_stats(literature_path)

    rows: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for table_row in table_rows:
        key = _key(table_row)
        rows.append(
            _row_from_table5(table_row, explanations.get(key), literature.get(key, {}))
        )
        seen.add(key)

    if include_extra_explanation_cases:
        for key, explanation_row in sorted(explanations.items()):
            if key in seen:
                continue
            extra = _row_from_extra_explanation(explanation_row, literature.get(key, {}))
            if extra["mechanistic_support"]:
                rows.append(extra)
    return rows


def summarize_case_evidence(rows: list[dict]) -> dict:
    grade_counts = dict(Counter(row["evidence_grade"] for row in rows))
    return {
        "row_count": len(rows),
        "grade_counts": grade_counts,
        "mechanistic_support_count": sum(
            1 for row in rows if row.get("mechanistic_support")
        ),
        "direct_literature_support_count": sum(
            1 for row in rows if row.get("direct_literature_support")
        ),
        "literature_record_row_count": sum(
            1 for row in rows if row.get("literature_record_count", 0) > 0
        ),
        "literature_review_candidate_count": sum(
            1 for row in rows if row.get("literature_support_candidate_count", 0) > 0
        ),
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in CSV_FIELDS} for row in rows])


def _write_markdown(path: Path, rows: list[dict], summary: dict) -> None:
    lines = [
        "# PU-XMSAT Case Evidence Report",
        "",
        "This report closes the minimal paper-facing loop for mechanism explanation "
        "and external evidence screening. The current candidate rows are derived "
        "from the existing MSAT/Table 5-style candidate artifacts and curated "
        "case-study outputs; they should not be described as a fully regenerated "
        "PU-XMSAT top-ranking table unless a future PU-XMSAT prediction export is added.",
        "",
        "## Summary",
        "",
        f"- Candidate rows: {summary['row_count']}",
        f"- Grade counts: {summary['grade_counts']}",
        f"- Rows with explicit mechanism support: {summary['mechanistic_support_count']}",
        f"- Rows with manually verified direct literature support: {summary['direct_literature_support_count']}",
        f"- Rows with automated literature records: {summary['literature_record_row_count']}",
        f"- Rows with automated literature review candidates: {summary['literature_review_candidate_count']}",
        "",
        "Automated literature hits are treated as review candidates only. They do "
        "not upgrade a row to Grade B unless `verified_support=True` is present.",
        "",
        "## Case Table",
        "",
        "| Rank | Source | Herb | ADR | Score | Grade | Mechanism | Literature Review Candidates |",
        "| ---: | --- | --- | --- | ---: | :---: | --- | ---: |",
    ]
    for row in rows:
        score = row.get("prediction_score")
        score_text = "" if score is None else f"{float(score):.4f}"
        herb = row.get("herb_chinese") or row.get("herb_latin") or row.get("herb_id")
        mechanism = row.get("top_mechanism_paths") or "No explicit short path"
        lines.append(
            "| {rank} | {source} | {herb} | {adr} | {score} | {grade} | {mechanism} | {lit} |".format(
                rank=row.get("rank") or "",
                source=row.get("source") or "",
                herb=str(herb).replace("|", "/"),
                adr=str(row.get("adr_pt") or row.get("adr_id")).replace("|", "/"),
                score=score_text,
                grade=row.get("evidence_grade"),
                mechanism=str(mechanism).replace("|", "/"),
                lit=row.get("literature_support_candidate_count", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Paper Claim Boundary",
            "",
            "- Use this table as an explanation and evidence-screening workflow artifact.",
            "- Do not claim that Table 5/6 has been equivalently reproduced from public materials.",
            "- Do not treat unverified automated literature candidates as confirmed support.",
            "- Grade C rows support mechanism discussion, not direct adverse-reaction validation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def write_case_evidence_artifacts(
    rows: list[dict],
    output_json: str | Path,
    output_csv: str | Path,
    output_md: str | Path,
) -> dict:
    summary = summarize_case_evidence(rows)
    payload = {
        "experiment": "case_evidence_report",
        "scope": "mechanism_explanation_and_external_evidence_screening",
        "claim_boundary": (
            "Automated literature candidates require manual verification; this "
            "artifact does not prove Table 5/6 equivalent reproduction."
        ),
        "summary": summary,
        "rows": rows,
    }

    out_json = Path(output_json)
    out_csv = Path(output_csv)
    out_md = Path(output_md)
    for path in (out_json, out_csv, out_md):
        path.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    _write_csv(out_csv, rows)
    _write_markdown(out_md, rows, summary)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table5", default="results/table5_top15.csv")
    parser.add_argument("--explanations", default="results/explanation_case_studies.json")
    parser.add_argument(
        "--literature-candidates",
        default="results/table5_literature_evidence_candidates.csv",
    )
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--output-json", default="results/case_evidence_report.json")
    parser.add_argument("--output-csv", default="results/case_evidence_report.csv")
    parser.add_argument(
        "--output-md",
        default="results/PU_XMSAT_CASE_EVIDENCE_REPORT.md",
    )
    parser.add_argument(
        "--no-extra-explanation-cases",
        action="store_true",
        help="Only include rows from the Table 5-style candidate CSV.",
    )
    args = parser.parse_args()

    rows = build_case_evidence_rows(
        table5_path=args.table5,
        explanation_path=args.explanations,
        literature_path=args.literature_candidates,
        limit=args.limit,
        include_extra_explanation_cases=not args.no_extra_explanation_cases,
    )
    payload = write_case_evidence_artifacts(
        rows,
        output_json=args.output_json,
        output_csv=args.output_csv,
        output_md=args.output_md,
    )
    print(
        "Wrote case evidence report with "
        f"{payload['summary']['row_count']} rows to {args.output_json}, "
        f"{args.output_csv}, and {args.output_md}"
    )


if __name__ == "__main__":
    main()
