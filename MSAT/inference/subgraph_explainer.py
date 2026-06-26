from __future__ import annotations


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


def extract_path_templates(data, herb_id: int, adr_id: int, max_paths: int = 20) -> list[dict]:
    paths: list[dict] = []
    compounds = _neighbors(data, ("herb", "contains", "compound"), herb_id)
    adr_targets = _neighbors(data, ("adr", "causes", "target"), adr_id)

    for compound_id in sorted(compounds):
        compound_targets = _reverse_neighbors(
            data, ("target", "binds", "compound"), compound_id
        )
        for target_id in sorted(compound_targets & adr_targets):
            paths.append(
                {
                    "template": "herb-compound-target-adr",
                    "herb_id": int(herb_id),
                    "compound_id": int(compound_id),
                    "target_id": int(target_id),
                    "adr_id": int(adr_id),
                }
            )
            if len(paths) >= max_paths:
                return paths

    direct_targets = _neighbors(data, ("herb", "targets", "target"), herb_id)
    for target_id in sorted(direct_targets & adr_targets):
        paths.append(
            {
                "template": "herb-target-adr",
                "herb_id": int(herb_id),
                "target_id": int(target_id),
                "adr_id": int(adr_id),
            }
        )
        if len(paths) >= max_paths:
            return paths
    return paths
