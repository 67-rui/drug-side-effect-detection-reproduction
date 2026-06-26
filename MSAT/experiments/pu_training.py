from __future__ import annotations

from collections.abc import Sequence

import torch

from experiments.pu_loss import (
    weighted_pu_bce_loss,
    weighted_pu_probability_bce_loss,
)


def make_weighted_batch_tensors(
    herb_idx: Sequence[int],
    adr_idx: Sequence[int],
    labels: Sequence[int],
    weights: Sequence[float],
    device,
) -> dict[str, torch.Tensor]:
    edges = torch.tensor([herb_idx, adr_idx], dtype=torch.long, device=device)
    return {
        "edges": edges,
        "labels": torch.tensor(labels, dtype=torch.float32, device=device),
        "weights": torch.tensor(weights, dtype=torch.float64, device=device),
    }


def train_one_epoch_weighted(
    model,
    data,
    optimizer,
    train_edges: torch.Tensor,
    train_labels: torch.Tensor,
    sample_weights: torch.Tensor,
    device,
) -> float:
    model.train()
    optimizer.zero_grad()
    logits = model(
        data.x_dict,
        data.edge_index_dict,
        data.edge_attr_dict,
        train_edges[0].to(device),
        train_edges[1].to(device),
    )
    loss = weighted_pu_bce_loss(
        logits,
        train_labels.float().to(device),
        sample_weights.float().to(device),
    )
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    return float(loss.item())


def train_one_epoch_weighted_probabilities(
    model,
    data,
    optimizer,
    train_edges: torch.Tensor,
    train_labels: torch.Tensor,
    sample_weights: torch.Tensor,
    device,
    gradient_clip: float = 1.0,
) -> float:
    model.train()
    optimizer.zero_grad()
    probabilities = model(
        data.x_dict,
        data.edge_index_dict,
        data.edge_attr_dict,
        train_edges[0].to(device),
        train_edges[1].to(device),
    )
    loss = weighted_pu_probability_bce_loss(
        probabilities,
        train_labels.float().to(device),
        sample_weights.float().to(device),
    )
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=gradient_clip)
    optimizer.step()
    return float(loss.item())
