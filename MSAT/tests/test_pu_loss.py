import torch

from experiments.pu_loss import weighted_pu_bce_loss


def test_weighted_pu_bce_loss_backpropagates():
    logits = torch.tensor([2.0, -1.0, 0.5], requires_grad=True)
    labels = torch.tensor([1.0, 0.0, 0.0])
    weights = torch.tensor([1.0, 0.8, 0.2])
    loss = weighted_pu_bce_loss(logits, labels, weights)
    loss.backward()
    assert loss.item() > 0
    assert logits.grad is not None
    assert logits.grad.shape == logits.shape


def test_lower_unlabeled_weight_reduces_loss_contribution():
    logits = torch.tensor([2.0, 2.0])
    labels = torch.tensor([0.0, 0.0])
    high = weighted_pu_bce_loss(logits, labels, torch.tensor([1.0, 1.0]))
    low = weighted_pu_bce_loss(logits, labels, torch.tensor([0.1, 0.1]))
    assert low.item() < high.item()
