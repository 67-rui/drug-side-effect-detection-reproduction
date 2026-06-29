#!/usr/bin/env python3
"""Build HGNC-based candidate names for unmapped target graph nodes."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from inference.biobert_encoder import encode_texts


HGNC_COMPLETE_SET_URL = (
    "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"
)
CLAIM_BOUNDARY = (
    "HGNC/BioBERT matches are computational candidate labels for readability and triage only. "
    "They are not original graph ID mappings, not biological validation, and must not upgrade "
    "external evidence grades without manual database/literature confirmation."
)

CSV_FIELDS = [
    "feature",
    "node_id",
    "candidate_rank",
    "symbol",
    "name",
    "hgnc_id",
    "uniprot_ids",
    "score",
    "margin",
    "mapping_status",
]


@dataclass(frozen=True)
class HGNCCandidate:
    hgnc_id: str
    symbol: str
    name: str
    text: str
    aliases: list[str]
    previous_symbols: list[str]
    uniprot_ids: list[str]


def _split_multi_value(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in str(value).split("|") if item.strip()]


def parse_hgnc_candidates(tsv_text: str, approved_only: bool = True) -> list[HGNCCandidate]:
    """Parse HGNC complete-set TSV rows into BioBERT candidate strings."""
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    candidates: list[HGNCCandidate] = []
    for row in reader:
        status = str(row.get("status", "")).strip().lower()
        if approved_only and status != "approved":
            continue
        symbol = str(row.get("symbol", "")).strip()
        name = str(row.get("name", "")).strip()
        hgnc_id = str(row.get("hgnc_id", "")).strip()
        if not symbol or not name:
            continue
        candidates.append(
            HGNCCandidate(
                hgnc_id=hgnc_id,
                symbol=symbol,
                name=name,
                text=f"{symbol} {name}",
                aliases=_split_multi_value(row.get("alias_symbol")),
                previous_symbols=_split_multi_value(row.get("prev_symbol")),
                uniprot_ids=_split_multi_value(row.get("uniprot_ids")),
            )
        )
    return candidates


def _target_ids_from_queue(queue_payload: dict[str, Any]) -> list[int]:
    ids: list[int] = []
    seen: set[int] = set()
    for row in queue_payload.get("rows", []):
        feature = str(row.get("feature", ""))
        node_type = str(row.get("node_type", ""))
        node_id = row.get("node_id")
        if node_type == "target" and node_id not in (None, ""):
            parsed = int(node_id)
        elif feature.startswith("target:") and feature.split(":", 1)[1].isdigit():
            parsed = int(feature.split(":", 1)[1])
        else:
            continue
        if parsed not in seen:
            ids.append(parsed)
            seen.add(parsed)
    return ids


def _candidate_row(
    rank: int,
    candidate: HGNCCandidate,
    score: float,
    margin: float,
) -> dict[str, Any]:
    return {
        "rank": int(rank),
        "symbol": candidate.symbol,
        "name": candidate.name,
        "hgnc_id": candidate.hgnc_id,
        "aliases": candidate.aliases,
        "previous_symbols": candidate.previous_symbols,
        "uniprot_ids": candidate.uniprot_ids,
        "score": round(float(score), 6),
        "margin": round(float(margin), 6),
        "mapping_status": "candidate_only",
    }


def _rank_one_target(
    node_id: int,
    node_vector: np.ndarray,
    candidates: list[HGNCCandidate],
    candidate_embeddings: np.ndarray,
    top_k: int,
) -> dict[str, Any]:
    scores = np.asarray(node_vector, dtype=np.float32) @ candidate_embeddings.T
    order = np.argsort(scores)[::-1][: max(1, int(top_k))]
    full_order = np.argsort(scores)[::-1]
    second_score = float(scores[full_order[1]]) if len(full_order) > 1 else float(scores[full_order[0]])
    top_score = float(scores[full_order[0]]) if len(full_order) else 0.0
    margin = top_score - second_score
    ranked = [
        _candidate_row(
            rank=index + 1,
            candidate=candidates[int(candidate_index)],
            score=float(scores[int(candidate_index)]),
            margin=margin if index == 0 else 0.0,
        )
        for index, candidate_index in enumerate(order)
    ]
    return {
        "feature": f"target:{int(node_id)}",
        "node_id": int(node_id),
        "top_candidate": ranked[0],
        "candidates": ranked,
    }


def build_target_name_candidate_report(
    queue_payload: dict[str, Any],
    hgnc_tsv_text: str,
    target_features: dict[int, np.ndarray],
    encode_fn: Callable[..., np.ndarray] = encode_texts,
    top_k: int = 5,
    batch_size: int = 64,
) -> dict[str, Any]:
    """Build candidate target names for target ids present in the top-20 mapping queue."""
    target_ids = _target_ids_from_queue(queue_payload)
    candidates = parse_hgnc_candidates(hgnc_tsv_text)
    if not candidates:
        raise ValueError("HGNC candidate table contains no approved symbol/name rows")

    candidate_embeddings = encode_fn([candidate.text for candidate in candidates], batch_size=batch_size)
    targets = []
    missing_target_features = []
    for node_id in target_ids:
        node_vector = target_features.get(int(node_id))
        if node_vector is None:
            missing_target_features.append(int(node_id))
            continue
        targets.append(
            _rank_one_target(
                node_id=node_id,
                node_vector=node_vector,
                candidates=candidates,
                candidate_embeddings=candidate_embeddings,
                top_k=top_k,
            )
        )

    return {
        "experiment": "top20_target_name_candidates",
        "created_at": datetime.now().isoformat(),
        "summary": {
            "target_count": len(targets),
            "requested_target_count": len(target_ids),
            "missing_target_feature_count": len(missing_target_features),
            "hgnc_candidate_count": len(candidates),
            "candidate_source": "HGNC complete set",
            "candidate_source_url": HGNC_COMPLETE_SET_URL,
            "top_k_per_target": int(top_k),
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "missing_target_features": missing_target_features,
        "targets": targets,
    }


def _load_target_features(graph_path: Path, target_ids: list[int]) -> dict[int, np.ndarray]:
    graph = torch.load(graph_path, map_location="cpu", weights_only=False)
    target_x = graph["target"].x.detach().cpu().numpy()
    features: dict[int, np.ndarray] = {}
    for node_id in target_ids:
        if 0 <= int(node_id) < target_x.shape[0]:
            features[int(node_id)] = target_x[int(node_id)]
    return features


def download_hgnc_tsv(url: str = HGNC_COMPLETE_SET_URL) -> str:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def write_outputs(report: dict[str, Any], output_json: Path, output_csv: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for target in report.get("targets", []):
            for candidate in target.get("candidates", []):
                writer.writerow(
                    {
                        "feature": target.get("feature", ""),
                        "node_id": target.get("node_id", ""),
                        "candidate_rank": candidate.get("rank", ""),
                        "symbol": candidate.get("symbol", ""),
                        "name": candidate.get("name", ""),
                        "hgnc_id": candidate.get("hgnc_id", ""),
                        "uniprot_ids": "|".join(candidate.get("uniprot_ids", []) or []),
                        "score": candidate.get("score", ""),
                        "margin": candidate.get("margin", ""),
                        "mapping_status": candidate.get("mapping_status", "candidate_only"),
                    }
                )

    lines = [
        "# Target Name Candidate Report",
        "",
        f"- Targets with candidates: {report.get('summary', {}).get('target_count', 0)}",
        f"- HGNC candidates: {report.get('summary', {}).get('hgnc_candidate_count', '')}",
        f"- Source: {report.get('summary', {}).get('candidate_source', '')}",
        "",
        report.get("claim_boundary", CLAIM_BOUNDARY),
        "",
        "| Target | Top candidate | HGNC ID | UniProt | Score | Margin |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for target in report.get("targets", []):
        candidate = target.get("top_candidate", {})
        symbol = candidate.get("symbol", "")
        name = candidate.get("name", "")
        uniprot = "|".join(candidate.get("uniprot_ids", []) or [])
        lines.append(
            "| `{feature}` | {symbol} ({name}) | {hgnc_id} | {uniprot} | {score:.6f} | {margin:.6f} |".format(
                feature=target.get("feature", ""),
                symbol=str(symbol).replace("|", "/"),
                name=str(name).replace("|", "/"),
                hgnc_id=str(candidate.get("hgnc_id", "")).replace("|", "/"),
                uniprot=uniprot.replace("|", "/"),
                score=float(candidate.get("score", 0.0)),
                margin=float(candidate.get("margin", 0.0)),
            )
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_hgnc_text(path: Path | None, allow_download: bool) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")
    if allow_download:
        return download_hgnc_tsv()
    raise FileNotFoundError("HGNC TSV not provided; pass --hgnc-tsv or --download-hgnc")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build target-name candidates for top-20 mechanism targets")
    parser.add_argument("--queue", type=Path, default=Path("results/top20_entity_mapping_queue.json"))
    parser.add_argument("--graph", type=Path, default=DataConfig.GRAPH_PATH)
    parser.add_argument("--hgnc-tsv", type=Path, default=None)
    parser.add_argument("--download-hgnc", action="store_true")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/top20_target_name_candidates.json"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("results/top20_target_name_candidates.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/PU_XMSAT_TOP20_TARGET_NAME_CANDIDATES.md"),
    )
    args = parser.parse_args()

    queue_payload = json.loads(args.queue.read_text(encoding="utf-8"))
    target_ids = _target_ids_from_queue(queue_payload)
    target_features = _load_target_features(args.graph, target_ids)
    hgnc_text = _load_hgnc_text(args.hgnc_tsv, args.download_hgnc)
    report = build_target_name_candidate_report(
        queue_payload=queue_payload,
        hgnc_tsv_text=hgnc_text,
        target_features=target_features,
        encode_fn=encode_texts,
        top_k=args.top_k,
        batch_size=args.batch_size,
    )
    write_outputs(report, args.output_json, args.output_csv, args.output_md)
    print(
        "[saved]",
        args.output_json,
        "targets=",
        report["summary"]["target_count"],
        "hgnc_candidates=",
        report["summary"]["hgnc_candidate_count"],
    )


if __name__ == "__main__":
    main()
