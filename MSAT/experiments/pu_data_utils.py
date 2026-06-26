from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


Pair = tuple[int, int]


def build_positive_pair_set(data) -> set[Pair]:
    edge_index = data["herb", "causes", "adr"].edge_index
    return {
        (int(edge_index[0, i]), int(edge_index[1, i]))
        for i in range(edge_index.size(1))
    }


def build_unobserved_pairs(
    num_herbs: int,
    num_adrs: int,
    positive_pairs: set[Pair],
) -> list[Pair]:
    return [
        (herb_id, adr_id)
        for herb_id in range(num_herbs)
        for adr_id in range(num_adrs)
        if (herb_id, adr_id) not in positive_pairs
    ]


def _neighbors(data, edge_type: tuple[str, str, str], source_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[0] == int(source_id)
    return {int(v) for v in edge_index[1, mask].tolist()}


def _reverse_neighbors(data, edge_type: tuple[str, str, str], target_id: int) -> set[int]:
    if edge_type not in data.edge_types:
        return set()
    edge_index = data[edge_type].edge_index
    mask = edge_index[1] == int(target_id)
    return {int(v) for v in edge_index[0, mask].tolist()}


def herb_target_set(data, herb_id: int) -> set[int]:
    direct = _neighbors(data, ("herb", "targets", "target"), herb_id)
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)
    via_compound: set[int] = set()
    for compound_id in compounds:
        via_compound.update(
            _reverse_neighbors(data, ("target", "binds", "compound"), compound_id)
        )
    return direct | via_compound


def adr_target_set(data, adr_id: int) -> set[int]:
    return _neighbors(data, ("adr", "causes", "target"), adr_id)


def count_mechanistic_support(data, herb_id: int, adr_id: int) -> dict:
    direct_targets = _neighbors(data, ("herb", "targets", "target"), herb_id)
    adr_targets = adr_target_set(data, adr_id)
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)

    compound_targets: set[int] = set()
    for compound_id in compounds:
        compound_targets.update(
            _reverse_neighbors(data, ("target", "binds", "compound"), compound_id)
        )

    direct_overlap = direct_targets & adr_targets
    compound_overlap = compound_targets & adr_targets
    total = len(direct_overlap) + len(compound_overlap)
    return {
        "direct_target_overlap": len(direct_overlap),
        "compound_target_overlap": len(compound_overlap),
        "total": total,
    }


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open() as fh:
        return [json.loads(line) for line in fh if line.strip()]
