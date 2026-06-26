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


def weighted_pu_probability_bce_loss(
    probabilities: torch.Tensor,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
    eps: float = 1e-7,
) -> torch.Tensor:
    probs = probabilities.float().clamp(min=eps, max=1.0 - eps)
    labels = labels.float().to(probs.device)
    weights = sample_weights.float().to(probs.device)
    per_sample = -(
        labels * torch.log(probs)
        + (1.0 - labels) * torch.log(1.0 - probs)
    )
    return (per_sample * weights).mean()
