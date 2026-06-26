import inspect

import train
from experiments.pu_training import make_weighted_batch_tensors


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
