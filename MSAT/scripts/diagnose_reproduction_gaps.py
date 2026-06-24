#!/usr/bin/env python3
"""Diagnose Fig.5a / Table 5 / unseen-CMM gaps vs paper expectations."""

from __future__ import annotations

import json
import re
import sys
import tarfile
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import matthews_corrcoef, precision_score, roc_auc_score

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

from baselines.common import positive_pair_set, remove_cmm_adr_pairs
from config import DataConfig
from experiments.feature_extractor import FeatureExtractor
from inference.coldstart import (
    eval_summary_coldstart,
    literature_holdout_mask,
    literature_pairs,
    train_herb_degree_for_fold,
)
from inference.artifact_manifest import file_manifest


def load_summary(name: str) -> dict:
    path = MSAT_ROOT / 'results' / name
    return json.loads(path.read_text())


def checkpoint_provenance(
    table5_summary_path: Path | None = None,
    local_checkpoint_path: Path | None = None,
) -> dict:
    summary_path = table5_summary_path or (MSAT_ROOT / 'results' / 'table5_summary.json')
    ckpt_path = local_checkpoint_path or (
        MSAT_ROOT / 'saved_models' / 'best_model_for_prediction.pt'
    )
    table5_summary = json.loads(summary_path.read_text(encoding='utf-8'))
    expected = table5_summary.get('checkpoint') or {}
    local = file_manifest(ckpt_path)
    expected_sha = expected.get('sha256')
    local_sha = local.get('sha256')
    matches = bool(expected_sha and local_sha and expected_sha == local_sha)
    warning = None
    if not local.get('exists'):
        warning = 'Local checkpoint is missing; Table 5 cannot be recomputed locally.'
    elif not matches:
        warning = (
            'Local checkpoint is not the checkpoint that generated Table 5; '
            'do not use it for Table 5 ranking diagnosis.'
        )
    return {
        'table5_summary': str(summary_path),
        'expected_checkpoint_path': expected.get('path'),
        'expected_checkpoint_sha256': expected_sha,
        'local_checkpoint_path': str(ckpt_path),
        'local_checkpoint_exists': bool(local.get('exists')),
        'local_checkpoint_sha256': local_sha,
        'local_checkpoint_matches_expected': matches,
        'warning': warning,
    }


def checkpoint_recovery_inventory(
    expected_sha256: str | None = None,
    model_dir: Path | None = None,
    result_bundle: Path | None = None,
) -> dict:
    table5_summary = load_summary('table5_summary.json')
    expected_sha = expected_sha256 or (table5_summary.get('checkpoint') or {}).get('sha256')
    models = model_dir or (MSAT_ROOT / 'saved_models')
    bundle = result_bundle or (
        MSAT_ROOT / 'server_results_2026-06-24' / 'phase9_results_bundle.tgz'
    )

    matching_paths = []
    scanned = []
    if models.is_dir() and expected_sha:
        for path in sorted(models.glob('*.pt')):
            manifest = file_manifest(path)
            scanned.append(
                {
                    'path': str(path),
                    'sha256': manifest.get('sha256'),
                    'size_bytes': manifest.get('size_bytes'),
                    'matches_expected': manifest.get('sha256') == expected_sha,
                }
            )
            if manifest.get('sha256') == expected_sha:
                matching_paths.append(str(path))

    bundle_contains_checkpoint = False
    bundle_error = None
    if bundle.is_file():
        try:
            with tarfile.open(bundle, 'r:*') as tf:
                names = tf.getnames()
            bundle_contains_checkpoint = any(
                name.endswith('.pt') or name.endswith('.pth') or name.endswith('.ckpt')
                for name in names
            )
        except tarfile.TarError as exc:
            bundle_error = f'{type(exc).__name__}: {exc}'
    else:
        bundle_error = 'bundle missing'

    return {
        'expected_checkpoint_sha256': expected_sha,
        'model_dir': str(models),
        'scanned_local_checkpoints': scanned,
        'matching_local_checkpoints': matching_paths,
        'result_bundle': str(bundle),
        'result_bundle_exists': bundle.is_file(),
        'result_bundle_contains_checkpoint': bundle_contains_checkpoint,
        'result_bundle_error': bundle_error,
        'can_restore_from_current_local_state': bool(
            matching_paths or bundle_contains_checkpoint
        ),
        'minimum_supplemental_materials': [
            f'Original predictor checkpoint with sha256 {expected_sha}',
            'Exact Table 5 export script/notebook used after model training',
            'Exact candidate-pool definition for "not included among labeled positives"',
            'TCMDA/literature evidence records for each accepted Top-15 row',
        ],
    }


def metrics_at_threshold(y_true, y_score, threshold: float) -> dict:
    y_pred = (y_score >= threshold).astype(int)
    return {
        'threshold': threshold,
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'mcc': float(matthews_corrcoef(y_true, y_pred)),
        'auc': float(roc_auc_score(y_true, y_score)),
    }


def sweep_thresholds(y_true, y_score) -> dict:
    best_f1 = {'f1': -1.0}
    best_mcc = {'mcc': -1.0}
    for t in np.linspace(0.05, 0.95, 19):
        m = metrics_at_threshold(y_true, y_score, float(t))
        pred = (y_score >= t).astype(int)
        f1 = 2 * m['precision'] * (pred & (y_true == 1)).sum() / max(
            (pred.sum() + (y_true == 1).sum()), 1
        )
        if f1 > best_f1.get('f1', -1):
            best_f1 = {**m, 'f1': float(f1)}
        if m['mcc'] > best_mcc.get('mcc', -1):
            best_mcc = m
    return {'best_mcc': best_mcc, 'at_0.5': metrics_at_threshold(y_true, y_score, 0.5)}


def pooled_coldstart_metrics(summary: dict, lit: set[tuple[int, int]]) -> dict:
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    y_all, s_all = [], []
    for fold_idx, fold in enumerate(summary['fold_results']):
        preds = fold['predictions']
        y_true = np.asarray(preds['y_true'])
        y_score = np.asarray(preds['y_score'])
        if 'herb_indices' in preds:
            test_h = np.asarray(preds['herb_indices'])
            test_a = np.asarray(preds['adr_indices'])
        else:
            _, test_data = extractor.load_fold_data(fold_idx)
            test_h = test_data['herb_indices']
            test_a = test_data['adr_indices']
        mask = literature_holdout_mask(y_true, test_h, test_a, lit)
        y_all.append(y_true[mask])
        s_all.append(y_score[mask])
    y = np.concatenate(y_all)
    s = np.concatenate(s_all)
    return sweep_thresholds(y, s)


def unseen_cmm_diagnostics() -> dict:
    lit = literature_pairs()
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
    )
    data_full = extractor.get_graph_data()

    rates = {
        'adr_edge_degree_zero': [],
        'any_herb_causes_degree_zero': [],
        'herb_not_in_train_fold_dev': [],
        'herb_not_in_train_pos_or_neg': [],
    }

    for fold_idx in range(10):
        train_data, test_data = extractor.load_fold_data(fold_idx)
        rng = np.random.RandomState(42 + fold_idx)
        n_dev = len(train_data['labels'])
        indices = rng.permutation(n_dev)
        n_val = int(n_dev * 0.1)
        val_sub = indices[:n_val]
        train_sub = indices[n_val:]

        test_pos = positive_pair_set(
            test_data['herb_indices'], test_data['adr_indices'], test_data['labels']
        )
        data = remove_cmm_adr_pairs(data_full.clone(), test_pos)
        pos_ei = data['herb', 'causes', 'adr'].edge_index
        herb_causes_deg = np.bincount(pos_ei[0].numpy(), minlength=data['herb'].x.size(0))

        train_herbs_dev = set(train_data['herb_indices'][train_sub].tolist())
        train_herbs_all = set(train_data['herb_indices'].tolist())

        lit_pos_in_test = []
        for i in range(len(test_data['labels'])):
            if test_data['labels'][i] != 1:
                continue
            pair = (int(test_data['herb_indices'][i]), int(test_data['adr_indices'][i]))
            if pair not in lit:
                continue
            lit_pos_in_test.append(int(test_data['herb_indices'][i]))

        if not lit_pos_in_test:
            continue

        h_arr = np.array(lit_pos_in_test)
        rates['adr_edge_degree_zero'].append(float((herb_causes_deg[h_arr] == 0).mean()))
        rates['herb_not_in_train_fold_dev'].append(float(np.mean([h not in train_herbs_dev for h in h_arr])))
        rates['herb_not_in_train_pos_or_neg'].append(float(np.mean([h not in train_herbs_all for h in h_arr])))

        # any-edge degree on train graph (all edge types ending at herb)
        any_deg = np.zeros(data['herb'].x.size(0))
        for et, ei in data.edge_index_dict.items():
            if et[2] == 'herb':
                any_deg += np.bincount(ei[1].numpy(), minlength=any_deg.size)
            if et[0] == 'herb':
                any_deg += np.bincount(ei[0].numpy(), minlength=any_deg.size)
        rates['any_herb_causes_degree_zero'].append(float((any_deg[h_arr] == 0).mean()))

    return {k: {'mean': float(np.mean(v)), 'values': v} for k, v in rates.items() if v}


def table5_diagnostics() -> dict:
    from scripts.run_table5_validation import (
        collect_oof_scores,
        faers_positive_pairs,
        graph_positive_pairs,
    )
    from scripts.run_table5_paper_compare import paper_herb_top1_rows
    from inference.entity_mapping import EntityNames

    summary_path = MSAT_ROOT / 'results' / 'summary.json'
    oof = collect_oof_scores(summary_path)
    faers = faers_positive_pairs()
    all_pos = graph_positive_pairs()
    lit = literature_pairs()

    def norm_name(text: str) -> str:
        return ' '.join(re.sub(r'[^a-z0-9]+', ' ', text.lower()).split())

    adr_by_name = {}
    names = EntityNames.load()
    for adr_id, rec in names.adrs.items():
        for value in (rec.meddra_pt, rec.primary):
            if value:
                adr_by_name.setdefault(norm_name(value), adr_id)

    paper_payload = json.loads(
        (MSAT_ROOT / 'data' / 'paper_table5_reference.json').read_text(encoding='utf-8')
    )
    mapped_pairs = []
    unmapped_adr_pts = []
    for ref in paper_payload.get('rows', []):
        herb_id = names.paper_herb_id(ref['latin'])
        adr_id = adr_by_name.get(norm_name(ref['adr_pt']))
        if herb_id is None or adr_id is None:
            if adr_id is None:
                unmapped_adr_pts.append(ref['adr_pt'])
            continue
        mapped_pairs.append((herb_id, adr_id))

    def top_k(excluded: set, k=15):
        cands = [(p, s) for p, s in oof.items() if p not in excluded]
        cands.sort(key=lambda x: x[1], reverse=True)
        return cands[:k]

    oof_top = top_k(all_pos)
    faers_top = top_k(faers)
    lit_in_top = sum(1 for p, _ in faers_top if p in lit)
    paper_seed_rows = paper_herb_top1_rows(names, oof, all_pos)
    paper_seed_supported = sum(
        1 for row in paper_seed_rows if row['database_verified'] or row['mechanistic_support']
    )
    paper_seed_adr_matches = sum(1 for row in paper_seed_rows if row['adr_match_paper'])
    return {
        'oof_exclude_all_positives': {
            'top1_score': oof_top[0][1] if oof_top else None,
            'lit_edges_in_top15': lit_in_top,
        },
        'oof_exclude_faers_only': {
            'top1_score': faers_top[0][1] if faers_top else None,
            'lit_edges_in_top15': lit_in_top,
            'n_lit_in_graph': len(lit),
        },
        'paper_seed_top1_oof': {
            'mode': 'paper_herb_top1_oof',
            'diagnostic_only': True,
            'is_table5_reproduction_claim': False,
            'reason': (
                'Uses the 15 paper Table 5 herbs as seeds, then picks each herb top-1 '
                'OOF ADR; it can reproduce paper support labels but not paper pairs.'
            ),
            'n_rows': len(paper_seed_rows),
            'adr_match_paper': paper_seed_adr_matches,
            'supported_count': paper_seed_supported,
            'support_rate': paper_seed_supported / len(paper_seed_rows)
            if paper_seed_rows
            else 0.0,
        },
        'paper_reference_pair_coverage': {
            'paper_rows': len(paper_payload.get('rows', [])),
            'mapped_pairs': len(mapped_pairs),
            'pairs_in_graph': sum(1 for pair in mapped_pairs if pair in all_pos),
            'pairs_in_faers': sum(1 for pair in mapped_pairs if pair in faers),
            'pairs_in_literature': sum(1 for pair in mapped_pairs if pair in lit),
            'pairs_in_oof_scores': sum(1 for pair in mapped_pairs if pair in oof),
            'unmapped_adr_pts': unmapped_adr_pts,
        },
        'n_faers_pairs': len(faers),
        'n_lit_pairs': len(lit),
        'n_all_pos': len(all_pos),
    }


def main() -> None:
    lit = literature_pairs()
    models = [
        ('MSAT', load_summary('summary.json')),
    ]
    cold = MSAT_ROOT / 'results' / 'coldstart_summary.json'
    if cold.exists():
        for row in json.loads(cold.read_text()).get('models', []):
            if row.get('model') == 'GAT':
                pass  # GAT not stored separately

    print('=' * 60)
    print('Fig.5a threshold sensitivity (pooled 10-fold literature hold-out)')
    print('=' * 60)
    for label, summary in [('MSAT', load_summary('summary.json'))]:
        sweep = pooled_coldstart_metrics(summary, lit)
        print(f'\n{label} @0.5: P={sweep["at_0.5"]["precision"]:.4f} MCC={sweep["at_0.5"]["mcc"]:.4f}')
        bm = sweep['best_mcc']
        print(f'{label} best-MCC @τ={bm["threshold"]:.2f}: P={bm["precision"]:.4f} MCC={bm["mcc"]:.4f}')

    if cold.exists():
        payload = json.loads(cold.read_text())
        for row in payload.get('models', []):
            if row.get('status') != 'ok':
                continue
            print(
                f'{row["model"]:12s} reported: P={row["precision"]["mean"]:.4f} '
                f'MCC={row["mcc"]["mean"]:.4f} AUC={row["auc"]["mean"]:.4f}'
            )

    print('\n' + '=' * 60)
    print('Unseen CMM rate definitions (literature positives in test fold)')
    print('=' * 60)
    unseen = unseen_cmm_diagnostics()
    for name, block in unseen.items():
        print(f'  {name:32s} mean={block["mean"]:.4f}')

    print('\n' + '=' * 60)
    print('Table 5 candidate pool diagnostics (OOF scores)')
    print('=' * 60)
    t5 = table5_diagnostics()
    print(json.dumps(t5, indent=2))

    out = MSAT_ROOT / 'results' / 'reproduction_gap_diagnosis.json'
    out.write_text(
        json.dumps(
            {
                'unseen_cmm': unseen,
                'table5': t5,
                'checkpoint_provenance': checkpoint_provenance(),
                'checkpoint_recovery_inventory': checkpoint_recovery_inventory(),
                'coldstart_reported': [
                    {k: row[k] for k in ('model', 'precision', 'mcc', 'auc') if k in row}
                    for row in json.loads(cold.read_text()).get('models', [])
                    if row.get('status') == 'ok'
                ]
                if cold.exists()
                else [],
            },
            indent=2,
        ),
        encoding='utf-8',
    )
    print(f'\n[SAVED] {out}')


if __name__ == '__main__':
    main()
