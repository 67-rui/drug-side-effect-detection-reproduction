from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from experiments.pu_data_utils import read_jsonl


STRATEGIES = ["random", "low_score", "hybrid"]


def summarize_strategy_counts(rows: list[dict]) -> dict:
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        out[row["strategy"]][row["pair_type"]] += 1
    return {strategy: dict(counts) for strategy, counts in out.items()}


def _resolve_candidate_cache(path: Path) -> Path | None:
    if path.exists():
        return path
    sample_path = path.with_name("pu_candidate_scores.sample.jsonl")
    if sample_path.exists():
        return sample_path
    return None


def _candidate_key(row: dict) -> tuple[float, int, int]:
    return (
        float(row.get("reliability_score", 0.0)),
        int(row.get("herb_id", 0)),
        int(row.get("adr_id", 0)),
    )


def build_strategy_rows(candidates: list[dict], selection_size: int = 100) -> list[dict]:
    if not candidates:
        return [
            {"strategy": "random", "pair_type": "negative"},
            {"strategy": "hybrid", "pair_type": "reliable_negative"},
        ]

    rows: list[dict] = []
    selections = {
        "random": candidates[:selection_size],
        "low_score": sorted(candidates, key=_candidate_key)[:selection_size],
        "hybrid": sorted(candidates, key=_candidate_key, reverse=True)[:selection_size],
    }
    for strategy, selected in selections.items():
        pair_type = "reliable_negative" if strategy == "hybrid" else "negative"
        for row in selected:
            rows.append(
                {
                    "strategy": strategy,
                    "pair_type": pair_type,
                    "herb_id": row.get("herb_id"),
                    "adr_id": row.get("adr_id"),
                    "reliability_score": row.get("reliability_score"),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/pu_negative_sampling_summary.json")
    parser.add_argument("--candidate-cache", default="results/pu_candidate_scores.jsonl")
    parser.add_argument("--selection-size", type=int, default=100)
    args = parser.parse_args()

    cache_path = _resolve_candidate_cache(Path(args.candidate_cache))
    candidates = read_jsonl(cache_path) if cache_path is not None else []
    rows = build_strategy_rows(candidates, selection_size=args.selection_size)
    payload = {
        "experiment": "negative_sampling_ablation",
        "strategies": STRATEGIES,
        "candidate_cache": str(cache_path) if cache_path is not None else None,
        "selection_counts": summarize_strategy_counts(rows),
        "output_files": {},
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
