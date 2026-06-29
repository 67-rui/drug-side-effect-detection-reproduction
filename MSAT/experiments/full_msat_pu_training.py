from __future__ import annotations

import copy
from dataclasses import dataclass
import json
from pathlib import Path
import re
import time

import numpy as np
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

from config import DataConfig, ModelConfig, TrainingConfig
from experiments.feature_extractor import FeatureExtractor
from experiments.cluster_holdout_generalization import (
    build_cluster_holdout_split,
    cluster_herb_features,
    summarize_cluster_holdout_split,
)
from experiments.pu_data_utils import read_jsonl
from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.pu_training import train_one_epoch_weighted_probabilities
from experiments.reliable_negative_sampling import CandidateScore, select_reliable_negatives
from model import MSATTCMFSFinal
from reproduction_protocol import protocol_metadata
from train import (
    _evaluation_positive_pair_set,
    _remove_cmm_adr_pairs,
    _state_dict_to_cpu,
    evaluate,
    find_optimal_threshold,
    prediction_payload,
)


MSAT_ROOT = Path(__file__).resolve().parents[1]


def _seed_fold_training(seed: int) -> None:
    seed = int(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


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
    checkpoint_dir: Path = Path("saved_models/pu_xmsat_formal")
    threshold_strategy: str = "fixed_0_5"
    allow_checkpoint_overwrite: bool = False
    split_mode: str = "official_fold"
    n_clusters: int = 10
    cluster_feature: str = "herb_x"


def _safe_float_token(value: float) -> str:
    return str(float(value)).replace(".", "p").replace("-", "m")


def _safe_name_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", str(value).strip())
    token = re.sub(r"_+", "_", token).strip("_")
    return token or "unknown"


def _safe_int_token(value: int) -> str:
    return str(int(value)).replace("-", "m")


def _compact_threshold_token(threshold_strategy: str) -> str:
    if threshold_strategy == "val_f1":
        return "valf1"
    if threshold_strategy == "fixed_0_5":
        return "fixed0p5"
    return _safe_name_token(threshold_strategy)


def formal_checkpoint_prefix(
    backend: str,
    sampling_strategy: str,
    seed: int,
    max_pairs: int,
    threshold_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
) -> str:
    return (
        f"pu_xmsat_{_safe_name_token(backend)}_{_safe_name_token(sampling_strategy)}_"
        f"seed{_safe_int_token(seed)}_pairs{_safe_int_token(max_pairs)}_"
        f"{_compact_threshold_token(threshold_strategy)}_"
        f"u{_safe_float_token(unlabeled_weight)}_"
        f"rn{_safe_float_token(reliable_negative_weight)}"
    )


def choose_threshold(
    val_probs,
    val_labels,
    strategy: str = "fixed_0_5",
) -> tuple[float, float | None]:
    if strategy == "fixed_0_5":
        return 0.5, None
    if strategy == "val_f1":
        threshold, val_f1 = find_optimal_threshold(
            np.asarray(val_probs),
            np.asarray(val_labels),
        )
        return float(threshold), float(val_f1)
    raise ValueError(f"unknown threshold strategy: {strategy}")


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


def _candidate_scores_from_cache(path: Path) -> list[CandidateScore]:
    if not path.exists():
        fallback = path.with_name("pu_candidate_scores.sample.jsonl")
        if fallback.exists():
            path = fallback
        else:
            return []

    rows = read_jsonl(path)
    return [
        CandidateScore(
            herb_id=int(row["herb_id"]),
            adr_id=int(row["adr_id"]),
            reliability_score=float(row.get("reliability_score", 0.0)),
            baseline_score=row.get("baseline_score"),
            structural_support=row.get("structural_support"),
            similar_positive_support=row.get("similar_positive_support"),
            adr_frequency=row.get("adr_frequency"),
            reason_flags=tuple(row.get("reason_flags", [])),
        )
        for row in rows
    ]


def _positive_pairs_from_train_data(
    train_data: dict,
    train_indices: np.ndarray,
    limit: int,
    allowed_train_herbs: set[int] | None = None,
) -> list[tuple[int, int]]:
    positives = [
        (int(train_data["herb_indices"][idx]), int(train_data["adr_indices"][idx]))
        for idx in train_indices
        if int(train_data["labels"][idx]) == 1
        and (
            allowed_train_herbs is None
            or int(train_data["herb_indices"][idx]) in allowed_train_herbs
        )
    ]
    return positives[:limit]


def _all_positive_pairs(data) -> set[tuple[int, int]]:
    edge_index = data["herb", "causes", "adr"].edge_index
    return {
        (int(edge_index[0, idx]), int(edge_index[1, idx]))
        for idx in range(edge_index.size(1))
    }


def _select_candidate_scores(
    candidates: list[CandidateScore],
    count: int,
    sampling_strategy: str,
    seed: int,
) -> list[CandidateScore]:
    if count <= 0:
        return []
    if sampling_strategy == "hybrid":
        return select_reliable_negatives(candidates, count=count, seed=seed)
    if sampling_strategy == "low_score":
        return sorted(
            candidates,
            key=lambda row: (row.reliability_score, row.herb_id, row.adr_id),
        )[:count]
    if sampling_strategy == "random":
        rng = np.random.RandomState(seed)
        order = rng.permutation(len(candidates))
        return [candidates[int(idx)] for idx in order[:count]]
    raise ValueError(f"unknown sampling strategy: {sampling_strategy}")


def _first_unobserved_pairs(
    num_herbs: int,
    num_adrs: int,
    positive_pairs: set[tuple[int, int]],
    excluded_pairs: set[tuple[int, int]],
    count: int,
    allowed_herbs: set[int] | None = None,
) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    if count <= 0:
        return pairs
    herb_ids = sorted(allowed_herbs) if allowed_herbs is not None else range(num_herbs)
    for herb_id in herb_ids:
        for adr_id in range(num_adrs):
            pair = (herb_id, adr_id)
            if pair in positive_pairs or pair in excluded_pairs:
                continue
            pairs.append(pair)
            if len(pairs) >= count:
                return pairs
    return pairs


def _build_node_degrees_dict(data) -> dict[str, torch.Tensor]:
    node_degrees_dict = {}
    for ntype in data.node_types:
        degree = torch.zeros(data[ntype].x.size(0))
        for edge_type, edge_index in data.edge_index_dict.items():
            if edge_type[2] == ntype:
                degree += torch.bincount(
                    edge_index[1],
                    minlength=data[ntype].x.size(0),
                ).float()
        node_degrees_dict[ntype] = degree
    return node_degrees_dict


def build_full_fold_pu_arrays(
    train_data: dict,
    train_indices: np.ndarray,
    num_herbs: int,
    num_adrs: int,
    all_positive_pairs: set[tuple[int, int]],
    reliable_negative_weight: float,
    unlabeled_weight: float,
    max_pairs: int,
    candidate_cache: str | Path,
    sampling_strategy: str,
    seed: int,
    allowed_train_herbs: set[int] | None = None,
) -> tuple[dict[str, np.ndarray], dict]:
    per_type = max(1, int(max_pairs) // 3)
    positive_pairs = _positive_pairs_from_train_data(
        train_data,
        train_indices,
        limit=per_type,
        allowed_train_herbs=allowed_train_herbs,
    )
    positive_pair_set = set(positive_pairs)

    candidates = [
        row
        for row in _candidate_scores_from_cache(Path(candidate_cache))
        if 0 <= row.herb_id < num_herbs
        and 0 <= row.adr_id < num_adrs
        and (row.herb_id, row.adr_id) not in all_positive_pairs
        and (allowed_train_herbs is None or row.herb_id in allowed_train_herbs)
    ]
    reliable_negatives = _select_candidate_scores(
        candidates,
        count=per_type,
        sampling_strategy=sampling_strategy,
        seed=seed,
    )
    reliable_pair_set = {(row.herb_id, row.adr_id) for row in reliable_negatives}

    candidate_unlabeled = [
        (row.herb_id, row.adr_id)
        for row in candidates
        if (row.herb_id, row.adr_id) not in positive_pair_set
        and (row.herb_id, row.adr_id) not in reliable_pair_set
    ][:per_type]

    excluded_pairs = positive_pair_set | reliable_pair_set | set(candidate_unlabeled)
    if len(reliable_negatives) < per_type:
        fallback_reliable = _first_unobserved_pairs(
            num_herbs,
            num_adrs,
            positive_pairs=all_positive_pairs,
            excluded_pairs=excluded_pairs,
            count=per_type - len(reliable_negatives),
            allowed_herbs=allowed_train_herbs,
        )
        reliable_negatives.extend(
            CandidateScore(herb_id=h, adr_id=a, reliability_score=0.0)
            for h, a in fallback_reliable
        )
        reliable_pair_set = {(row.herb_id, row.adr_id) for row in reliable_negatives}
        excluded_pairs = positive_pair_set | reliable_pair_set | set(candidate_unlabeled)

    if len(candidate_unlabeled) < per_type:
        candidate_unlabeled.extend(
            _first_unobserved_pairs(
                num_herbs,
                num_adrs,
                positive_pairs=all_positive_pairs,
                excluded_pairs=excluded_pairs,
                count=per_type - len(candidate_unlabeled),
                allowed_herbs=allowed_train_herbs,
            )
        )

    arrays = build_pu_training_arrays(
        positive_pairs=positive_pairs,
        reliable_negatives=reliable_negatives,
        unlabeled_pairs=candidate_unlabeled,
        unlabeled_weight=unlabeled_weight,
        reliable_negative_weight=reliable_negative_weight,
    )
    metadata = {
        "positive_pairs": len(positive_pairs),
        "reliable_negative_pairs": len(reliable_negatives),
        "unlabeled_pairs": len(candidate_unlabeled),
        "total_pairs": int(len(arrays["label"])),
        "sampling_strategy": sampling_strategy,
        "allowed_train_herb_count": (
            len(allowed_train_herbs) if allowed_train_herbs is not None else num_herbs
        ),
        "excluded_herb_count": (
            num_herbs - len(allowed_train_herbs) if allowed_train_herbs is not None else 0
        ),
    }
    return arrays, metadata


def _cluster_holdout_fold_data(
    data,
    all_positive_pairs: set[tuple[int, int]],
    fold_idx: int,
    config: FullMSATPUConfig,
    seed: int,
) -> tuple[dict, dict, dict, set[int]]:
    if config.cluster_feature != "herb_x":
        raise ValueError("cluster_feature currently supports only 'herb_x'")
    herb_features = data["herb"].x.detach().cpu().numpy()
    cluster_labels = cluster_herb_features(
        herb_features,
        n_clusters=int(config.n_clusters),
        seed=int(seed),
    )
    holdout_cluster = int(fold_idx) % int(config.n_clusters)
    positive_pairs = np.asarray(sorted(all_positive_pairs), dtype=np.int64)
    split = build_cluster_holdout_split(
        positive_pairs=positive_pairs,
        cluster_labels=cluster_labels,
        holdout_cluster=holdout_cluster,
        num_adrs=int(data["adr"].x.size(0)),
        neg_ratio=DataConfig.TEST_NEG_RATIO,
        seed=int(seed) + int(fold_idx),
    )
    summary = summarize_cluster_holdout_split(split)
    summary.update(
        {
            "n_clusters": int(config.n_clusters),
            "cluster_feature": config.cluster_feature,
            "cluster_label_counts": {
                str(label): int((cluster_labels == label).sum())
                for label in sorted(set(cluster_labels.tolist()))
            },
        }
    )
    allowed_train_herbs = set(range(int(data["herb"].x.size(0)))) - set(split["heldout_herbs"])
    return split["train_data"], split["test_data"], summary, allowed_train_herbs


def _checkpoint_path(config: FullMSATPUConfig, fold_idx: int) -> Path:
    checkpoint_dir = config.checkpoint_dir
    if not checkpoint_dir.is_absolute():
        checkpoint_dir = MSAT_ROOT / checkpoint_dir
    return checkpoint_dir / f"{config.checkpoint_prefix}_fold{fold_idx}.pt"


def _checkpoint_metadata_path(checkpoint_path: Path) -> Path:
    return checkpoint_path.with_suffix(".metadata.json")


def build_checkpoint_metadata(
    checkpoint_path: str | Path,
    backend: str,
    sampling_strategy: str,
    seed: int,
    fold_idx: int,
    max_pairs: int,
    threshold_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    best_epoch: int,
    best_val_auc: float,
) -> dict:
    checkpoint_path = Path(checkpoint_path)
    metadata_path = _checkpoint_metadata_path(checkpoint_path)
    protocol = protocol_metadata()
    return {
        "backend": backend,
        "sampling_strategy": sampling_strategy,
        "seed": int(seed),
        "fold": int(fold_idx),
        "pair_budget": int(max_pairs),
        "threshold_strategy": threshold_strategy,
        "unlabeled_weight": float(unlabeled_weight),
        "reliable_negative_weight": float(reliable_negative_weight),
        "best_epoch": int(best_epoch),
        "best_val_auc": float(best_val_auc),
        "validation_best_epoch": int(best_epoch),
        "validation_auc": float(best_val_auc),
        "protocol_version": protocol["version"],
        "protocol": protocol,
        "checkpoint_path": str(checkpoint_path),
        "metadata_path": str(metadata_path),
    }


def write_checkpoint_metadata(metadata: dict, checkpoint_path: str | Path) -> Path:
    metadata_path = _checkpoint_metadata_path(Path(checkpoint_path))
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return metadata_path


def _export_checkpoint(
    best_state: dict,
    config: FullMSATPUConfig,
    fold_idx: int,
    sampling_strategy: str,
    seed: int,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    best_epoch: int,
    best_val_auc: float,
) -> tuple[Path, Path]:
    checkpoint_path = _checkpoint_path(config, fold_idx)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = _checkpoint_metadata_path(checkpoint_path)
    if not config.allow_checkpoint_overwrite:
        existing_paths = [path for path in (checkpoint_path, metadata_path) if path.exists()]
        if existing_paths:
            existing = ", ".join(str(path) for path in existing_paths)
            raise FileExistsError(
                "refusing to overwrite existing PU-XMSAT checkpoint artifact(s): "
                f"{existing}. Use allow_checkpoint_overwrite=True only for an intentional rerun."
            )
    torch.save(_state_dict_to_cpu(best_state), checkpoint_path)
    metadata = build_checkpoint_metadata(
        checkpoint_path=checkpoint_path,
        backend=config.training_backend,
        sampling_strategy=sampling_strategy,
        seed=seed,
        fold_idx=fold_idx,
        max_pairs=config.max_pairs,
        threshold_strategy=config.threshold_strategy,
        unlabeled_weight=unlabeled_weight,
        reliable_negative_weight=reliable_negative_weight,
        best_epoch=best_epoch,
        best_val_auc=best_val_auc,
    )
    metadata_path = write_checkpoint_metadata(metadata, checkpoint_path)
    return checkpoint_path, metadata_path


def run_full_msat_pu_fold(
    fold_idx: int,
    config: FullMSATPUConfig,
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    candidate_cache: str | Path,
    seed: int,
) -> dict:
    fold_start_time = time.time()
    _seed_fold_training(seed + fold_idx)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
        n_folds=DataConfig.N_FOLDS,
        neg_ratio=DataConfig.NEG_RATIO,
        test_neg_ratio=DataConfig.TEST_NEG_RATIO,
        random_seed=DataConfig.RANDOM_SEED,
    )
    data = copy.deepcopy(extractor.get_graph_data())
    all_positive_pairs = _all_positive_pairs(data)
    cluster_protocol = {}
    allowed_train_herbs = None
    if config.split_mode == "official_fold":
        train_data, test_data = extractor.load_fold_data(fold_idx)
    elif config.split_mode == "cluster_holdout":
        train_data, test_data, cluster_protocol, allowed_train_herbs = _cluster_holdout_fold_data(
            data=data,
            all_positive_pairs=all_positive_pairs,
            fold_idx=fold_idx,
            config=config,
            seed=seed,
        )
    else:
        raise ValueError(f"unknown split_mode: {config.split_mode}")

    rng = np.random.RandomState(TrainingConfig.RANDOM_STATE + fold_idx)
    indices = rng.permutation(len(train_data["labels"]))
    n_val = int(len(train_data["labels"]) * (1 - TrainingConfig.TRAIN_VAL_SPLIT))
    n_val = max(1, n_val)
    val_sub = indices[:n_val]
    train_sub = indices[n_val:]

    hidden_eval_pos_pairs = _evaluation_positive_pair_set(
        train_data["herb_indices"][val_sub],
        train_data["adr_indices"][val_sub],
        train_data["labels"][val_sub],
        test_data["herb_indices"],
        test_data["adr_indices"],
        test_data["labels"],
    )
    data = _remove_cmm_adr_pairs(data, hidden_eval_pos_pairs)
    node_degrees_dict = _build_node_degrees_dict(data)

    arrays, pu_metadata = build_full_fold_pu_arrays(
        train_data=train_data,
        train_indices=train_sub,
        num_herbs=int(data["herb"].x.size(0)),
        num_adrs=int(data["adr"].x.size(0)),
        all_positive_pairs=all_positive_pairs,
        reliable_negative_weight=reliable_negative_weight,
        unlabeled_weight=unlabeled_weight,
        max_pairs=config.max_pairs,
        candidate_cache=candidate_cache,
        sampling_strategy=sampling_strategy,
        seed=seed + fold_idx,
        allowed_train_herbs=allowed_train_herbs,
    )

    data = data.to(device)
    train_edges = torch.from_numpy(
        np.stack([arrays["herb_idx"], arrays["adr_idx"]])
    ).long()
    train_labels = torch.as_tensor(arrays["label"], dtype=torch.float32)
    sample_weights = torch.as_tensor(arrays["sample_weight"], dtype=torch.float32)
    val_edges = (
        train_data["herb_indices"][val_sub],
        train_data["adr_indices"][val_sub],
    )
    val_labels = train_data["labels"][val_sub]

    model = MSATTCMFSFinal(
        node_types=list(data.node_types),
        edge_types=list(data.edge_types),
        in_channels_dict={ntype: data[ntype].x.size(1) for ntype in data.node_types},
        hidden_channels=ModelConfig.HIDDEN_CHANNELS,
        out_channels=ModelConfig.OUT_CHANNELS,
        num_layers=ModelConfig.NUM_LAYERS,
        num_heads=ModelConfig.NUM_HEADS,
        dropout=ModelConfig.DROPOUT,
        edge_attr_dim=ModelConfig.EDGE_ATTR_DIM,
        node_degrees_dict=node_degrees_dict,
        use_gated_edge_encoder=ModelConfig.USE_GATED_EDGE_ENCODER,
        use_bottleneck_transform=ModelConfig.USE_BOTTLENECK_TRANSFORM,
        use_late_fusion=ModelConfig.USE_LATE_FUSION,
    ).to(device)
    optimizer = AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode=TrainingConfig.SCHEDULER_MODE,
        factor=TrainingConfig.SCHEDULER_FACTOR,
        patience=TrainingConfig.SCHEDULER_PATIENCE,
    )

    train_start_time = time.time()
    best_val_auc = -1.0
    best_epoch = 0
    best_state = None
    patience = 0
    train_history = {"epochs": [], "train_loss": [], "val_auc": []}

    for epoch in range(max(1, int(config.max_epochs))):
        train_loss = train_one_epoch_weighted_probabilities(
            model,
            data,
            optimizer,
            train_edges,
            train_labels,
            sample_weights,
            device,
            gradient_clip=TrainingConfig.GRADIENT_CLIP,
        )
        if not np.isfinite(train_loss):
            break

        val_metrics, _ = evaluate(
            model,
            data,
            val_edges[0],
            val_edges[1],
            val_labels,
            device,
        )
        scheduler.step(val_metrics["auc"])

        train_history["epochs"].append(epoch + 1)
        train_history["train_loss"].append(float(train_loss))
        train_history["val_auc"].append(float(val_metrics["auc"]))

        if val_metrics["auc"] > best_val_auc:
            best_val_auc = float(val_metrics["auc"])
            best_epoch = epoch + 1
            patience = 0
            best_state = copy.deepcopy(model.state_dict())
        else:
            patience += 1
            if patience >= max(1, min(config.patience, int(config.max_epochs))):
                break

    train_time = time.time() - train_start_time
    checkpoint_path = None
    metadata_path = None
    if best_state is not None:
        model.load_state_dict(best_state)
        if config.save_checkpoints:
            checkpoint, metadata = _export_checkpoint(
                best_state=best_state,
                config=config,
                fold_idx=fold_idx,
                sampling_strategy=sampling_strategy,
                seed=seed,
                unlabeled_weight=unlabeled_weight,
                reliable_negative_weight=reliable_negative_weight,
                best_epoch=best_epoch,
                best_val_auc=best_val_auc,
            )
            checkpoint_path = str(checkpoint)
            metadata_path = str(metadata)

    _, val_probs = evaluate(
        model,
        data,
        val_edges[0],
        val_edges[1],
        val_labels,
        device,
        threshold=0.5,
    )
    optimal_threshold, val_f1_at_threshold = choose_threshold(
        val_probs,
        val_labels,
        strategy=config.threshold_strategy,
    )

    test_metrics, test_preds = evaluate(
        model,
        data,
        test_data["herb_indices"],
        test_data["adr_indices"],
        test_data["labels"],
        device,
        threshold=optimal_threshold,
    )

    return {
        "fold": fold_idx,
        "split_mode": config.split_mode,
        "cluster_protocol": cluster_protocol,
        "training_backend": config.training_backend,
        "best_epoch": best_epoch,
        "best_val_auc": float(best_val_auc),
        "optimal_threshold": float(optimal_threshold),
        "val_f1_at_threshold": val_f1_at_threshold,
        "threshold_strategy": config.threshold_strategy,
        "pu_pair_counts": pu_metadata,
        "test_metrics": test_metrics,
        "predictions": prediction_payload(
            test_data["labels"],
            test_preds,
            optimal_threshold,
        ),
        "training_history": train_history,
        "checkpoint_path": checkpoint_path,
        "metadata_path": metadata_path,
        "resource_usage": {
            "train_time_seconds": float(train_time),
            "total_time_seconds": float(time.time() - fold_start_time),
            "device": str(device),
        },
    }


def run_full_msat_pu_experiment(
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    max_folds: int,
    max_epochs: int,
    max_pairs: int,
    candidate_cache: str | Path,
    seed: int,
    threshold_strategy: str = "fixed_0_5",
    save_checkpoints: bool = False,
    checkpoint_prefix: str | None = None,
    checkpoint_dir: str | Path = Path("saved_models/pu_xmsat_formal"),
    allow_checkpoint_overwrite: bool = False,
    split_mode: str = "official_fold",
    n_clusters: int = 10,
    cluster_feature: str = "herb_x",
) -> dict:
    start = time.time()
    resolved_checkpoint_prefix = checkpoint_prefix or formal_checkpoint_prefix(
        backend="full_msat_pu",
        sampling_strategy=sampling_strategy,
        seed=seed,
        max_pairs=max_pairs,
        threshold_strategy=threshold_strategy,
        unlabeled_weight=unlabeled_weight,
        reliable_negative_weight=reliable_negative_weight,
    )
    config = FullMSATPUConfig(
        max_epochs=max_epochs,
        max_pairs=max_pairs,
        threshold_strategy=threshold_strategy,
        save_checkpoints=save_checkpoints,
        checkpoint_prefix=resolved_checkpoint_prefix,
        checkpoint_dir=Path(checkpoint_dir),
        allow_checkpoint_overwrite=allow_checkpoint_overwrite,
        split_mode=split_mode,
        n_clusters=int(n_clusters),
        cluster_feature=cluster_feature,
    )
    max_available_folds = int(n_clusters) if split_mode == "cluster_holdout" else DataConfig.N_FOLDS
    fold_count = min(max_available_folds, max(1, int(max_folds)))
    fold_results = [
        run_full_msat_pu_fold(
            fold_idx=fold_idx,
            config=config,
            sampling_strategy=sampling_strategy,
            unlabeled_weight=unlabeled_weight,
            reliable_negative_weight=reliable_negative_weight,
            candidate_cache=candidate_cache,
            seed=seed,
        )
        for fold_idx in range(fold_count)
    ]

    return {
        "status": "completed",
        "training_executed": True,
        "training_backend": config.training_backend,
        "split_mode": config.split_mode,
        "cluster_protocol": {
            "n_clusters": int(config.n_clusters),
            "cluster_feature": config.cluster_feature,
            "fold_count": int(fold_count),
            "claim_boundary": (
                "Cluster-held-out runs test held-out herb-cluster generalization, "
                "not external clinical validation or causal transportability."
            ),
        } if config.split_mode == "cluster_holdout" else {},
        "threshold_strategy": config.threshold_strategy,
        "fold_results": fold_results,
        "mean_metrics": summarize_full_fold_results(fold_results),
        "runtime_seconds": round(time.time() - start, 4),
        "checkpoint_export": {
            "save_checkpoints": bool(save_checkpoints),
            "checkpoint_dir": str(config.checkpoint_dir),
            "checkpoint_prefix": config.checkpoint_prefix,
            "allow_checkpoint_overwrite": bool(config.allow_checkpoint_overwrite),
            "checkpoint_naming_contract": (
                "filename includes backend, strategy, seed, pair budget, threshold "
                "strategy, unlabeled weight, reliable-negative weight, and fold index"
            ),
            "checkpoint_paths": [
                row.get("checkpoint_path")
                for row in fold_results
                if row.get("checkpoint_path")
            ],
            "checkpoint_metadata_paths": [
                row.get("metadata_path")
                for row in fold_results
                if row.get("metadata_path")
            ],
        },
        "protocol": protocol_metadata(),
        "note": (
            "Full MSAT PU backend trains MSATTCMFSFinal with PU sample weights. "
            "Pilot runs should be interpreted as implementation validation until "
            "multi-fold comparisons are completed."
        ),
    }
