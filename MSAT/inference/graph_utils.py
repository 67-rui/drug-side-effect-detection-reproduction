"""Graph helpers for MSAT inference (known edges, simple explanation paths)."""

from __future__ import annotations

import torch
from torch_geometric.data import HeteroData


def build_known_herb_adr_map(data: HeteroData) -> dict[int, set[int]]:
    """Map herb_id -> set of adr_id with supervised CMM–ADR edges in the graph."""
    ei = data['herb', 'causes', 'adr'].edge_index
    out: dict[int, set[int]] = {}
    for h, a in zip(ei[0].tolist(), ei[1].tolist()):
        out.setdefault(int(h), set()).add(int(a))
    return out


def herb_known_adr_counts(data: HeteroData) -> list[int]:
    n = data['herb'].x.size(0)
    counts = [0] * n
    ei = data['herb', 'causes', 'adr'].edge_index
    for h in ei[0].tolist():
        counts[int(h)] += 1
    return counts


def explain_herb_adr(
    data: HeteroData,
    herb_id: int,
    adr_id: int,
    limit: int = 8,
    herb_label: str | None = None,
    adr_label: str | None = None,
) -> list[str]:
    """Return short natural-language path hints from the knowledge graph."""
    h = herb_label or f'CMM #{herb_id}'
    a = adr_label or f'ADR #{adr_id}'
    paths: list[str] = []

    hc = data['herb', 'contains', 'compound'].edge_index
    ht = data['herb', 'targets', 'target'].edge_index
    at = data['adr', 'causes', 'target'].edge_index
    tb = data['target', 'binds', 'compound'].edge_index

    ha = data['herb', 'causes', 'adr'].edge_index
    if ((ha[0] == herb_id) & (ha[1] == adr_id)).any():
        paths.append(f'直接关联：{h} → {a}（图中有监督边）')

    herb_compounds = set(hc[1][hc[0] == herb_id].tolist())
    adr_targets = set(at[1][at[0] == adr_id].tolist())
    herb_targets = set(ht[1][ht[0] == herb_id].tolist())

    shared_targets = herb_targets & adr_targets
    for t in list(shared_targets)[:limit]:
        paths.append(f'共享靶点：{h} → Target #{t} ← {a}')

    if herb_compounds:
        comp_to_target = {}
        for t, c in zip(tb[0].tolist(), tb[1].tolist()):
            comp_to_target.setdefault(int(c), set()).add(int(t))
        for c in herb_compounds:
            targets_via_comp = comp_to_target.get(int(c), set()) & adr_targets
            for t in list(targets_via_comp)[:2]:
                paths.append(
                    f'成分介导：{h} → Compound #{c} → Target #{t} ← {a}'
                )
            if len(paths) >= limit:
                break

    if not paths:
        paths.append('知识图谱中未发现该 CMM–ADR 对的显式短路径（模型仍基于嵌入推断）')
    return paths[:limit]
