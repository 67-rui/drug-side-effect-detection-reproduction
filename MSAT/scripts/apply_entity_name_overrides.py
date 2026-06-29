#!/usr/bin/env python3
"""Merge curated compound/target names into entity_names.json."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _validate_record(section: str, node_id: str, record: dict[str, Any]) -> dict[str, Any]:
    if not str(node_id).isdigit():
        raise ValueError(f"{section} override id must be numeric: {node_id!r}")
    primary = str(record.get("primary", "")).strip()
    if not primary:
        raise ValueError(f"{section}:{node_id} override requires a non-empty primary name")
    merged = dict(record)
    merged["primary"] = primary
    merged.setdefault("source", "curated_override")
    return merged


def apply_overrides(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of base mapping with compound/target override records merged."""
    merged = copy.deepcopy(base)
    merged.setdefault("meta", {})
    merged.setdefault("herbs", {})
    merged.setdefault("adrs", {})
    merged.setdefault("compounds", {})
    merged.setdefault("targets", {})

    for section in ("compounds", "targets"):
        records = overrides.get(section, {}) or {}
        if not isinstance(records, dict):
            raise ValueError(f"{section} overrides must be an object keyed by node id")
        for node_id, record in records.items():
            if not isinstance(record, dict):
                raise ValueError(f"{section}:{node_id} override must be an object")
            merged[section][str(int(node_id))] = _validate_record(section, str(node_id), record)

    override_meta = dict(overrides.get("meta", {}) or {})
    override_meta.update(
        {
            "applied_at": datetime.now().isoformat(),
            "compound_count": len(overrides.get("compounds", {}) or {}),
            "target_count": len(overrides.get("targets", {}) or {}),
        }
    )
    merged["meta"]["compound_target_overrides"] = override_meta
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply compound/target name overrides")
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--overrides", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
    merged = apply_overrides(base, overrides)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        "[saved]",
        args.output,
        "compounds=",
        len(merged.get("compounds", {})),
        "targets=",
        len(merged.get("targets", {})),
    )


if __name__ == "__main__":
    main()
