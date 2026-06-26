from __future__ import annotations

import torch
import torch.nn.functional as F


def weighted_pu_bce_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
) -> torch.Tensor:
    per_sample = F.binary_cross_entropy_with_logits(
        logits,
        labels.float(),
        reduction="none",
    )
    weights = sample_weights.float().to(per_sample.device)
    return (per_sample * weights).mean()
