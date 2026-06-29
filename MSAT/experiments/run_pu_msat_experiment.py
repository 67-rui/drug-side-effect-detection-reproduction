from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np
import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig
from experiments.feature_extractor import FeatureExtractor
from experiments.pu_data_utils import build_unobserved_pairs, read_jsonl
from experiments.pu_dataset_builder import build_pu_training_arrays
from experiments.pu_loss import weighted_pu_bce_loss
from experiments.reliable_negative_sampling import CandidateScore, select_reliable_negatives


SUPPORTED_TRAINING_BACKENDS = {"weighted_embedding_smoke", "full_msat_pu"}


def resolve_training_backend(training_backend: str) -> str:
    if training_backend not in SUPPORTED_TRAINING_BACKENDS:
        supported = ", ".join(sorted(SUPPORTED_TRAINING_BACKENDS))
        raise ValueError(f"unknown backend: {training_backend}. Supported: {supported}")
    return training_backend


def build_experiment_config(
    sampling_strategy: str,
    unlabeled_weight: float,
    reliable_negative_weight: float,
    max_folds: int,
    max_epochs: int,
    training_backend: str = "weighted_embedding_smoke",
    threshold_strategy: str = "fixed_0_5",
    save_checkpoints: bool = False,
    checkpoint_prefix: str | None = None,
    checkpoint_dir: str = "saved_models/pu_xmsat_formal",
    allow_checkpoint_overwrite: bool = False,
    split_mode: str = "official_fold",
    n_clusters: int = 10,
    cluster_feature: str = "herb_x",
) -> dict:
    backend = resolve_training_backend(training_backend)
    return {
        "experiment": "pu_xmsat",
        "sampling_strategy": sampling_strategy,
        "threshold_strategy": threshold_strategy,
        "save_checkpoints": bool(save_checkpoints),
        "checkpoint_prefix": checkpoint_prefix,
        "checkpoint_dir": checkpoint_dir,
        "allow_checkpoint_overwrite": bool(allow_checkpoint_overwrite),
        "split_mode": split_mode,
        "n_clusters": int(n_clusters),
        "cluster_feature": cluster_feature,
        "loss": "weighted_pu_bce",
        "training_backend": backend,
        "unlabeled_weight": unlabeled_weight,
        "reliable_negative_weight": reliable_negative_weight,
        "max_folds": max_folds,
        "max_epochs": max_epochs,
        "baseline": "baseline/msat-reproduction-20260626",
    }


class PairEmbeddingSmokeModel(torch.nn.Module):
    def __init__(self, num_herbs: int, num_adrs: int, embedding_dim: int):
        super().__init__()
        self.herb_embedding = torch.nn.Embedding(num_herbs, embedding_dim)
        self.adr_embedding = torch.nn.Embedding(num_adrs, embedding_dim)
        self.bias = torch.nn.Parameter(torch.zeros(1))

    def forward(self, herb_idx: torch.Tensor, adr_idx: torch.Tensor) -> torch.Tensor:
        herb_vec = self.herb_embedding(herb_idx)
        adr_vec = self.adr_embedding(adr_idx)
        return (herb_vec * adr_vec).sum(dim=1) + self.bias


def run_weighted_pu_smoke_training(
    arrays: dict[str, np.ndarray],
    num_herbs: int,
    num_adrs: int,
    max_epochs: int,
    seed: int = 42,
    embedding_dim: int = 8,
    learning_rate: float = 0.05,
) -> dict:
    torch.manual_seed(seed)
    model = PairEmbeddingSmokeModel(
        num_herbs=num_herbs,
        num_adrs=num_adrs,
        embedding_dim=embedding_dim,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    herb_idx = torch.as_tensor(arrays["herb_idx"], dtype=torch.long)
    adr_idx = torch.as_tensor(arrays["adr_idx"], dtype=torch.long)
    labels = torch.as_tensor(arrays["label"], dtype=torch.float32)
    weights = torch.as_tensor(arrays["sample_weight"], dtype=torch.float32)

    loss_history: list[float] = []
    for _ in range(max_epochs):
        optimizer.zero_grad()
        logits = model(herb_idx, adr_idx)
        loss = weighted_pu_bce_loss(logits, labels, weights)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        loss_history.append(float(loss.item()))

    return {
        "training_executed": True,
        "backend": "weighted_embedding_smoke",
        "pair_count": int(len(labels)),
        "positive_count": int(labels.sum().item()),
        "loss_history": loss_history,
        "initial_loss": loss_history[0] if loss_history else None,
        "final_loss": loss_history[-1] if loss_history else None,
    }


def _positive_pairs_from_train_data(train_data: dict, limit: int) -> list[tuple[int, int]]:
    positives = [
        (int(h), int(a))
        for h, a, label in zip(
            train_data["herb_indices"],
            train_data["adr_indices"],
            train_data["labels"],
        )
        if int(label) == 1
    ]
    return positives[:limit]


def _candidate_scores_from_cache(path: Path) -> list[CandidateScore]:
    if not path.exists():
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


def build_fold_smoke_arrays(
    fold_idx: int,
    reliable_negative_weight: float,
    unlabeled_weight: float,
    max_pairs: int,
    candidate_cache: str | Path,
) -> tuple[dict[str, np.ndarray], dict]:
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
        n_folds=DataConfig.N_FOLDS,
        neg_ratio=DataConfig.NEG_RATIO,
        test_neg_ratio=DataConfig.TEST_NEG_RATIO,
        random_seed=DataConfig.RANDOM_SEED,
    )
    data = extractor.get_graph_data()
    train_data, _ = extractor.load_fold_data(fold_idx)
    num_herbs = int(data["herb"].x.size(0))
    num_adrs = int(data["adr"].x.size(0))

    per_type = max(1, max_pairs // 3)
    positive_pairs = _positive_pairs_from_train_data(train_data, limit=per_type)
    positive_set = set(positive_pairs)

    candidate_scores = _candidate_scores_from_cache(Path(candidate_cache))
    if candidate_scores:
        reliable_negatives = select_reliable_negatives(
            candidate_scores,
            count=per_type,
            seed=DataConfig.RANDOM_SEED,
        )
        unlabeled_pairs = [
            (row.herb_id, row.adr_id)
            for row in candidate_scores
            if (row.herb_id, row.adr_id) not in positive_set
        ][per_type : per_type * 2]
    else:
        unobserved = build_unobserved_pairs(num_herbs, num_adrs, positive_set)
        reliable_negatives = [
            CandidateScore(herb_id=h, adr_id=a, reliability_score=0.0)
            for h, a in unobserved[:per_type]
        ]
        unlabeled_pairs = unobserved[per_type : per_type * 2]

    reliable_pair_set = {(row.herb_id, row.adr_id) for row in reliable_negatives}
    unlabeled_pairs = [
        pair
        for pair in unlabeled_pairs
        if pair not in positive_set and pair not in reliable_pair_set
    ][:per_type]

    arrays = build_pu_training_arrays(
        positive_pairs=positive_pairs,
        reliable_negatives=reliable_negatives,
        unlabeled_pairs=unlabeled_pairs,
        unlabeled_weight=unlabeled_weight,
        reliable_negative_weight=reliable_negative_weight,
    )
    metadata = {
        "fold_idx": fold_idx,
        "num_herbs": num_herbs,
        "num_adrs": num_adrs,
        "positive_pairs": len(positive_pairs),
        "reliable_negative_pairs": len(reliable_negatives),
        "unlabeled_pairs": len(unlabeled_pairs),
    }
    return arrays, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=sorted(SUPPORTED_TRAINING_BACKENDS),
        default="weighted_embedding_smoke",
    )
    parser.add_argument("--sampling-strategy", default="hybrid")
    parser.add_argument(
        "--threshold-strategy",
        choices=["fixed_0_5", "val_f1"],
        default="fixed_0_5",
    )
    parser.add_argument("--unlabeled-weight", type=float, default=0.2)
    parser.add_argument("--reliable-negative-weight", type=float, default=0.8)
    parser.add_argument("--max-folds", type=int, default=1)
    parser.add_argument("--max-epochs", type=int, default=2)
    parser.add_argument("--output", default="results/pu_training_smoke_summary.json")
    parser.add_argument("--candidate-cache", default="results/pu_candidate_scores.sample.jsonl")
    parser.add_argument("--max-pairs", type=int, default=384)
    parser.add_argument("--embedding-dim", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--split-mode",
        choices=["official_fold", "cluster_holdout"],
        default="official_fold",
        help="Evaluation split protocol for the full_msat_pu backend.",
    )
    parser.add_argument("--n-clusters", type=int, default=10)
    parser.add_argument(
        "--cluster-feature",
        choices=["herb_x"],
        default="herb_x",
        help="Label-free herb feature source for cluster_holdout.",
    )
    parser.add_argument(
        "--save-checkpoints",
        action="store_true",
        help="Export best full_msat_pu fold checkpoints with formal non-baseline names.",
    )
    parser.add_argument(
        "--checkpoint-prefix",
        default=None,
        help=(
            "Optional checkpoint prefix. If omitted for full_msat_pu, a formal prefix "
            "including backend, strategy, seed, pair budget, threshold strategy, and PU "
            "weights is generated."
        ),
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="saved_models/pu_xmsat_formal",
        help="Checkpoint directory used only when --save-checkpoints is set.",
    )
    parser.add_argument(
        "--overwrite-checkpoints",
        action="store_true",
        help=(
            "Allow overwriting an existing formal PU-XMSAT checkpoint. Default is "
            "to refuse overwrites so manuscript checkpoints are not polluted."
        ),
    )
    args = parser.parse_args()

    start = time.time()
    backend = resolve_training_backend(args.backend)
    payload = build_experiment_config(
        sampling_strategy=args.sampling_strategy,
        unlabeled_weight=args.unlabeled_weight,
        reliable_negative_weight=args.reliable_negative_weight,
        max_folds=args.max_folds,
        max_epochs=args.max_epochs,
        training_backend=backend,
        threshold_strategy=args.threshold_strategy,
        save_checkpoints=args.save_checkpoints,
        checkpoint_prefix=args.checkpoint_prefix,
        checkpoint_dir=args.checkpoint_dir,
        allow_checkpoint_overwrite=args.overwrite_checkpoints,
        split_mode=args.split_mode,
        n_clusters=args.n_clusters,
        cluster_feature=args.cluster_feature,
    )

    if backend == "full_msat_pu":
        from experiments.full_msat_pu_training import run_full_msat_pu_experiment

        payload.update(
            run_full_msat_pu_experiment(
                sampling_strategy=args.sampling_strategy,
                unlabeled_weight=args.unlabeled_weight,
                reliable_negative_weight=args.reliable_negative_weight,
                max_folds=args.max_folds,
                max_epochs=args.max_epochs,
                max_pairs=args.max_pairs,
                candidate_cache=args.candidate_cache,
                seed=args.seed,
                threshold_strategy=args.threshold_strategy,
                save_checkpoints=args.save_checkpoints,
                checkpoint_prefix=args.checkpoint_prefix,
                checkpoint_dir=args.checkpoint_dir,
                allow_checkpoint_overwrite=args.overwrite_checkpoints,
                split_mode=args.split_mode,
                n_clusters=args.n_clusters,
                cluster_feature=args.cluster_feature,
            )
        )
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"Wrote {out}")
        return

    fold_results = []
    for fold_idx in range(max(1, args.max_folds)):
        arrays, fold_metadata = build_fold_smoke_arrays(
            fold_idx=fold_idx,
            reliable_negative_weight=args.reliable_negative_weight,
            unlabeled_weight=args.unlabeled_weight,
            max_pairs=args.max_pairs,
            candidate_cache=args.candidate_cache,
        )
        train_result = run_weighted_pu_smoke_training(
            arrays,
            num_herbs=fold_metadata["num_herbs"],
            num_adrs=fold_metadata["num_adrs"],
            max_epochs=args.max_epochs,
            seed=args.seed + fold_idx,
            embedding_dim=args.embedding_dim,
            learning_rate=args.learning_rate,
        )
        fold_results.append({**fold_metadata, **train_result})

    final_losses = [
        row["final_loss"]
        for row in fold_results
        if row.get("final_loss") is not None
    ]
    payload.update(
        {
            "status": "completed",
            "training_executed": True,
            "fold_results": fold_results,
            "mean_metrics": {
                "final_loss": float(np.mean(final_losses)) if final_losses else None,
            },
            "runtime_seconds": round(time.time() - start, 4),
            "note": (
                "Weighted PU smoke uses a lightweight pair-embedding scorer to "
                "verify data construction, sample weights, and loss stability. "
                "It is not a full MSAT GNN training result."
            ),
        }
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
