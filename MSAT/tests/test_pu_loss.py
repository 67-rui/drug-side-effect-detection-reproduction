import torch

from experiments.pu_loss import weighted_pu_bce_loss, weighted_pu_probability_bce_loss


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


def test_weighted_pu_probability_bce_loss_matches_manual_bce():
    probs = torch.tensor([0.8, 0.25, 0.6], requires_grad=True)
    labels = torch.tensor([1.0, 0.0, 0.0])
    weights = torch.tensor([1.0, 0.8, 0.2])

    loss = weighted_pu_probability_bce_loss(probs, labels, weights)
    expected = -(
        torch.log(torch.tensor(0.8)) * 1.0
        + torch.log(torch.tensor(0.75)) * 0.8
        + torch.log(torch.tensor(0.4)) * 0.2
    ) / 3

    assert torch.allclose(loss, expected, atol=1e-6)
    loss.backward()
    assert probs.grad is not None


def test_weighted_pu_probability_bce_loss_clamps_extreme_probs():
    probs = torch.tensor([0.0, 1.0], requires_grad=True)
    labels = torch.tensor([0.0, 1.0])
    weights = torch.tensor([1.0, 1.0])

    loss = weighted_pu_probability_bce_loss(probs, labels, weights)
    loss.backward()

    assert torch.isfinite(loss)
    assert probs.grad is not None
