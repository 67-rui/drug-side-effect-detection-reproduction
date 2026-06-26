from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def assign_evidence_grade(
    database_verified: bool,
    direct_literature_support: bool,
    mechanistic_support: bool,
) -> str:
    if database_verified:
        return "A"
    if direct_literature_support:
        return "B"
    if mechanistic_support:
        return "C"
    return "D"


def build_evidence_rows(table5: dict) -> list[dict]:
    rows = []
    for row in table5.get("rows", []):
        grade = assign_evidence_grade(
            database_verified=bool(row.get("database_verified")),
            direct_literature_support=bool(row.get("direct_literature_support")),
            mechanistic_support=bool(row.get("mechanistic_support")),
        )
        rows.append({**row, "evidence_grade": grade})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table5", default="results/table5_summary.json")
    parser.add_argument("--output-json", default="results/evidence_screening_summary.json")
    parser.add_argument("--output-csv", default="results/evidence_screening_table.csv")
    args = parser.parse_args()

    table5 = json.loads(Path(args.table5).read_text())
    rows = build_evidence_rows(table5)

    out_json = Path(args.output_json)
    out_csv = Path(args.output_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(
            {"experiment": "evidence_screening", "rows": rows},
            ensure_ascii=False,
            indent=2,
        )
    )
    if rows:
        with out_csv.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {out_json} and {out_csv}")


if __name__ == "__main__":
    main()
