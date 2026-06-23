"""Classical ML baselines: LR, RF, XGBoost."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from baselines.common import FoldSplit, compute_metrics, pair_features
from reproduction_protocol import protocol_metadata

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


def _predict_proba(model, X: np.ndarray) -> np.ndarray:
    if hasattr(model, 'predict_proba'):
        return model.predict_proba(X)[:, 1]
    return model.decision_function(X)


def train_eval_ml(model_name: str, fold: FoldSplit) -> Dict[str, float]:
    X_train = pair_features(
        fold.herb_x, fold.adr_x, fold.train_h, fold.train_a, fold.edge_attr_map
    )
    X_test = pair_features(
        fold.herb_x, fold.adr_x, fold.test_h, fold.test_a, fold.edge_attr_map
    )

    if model_name == 'lr':
        model = LogisticRegression(max_iter=2000, random_state=42, n_jobs=-1)
    elif model_name == 'rf':
        model = RandomForestClassifier(
            n_estimators=200, random_state=42, n_jobs=-1, class_weight='balanced_subsample'
        )
    elif model_name == 'xgb':
        if not HAS_XGB:
            raise ImportError('xgboost not installed')
        model = XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss',
        )
    else:
        raise ValueError(f'Unknown ML model: {model_name}')

    model.fit(X_train, fold.train_y)
    scores = _predict_proba(model, X_test)
    return compute_metrics(fold.test_y, scores)


def run_ml_cv(model_name: str, n_folds: int = 10) -> Dict:
    from baselines.common import aggregate_fold_metrics, prepare_fold

    fold_metrics: List[Dict[str, float]] = []
    for fold_idx in range(n_folds):
        print(f'  [{model_name}] fold {fold_idx + 1}/{n_folds}')
        fold = prepare_fold(fold_idx)
        metrics = train_eval_ml(model_name, fold)
        fold_metrics.append(metrics)
        print(f"    AUC={metrics['auc']:.4f} F1={metrics['f1']:.4f}")

    return {
        'model': model_name,
        'protocol': protocol_metadata(),
        'feature_config': {
            'pair_features': 'concat(herb_x, adr_x)',
            'include_cmm_adr_edge_attr': False,
            'leakage_note': (
                'CMM-ADR edge_attr is excluded because its presence directly '
                'identifies known positive CMM-ADR edges in sampled pairs.'
            ),
        },
        'fold_metrics': fold_metrics,
        'overall_metrics': aggregate_fold_metrics(fold_metrics),
    }
