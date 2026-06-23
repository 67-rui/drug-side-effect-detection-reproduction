
import os
from pathlib import Path


class ModelConfig:
    
    HIDDEN_CHANNELS = 576
    OUT_CHANNELS = 72
    NUM_LAYERS = 3
    NUM_HEADS = 8
    DROPOUT = 0.18
    EDGE_ATTR_DIM = 6
    
   
    USE_GATED_EDGE_ENCODER = True      
    USE_BOTTLENECK_TRANSFORM = True   
    USE_LATE_FUSION = True             
    USE_DEGREE_FEATURES = True         
    USE_EPSILON = True                 
    USE_DEGREE_SCALING = True          
    USE_GLOBAL_SOFTMAX = True         


class TrainingConfig:
    
   
    NUM_EPOCHS = 1000
    PATIENCE = 100
    
    
    LEARNING_RATE = 0.0004
    WEIGHT_DECAY = 1e-5
    OPTIMIZER = 'AdamW'
    
  
    GRADIENT_CLIP = 1.0
    BATCH_SIZE = 512
    
   
    N_FOLDS = 10
    TRAIN_VAL_SPLIT = 0.9  
    
   
    SCHEDULER_MODE = 'max'
    SCHEDULER_FACTOR = 0.6
    SCHEDULER_PATIENCE = 15
    
  
    RANDOM_STATE = 42
    USE_OPTIMAL_THRESHOLD = False  # True for 1:10 imbalanced (Phase 6)
    SAVE_FOLD_CHECKPOINTS = os.environ.get('MSAT_SAVE_FOLD_CHECKPOINTS', '').lower() in {
        '1', 'true', 'yes'
    }


class DataConfig:
    
  
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_ROOT / 'experiments_data_clean_final'
    GRAPH_PATH = DATA_DIR / 'complete_hetero_graph.pt'
    FOLDS_DIR = DATA_DIR / 'folds'
    FOLD_SPLIT_PATH = Path(__file__).resolve().parent / 'data' / '10fold_cv_split.pkl'
    NEG_RATIO = 1  # 1:1 type-constrained negative sampling (paper Section 3.5.1)
    TEST_NEG_RATIO = 1  # test split ratio; use >1 with NEG_RATIO=1 for Fig.6 sweep
    
  
    N_FOLDS = 10
    RANDOM_SEED = 42
    
 
    INDUCTIVE_MODE = True
