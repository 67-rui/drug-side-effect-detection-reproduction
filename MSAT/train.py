
import os
import sys
import json
import time
import copy
from pathlib import Path
from datetime import datetime

import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, matthews_corrcoef
)
from scipy import stats
from scipy.stats import spearmanr

import psutil
try:
    import GPUtil
except:
    GPUtil = None

MSAT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(MSAT_ROOT))
from experiments.feature_extractor import FeatureExtractor
from model import MSATTCMFSFinal
from config import ModelConfig, TrainingConfig, DataConfig
from reproduction_protocol import protocol_metadata


def _positive_pair_set(herb_indices, adr_indices, labels):
    mask = labels == 1
    return {
        (int(h), int(a))
        for h, a in zip(herb_indices[mask], adr_indices[mask])
    }


def _evaluation_positive_pair_set(val_h, val_a, val_y, test_h, test_a, test_y):
    """Positive CMM-ADR pairs hidden from the message-passing graph for eval."""
    return (
        _positive_pair_set(val_h, val_a, val_y)
        | _positive_pair_set(test_h, test_a, test_y)
    )


def _remove_cmm_adr_pairs(data, pairs_to_remove):
    pair_set = set(pairs_to_remove)
    for edge_index_key in [
        ('herb', 'causes', 'adr'),
        ('adr', 'rev_causes', 'herb'),
    ]:
        edge_index = data[edge_index_key].edge_index
        keep = []
        for i in range(edge_index.size(1)):
            if edge_index_key[0] == 'herb':
                pair = (int(edge_index[0, i]), int(edge_index[1, i]))
            else:
                pair = (int(edge_index[1, i]), int(edge_index[0, i]))
            keep.append(pair not in pair_set)

        keep_mask = torch.tensor(keep)
        data[edge_index_key].edge_index = edge_index[:, keep_mask]
        if hasattr(data[edge_index_key], 'edge_attr') and data[edge_index_key].edge_attr is not None:
            data[edge_index_key].edge_attr = data[edge_index_key].edge_attr[keep_mask]
    return data


def _safe_experiment_tag(experiment_tag='') -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in str(experiment_tag))


def prediction_checkpoint_path(experiment_tag='') -> Path:
    if not experiment_tag:
        return Path('saved_models/best_model_for_prediction.pt')
    return Path(f'saved_models/best_model_for_prediction_{_safe_experiment_tag(experiment_tag)}.pt')


def fold_checkpoint_path(fold_idx, experiment_tag='') -> Path:
    if not experiment_tag:
        return Path(f'saved_models/best_model_fold{fold_idx}.pt')
    return Path(f'saved_models/best_model_fold{fold_idx}_{_safe_experiment_tag(experiment_tag)}.pt')


def model_selection_score(fold_result):
    return float(fold_result['best_val_auc'])


def _state_dict_to_cpu(state_dict):
    return {
        key: value.detach().cpu().clone() if torch.is_tensor(value) else copy.deepcopy(value)
        for key, value in state_dict.items()
    }


def train_one_epoch(model, data, optimizer, train_edges, train_labels, device):
    model.train()
    optimizer.zero_grad()
    
    out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict,
                train_edges[0].to(device), train_edges[1].to(device))
    
    if torch.isnan(out).any():
        return float('nan')
    
    loss = F.binary_cross_entropy(out, train_labels.to(device))
    
    if torch.isnan(loss):
        return float('nan')
    
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), TrainingConfig.GRADIENT_CLIP)
    optimizer.step()
    
    return loss.item()


def find_optimal_threshold(probs, labels):
    best_threshold, best_f1 = 0.5, -1.0
    for threshold in np.linspace(0.01, 0.99, 99):
        pred_labels = (probs >= threshold).astype(int)
        score = f1_score(labels, pred_labels, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best_threshold = float(threshold)
    return best_threshold, best_f1


def evaluate(model, data, herb_indices, adr_indices, labels, device, threshold=0.5):
    model.eval()
    
    with torch.no_grad():
        out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict,
                   torch.LongTensor(herb_indices).to(device),
                   torch.LongTensor(adr_indices).to(device))
        
        pred_probs = torch.nan_to_num(out, nan=0.5).cpu().numpy()
        pred_labels = (pred_probs >= threshold).astype(int)
    
    return {
        'precision': float(precision_score(labels, pred_labels, zero_division=0)),
        'recall': float(recall_score(labels, pred_labels, zero_division=0)),
        'f1': float(f1_score(labels, pred_labels, zero_division=0)),
        'auc': float(roc_auc_score(labels, pred_probs)),
        'auprc': float(average_precision_score(labels, pred_probs)),
        'mcc': float(matthews_corrcoef(labels, pred_labels)),
        'threshold': float(threshold),
    }, pred_probs


def prediction_payload(labels, scores, threshold):
    scores = np.asarray(scores)
    return {
        'y_true': np.asarray(labels).tolist(),
        'y_score': scores.tolist(),
        'y_pred': (scores >= threshold).astype(int).tolist(),
    }


def train_single_fold(fold_idx, device, experiment_tag=''):
    print(f"\n{'='*80}")
    print(f"Fold {fold_idx + 1}/{TrainingConfig.N_FOLDS}")
    print(f"{'='*80}")
    
    fold_start_time = time.time()
    
   
    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=0.1)
    mem_before = process.memory_info().rss / 1024 / 1024
    
    gpu_mem_before = 0
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_mem_before = gpus[0].memoryUsed
        except:
            pass
    
   
    extractor = FeatureExtractor(
        data_dir=DataConfig.DATA_DIR,
        fold_split_path=DataConfig.FOLD_SPLIT_PATH,
        n_folds=DataConfig.N_FOLDS,
        neg_ratio=DataConfig.NEG_RATIO,
        test_neg_ratio=DataConfig.TEST_NEG_RATIO,
        random_seed=DataConfig.RANDOM_SEED,
    )
    data = extractor.get_graph_data()
    train_data, test_data = extractor.load_fold_data(fold_idx)
    
    print(f"  Train samples: {len(train_data['labels'])}")
    print(f"  Test samples:  {len(test_data['labels'])}")
    n_train_pos = int((train_data['labels'] == 1).sum())
    n_test_pos = int((test_data['labels'] == 1).sum())
    print(f"  Neg ratio: {DataConfig.NEG_RATIO}:1  (dev pos={n_train_pos}, test pos={n_test_pos})")
    
    rng = np.random.RandomState(TrainingConfig.RANDOM_STATE + fold_idx)
    n_dev = len(train_data['labels'])
    indices = rng.permutation(n_dev)
    n_val = int(n_dev * (1 - TrainingConfig.TRAIN_VAL_SPLIT))
    
    val_sub = indices[:n_val]
    train_sub = indices[n_val:]
    
    hidden_eval_pos_pairs = _evaluation_positive_pair_set(
        train_data['herb_indices'][val_sub],
        train_data['adr_indices'][val_sub],
        train_data['labels'][val_sub],
        test_data['herb_indices'],
        test_data['adr_indices'],
        test_data['labels'],
    )
    data = _remove_cmm_adr_pairs(data, hidden_eval_pos_pairs)
    print(
        f"  Excluded {len(hidden_eval_pos_pairs)} validation/test positive edges "
        "(paper §3.5.1 inductive)"
    )
    
   
    node_degrees_dict = {}
    for ntype in data.node_types:
        degree = torch.zeros(data[ntype].x.size(0))
        for edge_type, edge_index in data.edge_index_dict.items():
            if edge_type[2] == ntype:
                degree += torch.bincount(edge_index[1], minlength=data[ntype].x.size(0)).float()
        node_degrees_dict[ntype] = degree
    
    data = data.to(device)
    
  
    train_edges = torch.from_numpy(np.stack([
        train_data['herb_indices'][train_sub],
        train_data['adr_indices'][train_sub],
    ])).long()
    val_edges = (
        train_data['herb_indices'][val_sub],
        train_data['adr_indices'][val_sub],
    )
    train_labels = torch.FloatTensor(train_data['labels'][train_sub])
    val_labels = train_data['labels'][val_sub]
    
    print(f"  Train/Val split: {len(train_labels)}/{len(val_labels)}")
    
   
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
    
    print(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
   
    optimizer = AdamW(
        model.parameters(),
        lr=TrainingConfig.LEARNING_RATE,
        weight_decay=TrainingConfig.WEIGHT_DECAY
    )
    
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode=TrainingConfig.SCHEDULER_MODE,
        factor=TrainingConfig.SCHEDULER_FACTOR,
        patience=TrainingConfig.SCHEDULER_PATIENCE
    )
    
   
    train_start_time = time.time()
    best_val_auc = 0
    best_epoch = 0
    patience = 0
    best_state = None
    train_history = {'epochs': [], 'train_loss': [], 'val_auc': []}
    
    for epoch in range(TrainingConfig.NUM_EPOCHS):
        train_loss = train_one_epoch(model, data, optimizer, train_edges, train_labels, device)
        
        if np.isnan(train_loss):
            print(f"  ERROR: NaN loss at epoch {epoch+1}")
            break
        
        val_metrics, _ = evaluate(model, data, val_edges[0], val_edges[1], val_labels, device)
        scheduler.step(val_metrics['auc'])
        
        train_history['epochs'].append(epoch + 1)
        train_history['train_loss'].append(train_loss)
        train_history['val_auc'].append(val_metrics['auc'])
        
        if val_metrics['auc'] > best_val_auc:
            best_val_auc = val_metrics['auc']
            best_epoch = epoch + 1
            patience = 0
            best_state = copy.deepcopy(model.state_dict())
            
            if (epoch + 1) % 50 == 0:
                print(f"  Epoch {epoch+1}: val_auc={val_metrics['auc']:.4f} *")
        else:
            patience += 1
            if patience >= TrainingConfig.PATIENCE:
                print(f"  Early stopping at epoch {epoch+1}")
                break
    
    train_time = time.time() - train_start_time
    
    
    best_state_cpu = None
    if best_state:
        model.load_state_dict(best_state)
        best_state_cpu = _state_dict_to_cpu(best_state)
        
        
        if TrainingConfig.SAVE_FOLD_CHECKPOINTS:
            (MSAT_ROOT / 'saved_models').mkdir(parents=True, exist_ok=True)
            torch.save(best_state_cpu, MSAT_ROOT / fold_checkpoint_path(fold_idx, experiment_tag))
    
   
    cpu_after = process.cpu_percent(interval=0.1)
    mem_after = process.memory_info().rss / 1024 / 1024
    
    gpu_mem_after = 0
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_mem_after = gpus[0].memoryUsed
        except:
            pass
    
   
    optimal_threshold = 0.5
    val_f1_at_threshold = None
    if TrainingConfig.USE_OPTIMAL_THRESHOLD:
        _, val_probs = evaluate(
            model, data, val_edges[0], val_edges[1], val_labels, device, threshold=0.5
        )
        optimal_threshold, val_f1_at_threshold = find_optimal_threshold(val_probs, val_labels)
        print(f"  Optimal threshold (val F1): tau*={optimal_threshold:.3f}, val_f1={val_f1_at_threshold:.4f}")

    test_metrics, test_preds = evaluate(
        model, data, test_data['herb_indices'],
        test_data['adr_indices'], test_data['labels'], device,
        threshold=optimal_threshold,
    )
    
    fold_time = time.time() - fold_start_time
    
    print(f"\n  Fold {fold_idx+1} Results:")
    print(f"    Precision: {test_metrics['precision']:.4f}")
    print(f"    Recall:    {test_metrics['recall']:.4f}")
    print(f"    F1:        {test_metrics['f1']:.4f}")
    print(f"    AUC:       {test_metrics['auc']:.4f}")
    print(f"    AUPR:      {test_metrics['auprc']:.4f}")
    print(f"    MCC:       {test_metrics['mcc']:.4f}")
    print(f"    Time:      {fold_time:.1f}s")
    
    return {
        '_best_state': best_state_cpu,
        'fold': fold_idx,
        'best_epoch': best_epoch,
        'best_val_auc': best_val_auc,
        'optimal_threshold': optimal_threshold,
        'val_f1_at_threshold': val_f1_at_threshold,
        'test_metrics': test_metrics,
        'predictions': prediction_payload(test_data['labels'], test_preds, optimal_threshold),
        'training_history': train_history,
        'resource_usage': {
            'train_time_seconds': train_time,
            'total_time_seconds': fold_time,
            'cpu_percent_avg': (cpu_before + cpu_after) / 2,
            'memory_mb_peak': mem_after,
            'gpu_memory_mb_before': gpu_mem_before,
            'gpu_memory_mb_after': gpu_mem_after
        }
    }


def run_10fold_cv(experiment_tag=''):
    
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    print(f"Data: {DataConfig.DATA_DIR}")
    if experiment_tag:
        print(f"Experiment: {experiment_tag}")
    print(f"Neg ratio: {DataConfig.NEG_RATIO}:1")
    if TrainingConfig.USE_OPTIMAL_THRESHOLD:
        print("Threshold: optimal tau* from validation F1")
    print(f"Ablation: ESA={ModelConfig.USE_GATED_EDGE_ENCODER}, "
          f"HSP={ModelConfig.USE_BOTTLENECK_TRANSFORM}, "
          f"HCI={ModelConfig.USE_LATE_FUSION}\n")
    
    experiment_start = time.time()
    results = []
    best_overall_score = -1
    best_overall_fold = -1
    best_overall_state = None
    
    for fold in range(TrainingConfig.N_FOLDS):
        fold_result = train_single_fold(fold, device, experiment_tag=experiment_tag)
        fold_state = fold_result.pop('_best_state', None)
        results.append(fold_result)
        
        selection_score = model_selection_score(fold_result)
        if selection_score > best_overall_score:
            best_overall_score = selection_score
            best_overall_fold = fold
           
            if fold_state is not None:
                best_overall_state = fold_state
            elif TrainingConfig.SAVE_FOLD_CHECKPOINTS:
                state_path = MSAT_ROOT / fold_checkpoint_path(fold, experiment_tag)
                if os.path.exists(state_path):
                    best_overall_state = torch.load(state_path, map_location='cpu')
    
    total_experiment_time = time.time() - experiment_start
    
   
    print(f"\n{'='*80}")
    print("Overall Results (10-Fold CV)")
    print("="*80)
    
    overall_metrics = {}
    for metric in ['precision', 'recall', 'f1', 'auc', 'auprc', 'mcc']:
        values = [r['test_metrics'][metric] for r in results]
        overall_metrics[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'values': values
        }
        print(f"  {metric.upper():12s}: {overall_metrics[metric]['mean']:.4f} ± {overall_metrics[metric]['std']:.4f}")
    
    
    avg_train_time = np.mean([r['resource_usage']['train_time_seconds'] for r in results])
    avg_total_time = np.mean([r['resource_usage']['total_time_seconds'] for r in results])
    avg_cpu = np.mean([r['resource_usage']['cpu_percent_avg'] for r in results])
    avg_gpu = np.mean([r['resource_usage']['gpu_memory_mb_after'] for r in results if r['resource_usage']['gpu_memory_mb_after'] > 0])
    
    print(f"\nResource Usage:")
    print(f"  Avg train time: {avg_train_time:.1f}s")
    print(f"  Avg total time: {avg_total_time:.1f}s")
    print(f"  Avg CPU: {avg_cpu:.1f}%")
    if avg_gpu > 0:
        print(f"  Avg GPU: {avg_gpu:.1f} MB")
    
    
    print(f"\nStatistical Significance:")
    
    auc_values = overall_metrics['auc']['values']
    
   
    t_stat_random, p_value_random = stats.ttest_1samp(auc_values, 0.5)
    print(f"  vs Random (0.5): t={t_stat_random:.4f}, p={p_value_random:.2e}")
    
   
    auc_auprc_corr, _ = spearmanr(overall_metrics['auc']['values'], overall_metrics['auprc']['values'])
    print(f"  AUC-AUPRC correlation: {auc_auprc_corr:.4f}")
    
    
    (MSAT_ROOT / 'results').mkdir(parents=True, exist_ok=True)
    
    summary = {
        'model_name': 'MSAT-TCMFS-Final',
        'experiment_tag': experiment_tag or 'full',
        'protocol': protocol_metadata(),
        'model_info': {
            'architecture': 'MSAT with 3 core innovations',
            'innovations': [
                'Gated Edge Encoder',
                'Bottleneck Output Transform',
                'Late Fusion with Degree Features'
            ],
            'reference': 'Based on ablation study, uses Global Softmax',
            'ablation': {
                'USE_GATED_EDGE_ENCODER': ModelConfig.USE_GATED_EDGE_ENCODER,
                'USE_BOTTLENECK_TRANSFORM': ModelConfig.USE_BOTTLENECK_TRANSFORM,
                'USE_LATE_FUSION': ModelConfig.USE_LATE_FUSION,
            },
        },
        'data_config': {
            'data_dir': 'experiments_data_clean_final',
            'n_folds': TrainingConfig.N_FOLDS,
            'random_seed': DataConfig.RANDOM_SEED,
            'neg_ratio': DataConfig.NEG_RATIO,
            'test_neg_ratio': DataConfig.TEST_NEG_RATIO,
            'use_optimal_threshold': TrainingConfig.USE_OPTIMAL_THRESHOLD,
        },
        'model_config': {
            'hidden_channels': ModelConfig.HIDDEN_CHANNELS,
            'out_channels': ModelConfig.OUT_CHANNELS,
            'num_layers': ModelConfig.NUM_LAYERS,
            'num_heads': ModelConfig.NUM_HEADS,
            'dropout': ModelConfig.DROPOUT,
            'edge_attr_dim': ModelConfig.EDGE_ATTR_DIM
        },
        'training_config': {
            'learning_rate': TrainingConfig.LEARNING_RATE,
            'weight_decay': TrainingConfig.WEIGHT_DECAY,
            'num_epochs': TrainingConfig.NUM_EPOCHS,
            'patience': TrainingConfig.PATIENCE,
            'gradient_clip': TrainingConfig.GRADIENT_CLIP,
            'save_fold_checkpoints': TrainingConfig.SAVE_FOLD_CHECKPOINTS,
        },
        'overall_metrics': overall_metrics,
        'statistical_tests': {
            't_test_vs_random': {
                't_statistic': float(t_stat_random),
                'p_value': float(p_value_random)
            },
            'auc_auprc_correlation': float(auc_auprc_corr)
        },
        'fold_results': results,
        'resource_usage_avg': {
            'train_time_seconds': avg_train_time,
            'total_time_seconds': avg_total_time,
            'cpu_percent': avg_cpu,
            'gpu_memory_mb': avg_gpu if avg_gpu > 0 else 0
        },
        'experiment_info': {
            'total_experiment_time_seconds': total_experiment_time,
            'avg_best_epoch': np.mean([r['best_epoch'] for r in results]),
            'timestamp': datetime.now().isoformat()
        }
    }
    
    suffix = f'_{experiment_tag}' if experiment_tag else ''
    summary_path = MSAT_ROOT / f'results/summary{suffix}.json'

    if best_overall_state is not None:
        prediction_ckpt = MSAT_ROOT / prediction_checkpoint_path(experiment_tag)
        torch.save(best_overall_state, prediction_ckpt)
        print(
            f"[SAVED] {prediction_ckpt} "
            f"(from fold {best_overall_fold}, best_val_auc={best_overall_score:.4f})"
        )
        summary['prediction_checkpoint'] = str(prediction_ckpt)
        summary['prediction_checkpoint_selection'] = {
            'metric': 'best_val_auc',
            'fold': best_overall_fold,
            'score': float(best_overall_score),
        }

    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n[SAVED] {summary_path}")
    
    print(f"\n{'='*80}")
    print("Training Complete!")
    print(f"{'='*80}")


if __name__ == '__main__':
    run_10fold_cv()
