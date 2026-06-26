from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_experiment_config(
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    max_folds: int,
    max_epochs: int,
) -> dict:
    return {
        "experiment": "pu_xmsat",
        "sampling_strategy": sampling_strategy,
        "loss": "weighted_pu_bce",
        "unlabeled_weight": unlabeled_weight,
        "reliable_negative_weight": reliable_negative_weight,
        "max_folds": max_folds,
        "max_epochs": max_epochs,
        "baseline": "baseline/msat-reproduction-20260626",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampling-strategy", default="hybrid")
    parser.add_argument("--unlabeled-weight", type=float, default=0.2)
    parser.add_argument("--reliable-negative-weight", type=float, default=0.8)
    parser.add_argument("--max-folds", type=int, default=1)
    parser.add_argument("--max-epochs", type=int, default=2)
    parser.add_argument("--output", default="results/pu_training_smoke_summary.json")
    args = parser.parse_args()

    payload = build_experiment_config(
        sampling_strategy=args.sampling_strategy,
        unlabeled_weight=args.unlabeled_weight,
        reliable_negative_weight=args.reliable_negative_weight,
        max_folds=args.max_folds,
        max_epochs=args.max_epochs,
    )
    payload.update(
        {
            "status": "configured",
            "training_executed": False,
            "fold_results": [],
            "mean_metrics": {},
            "note": (
                "Smoke runner is configured. Enable real one-fold training only "
                "after confirming local runtime and checkpoint policy."
            ),
        }
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
