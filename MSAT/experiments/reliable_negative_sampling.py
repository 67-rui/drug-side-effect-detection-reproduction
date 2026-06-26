from __future__ import annotations

from dataclasses import dataclass, field


Pair = tuple[int, int]


@dataclass(frozen=True)
class CandidateScore:
    herb_id: int
    adr_id: int
    reliability_score: float
    baseline_score: float | None = None
    structural_support: int | None = None
    similar_positive_support: int | None = None
    adr_frequency: int | None = None
    reason_flags: tuple[str, ...] = field(default_factory=tuple)


def normalize_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(value - lo) / (hi - lo) for value in values]


def score_reliable_negative_candidates(
    unobserved_pairs: list[Pair],
    baseline_scores: dict[Pair, float] | None = None,
    structural_support: dict[Pair, int] | None = None,
    similar_positive_support: dict[Pair, int] | None = None,
    adr_frequency: dict[int, int] | None = None,
) -> list[CandidateScore]:
    baseline_scores = baseline_scores or {}
    structural_support = structural_support or {}
    similar_positive_support = similar_positive_support or {}
    adr_frequency = adr_frequency or {}

    baseline_values = [baseline_scores.get(pair, 0.5) for pair in unobserved_pairs]
    structural_values = [
        float(structural_support.get(pair, 0)) for pair in unobserved_pairs
    ]
    similar_values = [
        float(similar_positive_support.get(pair, 0)) for pair in unobserved_pairs
    ]
    adr_freq_values = [
        float(adr_frequency.get(pair[1], 0)) for pair in unobserved_pairs
    ]

    baseline_norm = normalize_scores(baseline_values)
    structural_norm = normalize_scores(structural_values)
    similar_norm = normalize_scores(similar_values)
    adr_freq_norm = normalize_scores(adr_freq_values)

    rows: list[CandidateScore] = []
    for idx, pair in enumerate(unobserved_pairs):
        low_model = 1.0 - baseline_norm[idx]
        low_structure = 1.0 - structural_norm[idx]
        low_similar_positive = 1.0 - similar_norm[idx]
        frequency_penalty = adr_freq_norm[idx]

        score = (
            0.45 * low_model
            + 0.30 * low_structure
            + 0.20 * low_similar_positive
            + 0.05 * frequency_penalty
        )

        flags: list[str] = []
        if low_model >= 0.70:
            flags.append("low_model_score")
        if low_structure >= 0.70:
            flags.append("low_structural_support")
        if low_similar_positive >= 0.70:
            flags.append("low_similar_positive_support")

        rows.append(
            CandidateScore(
                herb_id=pair[0],
                adr_id=pair[1],
                reliability_score=float(score),
                baseline_score=baseline_scores.get(pair),
                structural_support=structural_support.get(pair),
                similar_positive_support=similar_positive_support.get(pair),
                adr_frequency=adr_frequency.get(pair[1]),
                reason_flags=tuple(flags),
            )
        )
    return rows


def select_reliable_negatives(
    candidates: list[CandidateScore],
    count: int,
    seed: int,
) -> list[CandidateScore]:
    del seed
    ordered = sorted(
        candidates,
        key=lambda row: (-row.reliability_score, row.herb_id, row.adr_id),
    )
    return ordered[:count]
