#!/usr/bin/env python3
"""Run the final PU-XMSAT checkpoint and mechanism-interpretability pipeline."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence


MSAT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8"
DEFAULT_RESULTS_DIR = Path("results")
DEFAULT_CHECKPOINT_DIR = Path("saved_models/pu_xmsat_formal")


@dataclass(frozen=True)
class PipelineStep:
    name: str
    argv: list[str]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the formal full-positive hybrid PU-XMSAT checkpoint export and "
            "checkpoint-aware mechanism interpretability pipeline."
        )
    )
    parser.add_argument("--python", dest="python_executable", default=sys.executable)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-folds", type=int, default=10)
    parser.add_argument("--max-epochs", type=int, default=200)
    parser.add_argument("--max-pairs", type=int, default=66015)
    parser.add_argument("--sampling-strategy", default="hybrid")
    parser.add_argument("--threshold-strategy", default="val_f1")
    parser.add_argument("--unlabeled-weight", type=float, default=0.2)
    parser.add_argument("--reliable-negative-weight", type=float, default=0.8)
    parser.add_argument(
        "--candidate-cache",
        default="results/pu_candidate_scores.random50k.jsonl",
    )
    parser.add_argument("--checkpoint-dir", default=str(DEFAULT_CHECKPOINT_DIR))
    parser.add_argument("--checkpoint-prefix", default=None)
    parser.add_argument("--prediction-fold", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--score-batch-size", type=int, default=2048)
    parser.add_argument("--max-cases", type=int, default=50)
    parser.add_argument("--max-features", type=int, default=0)
    parser.add_argument("--aggregate-top-k", type=int, default=10)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument(
        "--manifest",
        default="results/final_pu_xmsat_pipeline_manifest.json",
        help="JSON manifest path recording every command before execution.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the manifest and print commands without executing training.",
    )
    parser.add_argument(
        "--allow-nonfinal-config",
        action="store_true",
        help=(
            "Allow fold/epoch/pair/top-K settings below the formal final pipeline "
            "defaults. Do not use for manuscript final checkpoint export."
        ),
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.allow_nonfinal_config:
        return
    if int(args.max_folds) != 10:
        raise ValueError("final PU-XMSAT pipeline requires the full 10-fold configuration")
    if int(args.max_epochs) < 200:
        raise ValueError("final PU-XMSAT pipeline requires at least 200 epochs")
    if int(args.max_pairs) < 66015:
        raise ValueError("final PU-XMSAT pipeline requires pair budget >= 66015")
    if int(args.top_k) < 50:
        raise ValueError("final PU-XMSAT mechanism export requires top-K >= 50")
    if int(args.max_cases) < int(args.top_k):
        raise ValueError("contribution max-cases must cover the requested top-K candidates")


def _format_float_token(value: float) -> str:
    return str(float(value)).replace(".", "p").replace("-", "m")


def formal_checkpoint_prefix(args: argparse.Namespace) -> str:
    if args.checkpoint_prefix:
        return str(args.checkpoint_prefix)
    threshold = "valf1" if args.threshold_strategy == "val_f1" else str(args.threshold_strategy)
    return (
        f"pu_xmsat_full_msat_pu_{args.sampling_strategy}_"
        f"seed{int(args.seed)}_pairs{int(args.max_pairs)}_"
        f"{threshold}_u{_format_float_token(float(args.unlabeled_weight))}_"
        f"rn{_format_float_token(float(args.reliable_negative_weight))}"
    )


def _results_path(args: argparse.Namespace, filename: str) -> str:
    return str(Path(args.results_dir) / filename)


def final_checkpoint_path(args: argparse.Namespace) -> str:
    prefix = formal_checkpoint_prefix(args)
    return str(Path(args.checkpoint_dir) / f"{prefix}_fold{int(args.prediction_fold)}.pt")


def _training_output_path(args: argparse.Namespace) -> str:
    return _results_path(
        args,
        f"pu_xmsat_final_hybrid_seed{int(args.seed)}_checkpoint_export.json",
    )


def build_pipeline_commands(args: argparse.Namespace) -> list[PipelineStep]:
    prefix = formal_checkpoint_prefix(args)
    checkpoint_path = final_checkpoint_path(args)
    py = str(args.python_executable)
    results = {
        "top_json": _results_path(args, "pu_xmsat_top_predictions.json"),
        "top_csv": _results_path(args, "pu_xmsat_top_predictions.csv"),
        "top_md": _results_path(args, "PU_XMSAT_TOP_PREDICTIONS_EXPORT.md"),
        "contribution_json": _results_path(args, "contribution_quantification.json"),
        "contribution_csv": _results_path(args, "contribution_quantification.csv"),
        "contribution_md": _results_path(args, "PU_XMSAT_CONTRIBUTION_QUANTIFICATION.md"),
        "batch_json": _results_path(args, "batch_mechanism_interpretability.json"),
        "batch_csv": _results_path(args, "batch_mechanism_interpretability.csv"),
        "batch_md": _results_path(args, "PU_XMSAT_BATCH_MECHANISM_INTERPRETABILITY.md"),
        "aggregate_json": _results_path(args, "contribution_aggregate_summary.json"),
        "aggregate_csv": _results_path(args, "contribution_aggregate_summary.csv"),
        "aggregate_md": _results_path(args, "PU_XMSAT_CONTRIBUTION_AGGREGATE_SUMMARY.md"),
        "layer_json": _results_path(args, "mechanism_explanation_layer.json"),
        "layer_csv": _results_path(args, "mechanism_explanation_layer.csv"),
        "layer_md": _results_path(args, "PU_XMSAT_MECHANISM_EXPLANATION_LAYER.md"),
        "queue_json": _results_path(args, "direction3_targeted_review_queue.json"),
        "queue_csv": _results_path(args, "direction3_targeted_review_queue.csv"),
        "queue_md": _results_path(args, "PU_XMSAT_DIRECTION3_TARGETED_REVIEW_QUEUE.md"),
    }
    return [
        PipelineStep(
            "train_final_checkpoint",
            [
                py,
                "experiments/run_pu_msat_experiment.py",
                "--backend",
                "full_msat_pu",
                "--sampling-strategy",
                str(args.sampling_strategy),
                "--seed",
                str(int(args.seed)),
                "--max-folds",
                str(int(args.max_folds)),
                "--max-epochs",
                str(int(args.max_epochs)),
                "--max-pairs",
                str(int(args.max_pairs)),
                "--threshold-strategy",
                str(args.threshold_strategy),
                "--unlabeled-weight",
                str(float(args.unlabeled_weight)),
                "--reliable-negative-weight",
                str(float(args.reliable_negative_weight)),
                "--candidate-cache",
                str(args.candidate_cache),
                "--save-checkpoints",
                "--checkpoint-dir",
                str(args.checkpoint_dir),
                "--checkpoint-prefix",
                prefix,
                "--output",
                _training_output_path(args),
            ],
        ),
        PipelineStep(
            "export_top_predictions",
            [
                py,
                "scripts/export_pu_xmsat_top_predictions.py",
                "--checkpoint",
                checkpoint_path,
                "--checkpoint-is-final-pu-xmsat",
                "--top-k",
                str(int(args.top_k)),
                "--score-batch-size",
                str(int(args.score_batch_size)),
                "--device",
                str(args.device),
                "--output-json",
                results["top_json"],
                "--output-csv",
                results["top_csv"],
                "--output-md",
                results["top_md"],
            ],
        ),
        PipelineStep(
            "quantify_contributions",
            [
                py,
                "scripts/run_contribution_quantification.py",
                "--input",
                results["top_json"],
                "--checkpoint",
                checkpoint_path,
                "--checkpoint-is-final-pu",
                "--max-cases",
                str(int(args.max_cases)),
                "--max-features",
                str(int(args.max_features)),
                "--device",
                str(args.device),
                "--output-json",
                results["contribution_json"],
                "--output-csv",
                results["contribution_csv"],
                "--output-md",
                results["contribution_md"],
            ],
        ),
        PipelineStep(
            "run_batch_interpretability",
            [
                py,
                "scripts/run_batch_mechanism_interpretability.py",
                "--top-k",
                str(int(args.top_k)),
                "--final-predictions",
                results["top_json"],
                "--contribution",
                results["contribution_json"],
                "--checkpoint",
                checkpoint_path,
                "--checkpoint-is-final-pu",
                "--output-json",
                results["batch_json"],
                "--output-csv",
                results["batch_csv"],
                "--output-md",
                results["batch_md"],
            ],
        ),
        PipelineStep(
            "summarize_contributions",
            [
                py,
                "scripts/summarize_contribution_quantification.py",
                "--input",
                results["batch_json"],
                "--output-json",
                results["aggregate_json"],
                "--output-csv",
                results["aggregate_csv"],
                "--output-md",
                results["aggregate_md"],
                "--top-k",
                str(int(args.aggregate_top_k)),
            ],
        ),
        PipelineStep(
            "build_mechanism_explanation_layer",
            [
                py,
                "scripts/build_mechanism_explanation_layer.py",
                "--input",
                results["contribution_json"],
                "--output-json",
                results["layer_json"],
                "--output-csv",
                results["layer_csv"],
                "--output-md",
                results["layer_md"],
                "--top-k",
                str(int(args.aggregate_top_k)),
            ],
        ),
        PipelineStep(
            "build_direction3_review_queue",
            [
                py,
                "scripts/build_direction3_targeted_review_queue.py",
                "--contribution",
                results["batch_json"],
                "--output-json",
                results["queue_json"],
                "--output-csv",
                results["queue_csv"],
                "--output-md",
                results["queue_md"],
            ],
        ),
    ]


def _manifest_payload(args: argparse.Namespace, commands: Sequence[PipelineStep]) -> dict:
    return {
        "experiment": "final_pu_xmsat_interpretability_pipeline",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": bool(args.dry_run),
        "final_checkpoint_path": final_checkpoint_path(args),
        "training_output": _training_output_path(args),
        "config": {
            "backend": "full_msat_pu",
            "sampling_strategy": args.sampling_strategy,
            "seed": int(args.seed),
            "max_folds": int(args.max_folds),
            "max_epochs": int(args.max_epochs),
            "max_pairs": int(args.max_pairs),
            "threshold_strategy": args.threshold_strategy,
            "unlabeled_weight": float(args.unlabeled_weight),
            "reliable_negative_weight": float(args.reliable_negative_weight),
            "top_k": int(args.top_k),
            "max_cases": int(args.max_cases),
            "allow_nonfinal_config": bool(args.allow_nonfinal_config),
        },
        "commands": [
            {"name": step.name, "argv": step.argv}
            for step in commands
        ],
    }


def _write_manifest(path: str | Path, payload: dict) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(MSAT_ROOT) if not existing else f"{MSAT_ROOT}{os.pathsep}{existing}"
    return env


def run_pipeline(
    args: argparse.Namespace,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> dict:
    validate_args(args)
    commands = build_pipeline_commands(args)
    manifest = _manifest_payload(args, commands)
    _write_manifest(args.manifest, manifest)

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return manifest

    env = _subprocess_env()
    for step in commands:
        result = runner(step.argv, cwd=MSAT_ROOT, env=env)
        if result.returncode != 0:
            raise RuntimeError(f"{step.name} failed with exit code {result.returncode}")
    return manifest


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        run_pipeline(args)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
