from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def build_case_row(
    herb_id: int,
    adr_id: int,
    score: float,
    paths: list[dict],
    contributions: list[dict],
) -> dict:
    return {
        "herb_id": int(herb_id),
        "adr_id": int(adr_id),
        "prediction_score": float(score),
        "paths": paths,
        "path_count": len(paths),
        "contributions": contributions,
        "contribution_count": len(contributions),
    }


def _rows_from_table5(path: Path, limit: int) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            path_hint = row.get("path_hint", "")
            paths = [{"path": path_hint}] if path_hint else []
            contributions = []
            if row.get("mechanistic_support") == "True":
                contributions.append(
                    {"feature": "mechanistic_support", "score_drop": None}
                )
            rows.append(
                build_case_row(
                    herb_id=int(row["herb_id"]),
                    adr_id=int(row["adr_id"]),
                    score=float(row["score_pct"]) / 100.0,
                    paths=paths,
                    contributions=contributions,
                )
                | {
                    "rank": int(row["rank"]),
                    "source": "table5_top15",
                    "database_verified": row.get("database_verified") == "True",
                }
            )
            if len(rows) >= limit:
                break
    return rows


def _row_from_zhishi_case(path: Path) -> dict | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    paths = [{"path": item} for item in data.get("paths", [])]
    contributions = [
        {"feature": "nobiletin_cid", "value": data.get("paper_targets", {}).get("nobiletin_cid")},
        {"feature": "transporter", "value": data.get("paper_targets", {}).get("transporter")},
    ]
    return build_case_row(
        herb_id=int(data["herb_id"]),
        adr_id=int(data["adr_id"]),
        score=float(data["score"]),
        paths=paths,
        contributions=[row for row in contributions if row.get("value") is not None],
    ) | {
        "rank": data.get("rank"),
        "rank_total": data.get("rank_total"),
        "source": "case_zhishi_diarrhoea",
    }


def build_case_rows(
    table5_path: str | Path = "results/table5_top15.csv",
    zhishi_case_path: str | Path = "results/case_zhishi_diarrhoea.json",
    min_rows: int = 5,
) -> list[dict]:
    rows: list[dict] = []
    zhishi = _row_from_zhishi_case(Path(zhishi_case_path))
    if zhishi is not None:
        rows.append(zhishi)
    rows.extend(_rows_from_table5(Path(table5_path), limit=max(min_rows, 0)))
    return rows[: max(len(rows), min_rows)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/explanation_case_studies.json")
    parser.add_argument("--table5", default="results/table5_top15.csv")
    parser.add_argument("--zhishi-case", default="results/case_zhishi_diarrhoea.json")
    parser.add_argument("--min-rows", type=int, default=5)
    args = parser.parse_args()

    rows = build_case_rows(
        table5_path=args.table5,
        zhishi_case_path=args.zhishi_case,
        min_rows=args.min_rows,
    )
    payload = {"experiment": "explanation_case_study", "rows": rows}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
