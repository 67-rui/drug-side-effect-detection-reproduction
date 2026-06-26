from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class FullMSATPUConfig:
    max_epochs: int
    max_pairs: int
    patience: int = 100
    learning_rate: float = 0.0004
    weight_decay: float = 1e-5
    training_backend: str = "full_msat_pu"
    checkpoint_prefix: str = "pu_xmsat"
    save_checkpoints: bool = False
    checkpoint_dir: Path = Path("saved_models")


def summarize_full_fold_results(fold_results: list[dict]) -> dict:
    metrics = {}
    for metric in ["auc", "auprc", "f1", "mcc"]:
        values = [
            float(row["test_metrics"][metric])
            for row in fold_results
            if metric in row.get("test_metrics", {})
        ]
        metrics[metric] = float(np.mean(values)) if values else None

    final_losses = []
    for row in fold_results:
        losses = row.get("training_history", {}).get("train_loss", [])
        if losses:
            final_losses.append(float(losses[-1]))
    metrics["final_loss"] = float(np.mean(final_losses)) if final_losses else None
    return metrics
