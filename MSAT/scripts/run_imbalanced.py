#!/usr/bin/env python3
"""Run MSAT 1:10 imbalanced experiment (Table 4, Phase 6 Task 6.1)."""

from __future__ import annotations

import sys
from pathlib import Path

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from config import DataConfig, TrainingConfig
import train


def main() -> None:
    DataConfig.NEG_RATIO = 10
    DataConfig.TEST_NEG_RATIO = 10
    TrainingConfig.USE_OPTIMAL_THRESHOLD = True

    print('=' * 80)
    print('Phase 6 Task 6.1: 1:10 imbalanced experiment (Table 4)')
    print(f'  neg_ratio={DataConfig.NEG_RATIO}:1')
    print(f'  test_neg_ratio={DataConfig.TEST_NEG_RATIO}:1')
    print(f'  use_optimal_threshold={TrainingConfig.USE_OPTIMAL_THRESHOLD}')
    print('  Expected MSAT AUC ~ 0.875 ± 0.005')
    print('=' * 80)

    train.run_10fold_cv(experiment_tag='neg10')


if __name__ == '__main__':
    main()
