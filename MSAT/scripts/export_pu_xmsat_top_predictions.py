#!/usr/bin/env python3
"""Export PU-XMSAT top-ranking predictions for unobserved CMM-ADR pairs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from inference.artifact_manifest import file_manifest
from inference.contribution_scoring import extract_node_refs_from_path


DEFAULT_TOP_K = 50
DEFAULT_CANDIDATE_SOURCE = "pu_xmsat_global_unobserved_pairs"
DEFAULT_OUTPUT_JSON = MSAT_ROOT / "results" / "pu_xmsat_top_predictions.json"
DEFAULT_OUTPUT_CSV = MSAT_ROOT / "results" / "pu_xmsat_top_predictions.csv"
DEFAULT_OUTPUT_MD = MSAT_ROOT / "results" / "PU_XMSAT_TOP_PREDICTIONS_EXPORT.md"

CLAIM_BOUNDARY = (
    "PU-XMSAT prediction scores are model-ranked hypotheses for CMM-ADR triage; "
    "they are not external clinical validation, confirmed causal effects, or medical recommendations."
)

CSV_FIELDS = [
    "rank",
    "herb_id",
    "herb_name",
    "herb_latin",
    "herb_chinese",
    "herb_pinyin",
    "adr_id",
    "adr_pt",
    "prediction_score",
    "score",
    "original_score",
    "has_explicit_mechanism_path",
    "mechanism_path_count",
    "explicit_mechanism_path_count",
    "top_mechanism_paths",
    "source",
    "candidate_source",
    "checkpoint_path",
    "is_final_10fold_export",
    "claim_boundary",
]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export PU-XMSAT top-ranking predictions for unobserved CMM-ADR pairs."
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="PU-XMSAT checkpoint to load. Required for CLI execution.",
    )
    parser.add_argument("--device", default=None, help="Torch device for MSATPredictor.")
    parser.add_argument(
        "--entity-names-path",
        type=Path,
        default=None,
        help="Optional entity_names.json override passed to MSATPredictor.",
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--max-herbs", type=int, default=None)
    parser.add_argument("--candidate-limit", type=int, default=None)
    parser.add_argument("--score-batch-size", type=int, default=2048)
    parser.add_argument(
        "--checkpoint-is-final-pu-xmsat",
        "--final-10fold-export",
        action="store_true",
        dest="checkpoint_is_final_pu_xmsat",
        help="Mark the checkpoint as the final 10-fold PU-XMSAT export unless its path indicates pilot/fallback/smoke/debug scope.",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser


def _record_field(record: Any, field: str) -> str:
    value = getattr(record, field, "")
    return "" if value is None else str(value)


def _herb_metadata(names: Any, herb_id: int) -> dict[str, str]:
    herbs = getattr(names, "herbs", {}) or {}
    record = herbs.get(int(herb_id)) if hasattr(herbs, "get") else None
    if hasattr(names, "herb_display"):
        herb_name = names.herb_display(int(herb_id))
    else:
        herb_name = f"CMM #{herb_id}"
    return {
        "herb_name": herb_name,
        "herb_latin": _record_field(record, "latin"),
        "herb_chinese": _record_field(record, "chinese"),
        "herb_pinyin": _record_field(record, "pinyin"),
    }


def _adr_pt(names: Any, adr_id: int) -> str:
    adrs = getattr(names, "adrs", {}) or {}
    record = adrs.get(int(adr_id)) if hasattr(adrs, "get") else None
    meddra_pt = _record_field(record, "meddra_pt")
    if meddra_pt:
        return meddra_pt
    if hasattr(names, "adr_display"):
        return names.adr_display(int(adr_id))
    return f"ADR #{adr_id}"


def _path_texts(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        for key in ("path", "path_text", "template"):
            text = value.get(key)
            if isinstance(text, str) and text.strip():
                return [text.strip()]
        return []
    if isinstance(value, list):
        paths: list[str] = []
        for item in value:
            paths.extend(_path_texts(item))
        return paths
    text = str(value).strip()
    return [text] if text else []


def _candidate_paths(predictor: Any, herb_id: int, adr_id: int) -> list[str]:
    if hasattr(predictor, "explain_herb_adr"):
        return _path_texts(predictor.explain_herb_adr(int(herb_id), int(adr_id)))

    names = getattr(predictor, "names", None)
    if hasattr(predictor, "data") and names is not None:
        from inference.graph_utils import explain_herb_adr

        return _path_texts(
            explain_herb_adr(
                predictor.data,
                int(herb_id),
                int(adr_id),
                herb_label=_herb_metadata(names, int(herb_id))["herb_name"],
                adr_label=_adr_pt(names, int(adr_id)),
            )
        )

    if hasattr(predictor, "predict_pair"):
        pair = predictor.predict_pair(int(herb_id), int(adr_id))
        return _path_texts(pair.get("paths") or pair.get("top_mechanism_paths"))

    return []


def _explicit_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if extract_node_refs_from_path(path)]


def _checkpoint_context(
    checkpoint_path: str | Path,
    checkpoint_is_final_pu_xmsat: bool,
) -> dict[str, Any]:
    checkpoint_text = str(checkpoint_path)
    lowered = checkpoint_text.lower()
    scoped_tokens = ("pilot", "fallback", "smoke", "debug")
    scoped_checkpoint = any(token in lowered for token in scoped_tokens)
    is_final = bool(checkpoint_is_final_pu_xmsat) and not scoped_checkpoint

    if is_final:
        label = "final_10fold_pu_xmsat_export"
        limitations = (
            "Checkpoint was explicitly marked as part of the final 10-fold PU-XMSAT export; "
            "candidate claims remain bounded by the prediction-score claim boundary."
        )
    elif scoped_checkpoint:
        label = "limited_scope_checkpoint"
        limitations = (
            "This is not final 10-fold export output because the checkpoint path indicates "
            "pilot, smoke, fallback, or debug scope. Treat rankings as scoped model "
            "triage candidates only."
        )
    else:
        label = "unmarked_checkpoint"
        limitations = (
            "This is not final 10-fold export output unless the run is explicitly marked "
            "with --checkpoint-is-final-pu-xmsat and supported by the checkpoint protocol."
        )

    return {
        "checkpoint_context": label,
        "is_final_10fold_export": is_final,
        "path_indicates_limited_scope": scoped_checkpoint,
        "scope_limitations": limitations,
    }


def _validate_positive_int(value: int | None, name: str) -> None:
    if value is not None and int(value) <= 0:
        raise ValueError(f"{name} must be a positive integer when provided")


def build_top_prediction_export(
    predictor: Any,
    checkpoint_path: str | Path,
    top_k: int = DEFAULT_TOP_K,
    *,
    max_herbs: int | None = None,
    candidate_limit: int | None = None,
    score_batch_size: int = 2048,
    checkpoint_is_final_pu_xmsat: bool = False,
    candidate_source: str = DEFAULT_CANDIDATE_SOURCE,
) -> dict[str, Any]:
    requested_top_k = int(top_k)
    _validate_positive_int(requested_top_k, "top_k")
    _validate_positive_int(max_herbs, "max_herbs")
    _validate_positive_int(candidate_limit, "candidate_limit")
    _validate_positive_int(score_batch_size, "score_batch_size")

    n_herb = int(getattr(predictor, "n_herb"))
    n_adr = int(getattr(predictor, "n_adr"))
    herb_count = min(n_herb, int(max_herbs) if max_herbs is not None else n_herb)
    known_map = getattr(predictor, "known_map", {}) or {}
    names = getattr(predictor, "names", None)

    candidates: list[tuple[float, int, int]] = []
    scored_pair_count = 0
    excluded_known_positive_count = 0
    limit_reached = False

    for herb_id in range(herb_count):
        scores = predictor.score_herb_all_adrs(int(herb_id), batch_size=int(score_batch_size))
        known_adrs = set(known_map.get(int(herb_id), set()))
        for adr_id in range(min(n_adr, len(scores))):
            scored_pair_count += 1
            if int(adr_id) in known_adrs:
                excluded_known_positive_count += 1
                continue
            candidates.append((float(scores[adr_id]), int(herb_id), int(adr_id)))
            if candidate_limit is not None and len(candidates) >= int(candidate_limit):
                limit_reached = True
                break
        if limit_reached:
            break

    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    checkpoint_text = str(checkpoint_path)
    context = _checkpoint_context(
        checkpoint_text,
        checkpoint_is_final_pu_xmsat=checkpoint_is_final_pu_xmsat,
    )

    rows: list[dict[str, Any]] = []
    for rank, (score, herb_id, adr_id) in enumerate(candidates[:requested_top_k], start=1):
        paths = _candidate_paths(predictor, herb_id, adr_id)
        explicit_paths = _explicit_paths(paths)
        herb_meta = _herb_metadata(names, herb_id) if names is not None else {
            "herb_name": f"CMM #{herb_id}",
            "herb_latin": "",
            "herb_chinese": "",
            "herb_pinyin": "",
        }
        row = {
            "rank": rank,
            "herb_id": herb_id,
            **herb_meta,
            "adr_id": adr_id,
            "adr_pt": _adr_pt(names, adr_id) if names is not None else f"ADR #{adr_id}",
            "prediction_score": score,
            "score": score,
            "original_score": score,
            "has_explicit_mechanism_path": bool(explicit_paths),
            "mechanism_path_count": len(paths),
            "explicit_mechanism_path_count": len(explicit_paths),
            "top_mechanism_paths": paths,
            "explicit_mechanism_paths": explicit_paths,
            "source": candidate_source,
            "candidate_source": candidate_source,
            "checkpoint_path": checkpoint_text,
            "is_final_10fold_export": context["is_final_10fold_export"],
        }
        rows.append(row)

    payload = {
        "experiment": "pu_xmsat_top_prediction_export",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "candidate_pool": "all scored CMM-ADR pairs excluding predictor.known_map positive edges",
            "known_positive_exclusion": "predictor.known_map",
            "scoring_method": "MSATPredictor.score_herb_all_adrs",
            "top_k": requested_top_k,
            "score_batch_size": int(score_batch_size),
            "max_herbs": max_herbs,
            "candidate_limit": candidate_limit,
        },
        "candidate_source": candidate_source,
        "checkpoint_path": checkpoint_text,
        "checkpoint": file_manifest(checkpoint_text),
        "checkpoint_context": context,
        "checkpoint_is_final_pu_xmsat": context["is_final_10fold_export"],
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": {
            "requested_top_k": requested_top_k,
            "selected_count": len(rows),
            "scored_pair_count": scored_pair_count,
            "excluded_known_positive_count": excluded_known_positive_count,
            "available_unobserved_candidate_count": len(candidates),
            "herb_count": herb_count,
            "adr_count": n_adr,
            "candidate_limit_reached": limit_reached,
            "explicit_path_candidate_count": sum(
                1 for row in rows if row["has_explicit_mechanism_path"]
            ),
        },
        "rows": rows,
        "candidates": rows,
    }
    return payload


def _csv_value(value: Any) -> Any:
    if isinstance(value, list):
        return " || ".join(str(item) for item in value)
    return value


def _write_markdown(payload: dict[str, Any], output_md: str | Path) -> None:
    context = payload["checkpoint_context"]
    summary = payload["summary"]
    lines = [
        "# PU-XMSAT Top Predictions Export",
        "",
        f"- Created at: {payload['created_at']}",
        f"- Checkpoint: {payload['checkpoint_path']}",
        f"- Candidate source: {payload['candidate_source']}",
        f"- Final 10-fold export: {context['is_final_10fold_export']}",
        f"- Scope limitations: {context['scope_limitations']}",
        f"- Claim boundary: {payload['claim_boundary']}",
        "",
        "## Summary",
        "",
        f"- Requested top K: {summary['requested_top_k']}",
        f"- Selected rows: {summary['selected_count']}",
        f"- Known positive pairs excluded: {summary['excluded_known_positive_count']}",
        f"- Rows with explicit mechanism paths: {summary['explicit_path_candidate_count']}",
        "",
        "## Top Rows",
        "",
        "| Rank | Herb ID | Herb | ADR ID | ADR PT | Score | Explicit paths |",
        "| ---: | ---: | --- | ---: | --- | ---: | ---: |",
    ]
    for row in payload["rows"][:50]:
        lines.append(
            "| {rank} | {herb_id} | {herb_name} | {adr_id} | {adr_pt} | {score:.6f} | {paths} |".format(
                rank=row["rank"],
                herb_id=row["herb_id"],
                herb_name=str(row["herb_name"]).replace("|", "/"),
                adr_id=row["adr_id"],
                adr_pt=str(row["adr_pt"]).replace("|", "/"),
                score=float(row["prediction_score"]),
                paths=row["explicit_mechanism_path_count"],
            )
        )
    Path(output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_prediction_artifacts(
    payload: dict[str, Any],
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_csv: str | Path = DEFAULT_OUTPUT_CSV,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
) -> None:
    output_json = Path(output_json)
    output_csv = Path(output_csv)
    output_md = Path(output_md)
    for path in (output_json, output_csv, output_md):
        path.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in payload["rows"]:
            csv_row = {
                field: _csv_value(row.get(field, payload.get(field, "")))
                for field in CSV_FIELDS
            }
            csv_row["claim_boundary"] = payload["claim_boundary"]
            writer.writerow(csv_row)

    _write_markdown(payload, output_md)


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.checkpoint is None:
        parser.error("--checkpoint is required for PU-XMSAT top prediction export")

    from inference.predictor import MSATPredictor

    predictor = MSATPredictor(
        checkpoint=args.checkpoint,
        device=args.device,
        entity_names_path=args.entity_names_path,
    )
    payload = build_top_prediction_export(
        predictor,
        checkpoint_path=args.checkpoint,
        top_k=args.top_k,
        max_herbs=args.max_herbs,
        candidate_limit=args.candidate_limit,
        score_batch_size=args.score_batch_size,
        checkpoint_is_final_pu_xmsat=args.checkpoint_is_final_pu_xmsat,
    )
    write_top_prediction_artifacts(payload, args.output_json, args.output_csv, args.output_md)
    print(
        json.dumps(
            {
                "selected_count": payload["summary"]["selected_count"],
                "checkpoint_path": payload["checkpoint_path"],
                "is_final_10fold_export": payload["checkpoint_context"]["is_final_10fold_export"],
                "output_json": str(args.output_json),
                "output_csv": str(args.output_csv),
                "output_md": str(args.output_md),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
