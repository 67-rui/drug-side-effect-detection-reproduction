import inspect

import torch

import train
from experiments.pu_training import (
    make_weighted_batch_tensors,
    train_one_epoch_weighted_probabilities,
)


def test_default_train_one_epoch_signature_is_unchanged():
    params = list(inspect.signature(train.train_one_epoch).parameters)
    assert params == ["model", "data", "optimizer", "train_edges", "train_labels", "device"]


def test_make_weighted_batch_tensors_shapes():
    batch = make_weighted_batch_tensors(
        herb_idx=[0, 1],
        adr_idx=[2, 3],
        labels=[1, 0],
        weights=[1.0, 0.2],
        device="cpu",
    )
    assert batch["edges"].shape == (2, 2)
    assert batch["labels"].tolist() == [1.0, 0.0]
    assert batch["weights"].tolist() == [1.0, 0.2]


class ProbabilityToyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.logit = torch.nn.Parameter(torch.tensor([0.0, 0.0]))

    def forward(self, x_dict, edge_index_dict, edge_attr_dict, herb_indices, adr_indices):
        del x_dict, edge_index_dict, edge_attr_dict, herb_indices, adr_indices
        return torch.sigmoid(self.logit)


class ToyData:
    x_dict = {}
    edge_index_dict = {}
    edge_attr_dict = {}


def test_train_one_epoch_weighted_probabilities_updates_probability_model():
    model = ProbabilityToyModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    edges = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
    labels = torch.tensor([1.0, 0.0])
    weights = torch.tensor([1.0, 0.2])

    before = model.logit.detach().clone()
    loss = train_one_epoch_weighted_probabilities(
        model, ToyData(), optimizer, edges, labels, weights, "cpu"
    )

    assert loss > 0
    assert not torch.equal(before, model.logit.detach())
