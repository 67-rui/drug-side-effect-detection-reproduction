from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import random
import sys

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from experiments.feature_extractor import FeatureExtractor
from experiments.pu_data_utils import (
    build_positive_pair_set,
    build_unobserved_pairs,
    count_mechanistic_support,
    write_jsonl,
)
from experiments.reliable_negative_sampling import (
    CandidateScore,
    score_reliable_negative_candidates,
)


Pair = tuple[int, int]


def row_from_candidate(candidate: CandidateScore) -> dict:
    return {
        "herb_id": candidate.herb_id,
        "adr_id": candidate.adr_id,
        "reliability_score": candidate.reliability_score,
        "baseline_score": candidate.baseline_score,
        "structural_support": candidate.structural_support,
        "similar_positive_support": candidate.similar_positive_support,
        "adr_frequency": candidate.adr_frequency,
        "reason_flags": list(candidate.reason_flags),
    }


def _bounded_unobserved_pairs(
    num_herbs: int,
    num_adrs: int,
    positive_pairs: set[Pair],
    max_candidates: int,
    seed: int = DataConfig.RANDOM_SEED,
    selection: str = "random",
) -> list[Pair]:
    if max_candidates <= 0:
        return []
    if selection not in {"random", "prefix"}:
        raise ValueError(f"unknown candidate selection: {selection}")

    pairs: list[Pair] = []
    rng = random.Random(seed)
    seen = 0
    for herb_id in range(num_herbs):
        for adr_id in range(num_adrs):
            pair = (herb_id, adr_id)
            if pair in positive_pairs:
                continue
            if selection == "prefix":
                pairs.append(pair)
                if len(pairs) >= max_candidates:
                    return pairs
                continue

            seen += 1
            if len(pairs) < max_candidates:
                pairs.append(pair)
            else:
                replace_idx = rng.randrange(seen)
                if replace_idx < max_candidates:
                    pairs[replace_idx] = pair
    return sorted(pairs)


def build_candidate_rows(
    max_candidates: int | None = 1000,
    data_dir: str | Path = DataConfig.DATA_DIR,
    seed: int = DataConfig.RANDOM_SEED,
    candidate_selection: str = "random",
) -> list[dict]:
    extractor = FeatureExtractor(data_dir=data_dir, fold_split_path=DataConfig.FOLD_SPLIT_PATH)
    data = extractor.get_graph_data()
    positive_pairs = build_positive_pair_set(data)
    num_herbs = int(data["herb"].x.size(0))
    num_adrs = int(data["adr"].x.size(0))

    if max_candidates is None:
        unobserved_pairs = build_unobserved_pairs(num_herbs, num_adrs, positive_pairs)
    else:
        unobserved_pairs = _bounded_unobserved_pairs(
            num_herbs,
            num_adrs,
            positive_pairs,
            max_candidates,
            seed=seed,
            selection=candidate_selection,
        )

    structural_support = {
        pair: count_mechanistic_support(data, pair[0], pair[1])["total"]
        for pair in unobserved_pairs
    }
    adr_frequency = Counter(adr_id for _, adr_id in positive_pairs)
    candidates = score_reliable_negative_candidates(
        unobserved_pairs=unobserved_pairs,
        structural_support=structural_support,
        adr_frequency=dict(adr_frequency),
    )
    return [row_from_candidate(candidate) for candidate in candidates]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/pu_candidate_scores.jsonl")
    parser.add_argument("--data-dir", default=str(DataConfig.DATA_DIR))
    parser.add_argument("--max-candidates", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=DataConfig.RANDOM_SEED)
    parser.add_argument(
        "--candidate-selection",
        choices=["random", "prefix"],
        default="random",
        help="How to choose a bounded subset of unobserved pairs.",
    )
    parser.add_argument(
        "--all-candidates",
        action="store_true",
        help="Score all unobserved pairs instead of a bounded smoke-test sample.",
    )
    args = parser.parse_args()

    max_candidates = None if args.all_candidates else args.max_candidates
    rows = build_candidate_rows(
        max_candidates=max_candidates,
        data_dir=args.data_dir,
        seed=args.seed,
        candidate_selection=args.candidate_selection,
    )
    write_jsonl(Path(args.output), rows)
    print(f"Wrote {len(rows)} candidate scores to {args.output}")


if __name__ == "__main__":
    main()
