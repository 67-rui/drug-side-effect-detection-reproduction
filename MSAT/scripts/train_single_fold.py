#!/usr/bin/env python3
"""Run a single CV fold for smoke testing."""

import sys
from pathlib import Path

import torch

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from train import train_single_fold


def main() -> None:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')
    result = train_single_fold(fold_idx=0, device=device)
    m = result['test_metrics']
    print(f"Fold 0 — AUC={m['auc']:.4f}  AUPRC={m['auprc']:.4f}  F1={m['f1']:.4f}  MCC={m['mcc']:.4f}")


if __name__ == '__main__':
    main()
