import json
from pathlib import Path

import pytest
import torch

from experiments.full_msat_pu_training import (
    FullMSATPUConfig,
    _export_checkpoint,
    _checkpoint_metadata_path,
    _checkpoint_path,
    build_checkpoint_metadata,
    formal_checkpoint_prefix,
    write_checkpoint_metadata,
)


def test_formal_checkpoint_prefix_uses_safe_pu_xmsat_tokens():
    prefix = formal_checkpoint_prefix(
        backend="full_msat_pu",
        sampling_strategy="hybrid",
        seed=2026,
        max_pairs=66015,
        threshold_strategy="val_f1",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
    )

    assert prefix == "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8"
    assert " " not in prefix
    assert "." not in prefix
    assert "/" not in prefix


def test_checkpoint_path_appends_fold_under_explicit_directory(tmp_path):
    cfg = FullMSATPUConfig(
        max_epochs=1,
        max_pairs=66015,
        checkpoint_prefix="pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8",
        checkpoint_dir=tmp_path,
        save_checkpoints=True,
        threshold_strategy="val_f1",
    )

    path = _checkpoint_path(cfg, fold_idx=0)

    assert path == tmp_path / "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt"
    assert _checkpoint_metadata_path(path) == tmp_path / "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.metadata.json"
    assert "best_model" not in path.name


def test_checkpoint_metadata_records_reproducibility_context(tmp_path):
    checkpoint = tmp_path / "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt"
    metadata = build_checkpoint_metadata(
        checkpoint_path=checkpoint,
        backend="full_msat_pu",
        sampling_strategy="hybrid",
        seed=2026,
        fold_idx=0,
        max_pairs=66015,
        threshold_strategy="val_f1",
        unlabeled_weight=0.2,
        reliable_negative_weight=0.8,
        best_epoch=54,
        best_val_auc=0.9804,
    )

    assert metadata["backend"] == "full_msat_pu"
    assert metadata["sampling_strategy"] == "hybrid"
    assert metadata["seed"] == 2026
    assert metadata["fold"] == 0
    assert metadata["pair_budget"] == 66015
    assert metadata["threshold_strategy"] == "val_f1"
    assert metadata["unlabeled_weight"] == 0.2
    assert metadata["reliable_negative_weight"] == 0.8
    assert metadata["best_epoch"] == 54
    assert metadata["best_val_auc"] == 0.9804
    assert metadata["validation_best_epoch"] == 54
    assert metadata["validation_auc"] == 0.9804
    assert metadata["checkpoint_path"] == str(checkpoint)
    assert metadata["metadata_path"] == str(_checkpoint_metadata_path(checkpoint))
    assert metadata["protocol_version"] == "2026-06-23-val-test-edge-hidden"
    assert metadata["protocol"]["version"] == "2026-06-23-val-test-edge-hidden"

    metadata_path = write_checkpoint_metadata(metadata, checkpoint)
    written = json.loads(Path(metadata_path).read_text())
    assert written == metadata


def test_export_checkpoint_refuses_to_overwrite_existing_file_by_default(tmp_path):
    cfg = FullMSATPUConfig(
        max_epochs=1,
        max_pairs=66015,
        checkpoint_prefix="pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8",
        checkpoint_dir=tmp_path,
        save_checkpoints=True,
        threshold_strategy="val_f1",
    )
    existing = _checkpoint_path(cfg, fold_idx=0)
    existing.write_bytes(b"already here")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        _export_checkpoint(
            {"weight": torch.tensor([1.0])},
            cfg,
            fold_idx=0,
            sampling_strategy="hybrid",
            seed=2026,
            unlabeled_weight=0.2,
            reliable_negative_weight=0.8,
            best_epoch=1,
            best_val_auc=0.9,
        )

    assert existing.read_bytes() == b"already here"
