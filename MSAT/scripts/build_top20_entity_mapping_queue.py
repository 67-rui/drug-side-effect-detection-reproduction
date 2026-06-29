#!/usr/bin/env python3
"""Build a focused compound/target mapping queue for top-20 mechanism cases."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


FIELDS = [
    "feature",
    "node_type",
    "node_id",
    "current_display_name",
    "name_source",
    "mapping_status",
    "case_count",
    "occurrence_count",
    "max_score_drop",
    "mean_score_drop",
    "case_links",
    "top_path_text",
]


def _feature_parts(feature: str) -> tuple[str, int] | None:
    if ":" not in str(feature):
        return None
    node_type, raw_id = str(feature).split(":", 1)
    if node_type not in {"compound", "target"} or not raw_id.isdigit():
        return None
    return node_type, int(raw_id)


def _records(names_payload: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    value = names_payload.get(section, {}) or {}
    return value if isinstance(value, dict) else {}


def _display_for(
    feature: str,
    node_type: str,
    node_id: int,
    names_payload: dict[str, Any],
) -> tuple[str, str, str]:
    section = "compounds" if node_type == "compound" else "targets"
    record = _records(names_payload, section).get(str(node_id), {})
    primary = str(record.get("primary", "")).strip()
    if primary:
        return primary, str(record.get("source") or "entity_names"), "mapped"
    fallback = "Compound" if node_type == "compound" else "Target"
    return f"{fallback} #{node_id}", "unmapped_graph_id", "needs_mapping"


def _path_rows(case: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in case.get("path_contributions", []) or case.get("pathway_contributions", []) or []:
        rows.append(row)
    return rows


def _node_rows(case: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in case.get("node_contributions", []) or []:
        rows.append(row)
    for group in ("component_contributions", "target_contributions"):
        for row in case.get(group, []) or []:
            rows.append(row)
    return rows


def build_mapping_queue(
    batch_payload: dict[str, Any],
    names_payload: dict[str, Any],
) -> dict[str, Any]:
    buckets: dict[str, dict[str, Any]] = {}
    case_sets: dict[str, set[tuple[int, int]]] = defaultdict(set)
    score_drops: dict[str, list[float]] = defaultdict(list)
    path_texts: dict[str, list[str]] = defaultdict(list)

    for case in batch_payload.get("cases", []):
        herb_id = int(case.get("herb_id"))
        adr_id = int(case.get("adr_id"))
        case_link = (herb_id, adr_id)
        for row in _node_rows(case):
            feature = str(row.get("feature", ""))
            parsed = _feature_parts(feature)
            if not parsed:
                continue
            node_type, node_id = parsed
            buckets.setdefault(
                feature,
                {"feature": feature, "node_type": node_type, "node_id": node_id},
            )
            case_sets[feature].add(case_link)
            score_drops[feature].append(float(row.get("score_drop", 0.0) or 0.0))
        for row in _path_rows(case):
            for feature in row.get("features", []) or []:
                parsed = _feature_parts(str(feature))
                if not parsed:
                    continue
                node_type, node_id = parsed
                buckets.setdefault(
                    str(feature),
                    {"feature": str(feature), "node_type": node_type, "node_id": node_id},
                )
                case_sets[str(feature)].add(case_link)
                score_drops[str(feature)].append(float(row.get("score_drop", 0.0) or 0.0))
                text = str(row.get("path_text", "")).strip()
                if text:
                    path_texts[str(feature)].append(text)

    rows = []
    for feature, bucket in buckets.items():
        node_type = bucket["node_type"]
        node_id = int(bucket["node_id"])
        display, source, status = _display_for(feature, node_type, node_id, names_payload)
        drops = score_drops.get(feature, [0.0])
        links = sorted(case_sets.get(feature, set()))
        rows.append(
            {
                **bucket,
                "current_display_name": display,
                "name_source": source,
                "mapping_status": status,
                "case_count": len(links),
                "occurrence_count": len(drops),
                "max_score_drop": round(max(drops), 10),
                "mean_score_drop": round(sum(drops) / len(drops), 10),
                "case_links": "; ".join(f"herb {h} -> ADR {a}" for h, a in links),
                "top_path_text": path_texts.get(feature, [""])[0],
            }
        )

    rows.sort(
        key=lambda row: (
            row["mapping_status"] != "needs_mapping",
            -float(row["max_score_drop"]),
            row["node_type"],
            int(row["node_id"]),
        )
    )
    return {
        "experiment": "top20_entity_mapping_queue",
        "created_at": datetime.now().isoformat(),
        "summary": {
            "compound_count": sum(1 for row in rows if row["node_type"] == "compound"),
            "target_count": sum(1 for row in rows if row["node_type"] == "target"),
            "mapped_count": sum(1 for row in rows if row["mapping_status"] == "mapped"),
            "unmapped_count": sum(1 for row in rows if row["mapping_status"] == "needs_mapping"),
        },
        "claim_boundary": (
            "This queue identifies graph nodes that need human-readable names. "
            "Mapped names must preserve their source and should not be treated as biological validation."
        ),
        "rows": rows,
    }


def write_outputs(queue: dict[str, Any], output_json: Path, output_csv: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in queue["rows"]:
            writer.writerow({field: row.get(field, "") for field in FIELDS})
    lines = [
        "# Top-20 Entity Mapping Queue",
        "",
        f"- Compounds: {queue['summary']['compound_count']}",
        f"- Targets: {queue['summary']['target_count']}",
        f"- Mapped: {queue['summary']['mapped_count']}",
        f"- Needs mapping: {queue['summary']['unmapped_count']}",
        "",
        "Mapped names are readability aids and do not upgrade evidence grade.",
        "",
        "| Feature | Current name | Source | Cases | Max drop | Top path |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in queue["rows"][:40]:
        lines.append(
            "| `{feature}` | {name} | {source} | {cases} | {drop:.6f} | {path} |".format(
                feature=row["feature"],
                name=str(row["current_display_name"]).replace("|", "/"),
                source=row["name_source"],
                cases=row["case_count"],
                drop=float(row["max_score_drop"]),
                path=str(row["top_path_text"]).replace("|", "/"),
            )
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build top-20 compound/target mapping queue")
    parser.add_argument(
        "--batch",
        type=Path,
        default=Path("results/batch_mechanism_interpretability_top5000_random_controls.json"),
    )
    parser.add_argument("--entity-names", type=Path, default=Path("data/entity_names.json"))
    parser.add_argument("--output-json", type=Path, default=Path("results/top20_entity_mapping_queue.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("results/top20_entity_mapping_queue.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("results/PU_XMSAT_TOP20_ENTITY_MAPPING_QUEUE.md"))
    args = parser.parse_args()

    batch_payload = json.loads(args.batch.read_text(encoding="utf-8"))
    names_payload = json.loads(args.entity_names.read_text(encoding="utf-8"))
    queue = build_mapping_queue(batch_payload, names_payload)
    write_outputs(queue, args.output_json, args.output_csv, args.output_md)
    print(
        "[saved]",
        args.output_json,
        "needs_mapping=",
        queue["summary"]["unmapped_count"],
    )


if __name__ == "__main__":
    main()
