import pytest
from pathlib import Path

from experiments.feature_extractor import FeatureExtractor

DATA_DIR = Path(__file__).resolve().parents[2] / 'experiments_data_clean_final'


@pytest.mark.skipif(not (DATA_DIR / 'complete_hetero_graph.pt').exists(), reason='data not downloaded')
def test_graph_has_four_node_types():
    ext = FeatureExtractor(data_dir=str(DATA_DIR))
    data = ext.get_graph_data()
    for ntype in ('herb', 'compound', 'target', 'adr'):
        assert ntype in data.node_types
    assert data['herb'].x.shape == (651, 768)
    assert data['adr'].x.shape == (5974, 768)


@pytest.mark.skipif(not (DATA_DIR / 'complete_hetero_graph.pt').exists(), reason='data not downloaded')
def test_fold_loads_neg10_samples():
    fold_split = Path(__file__).resolve().parents[1] / 'data' / '10fold_cv_split.pkl'
    if not fold_split.exists():
        pytest.skip('official fold split not downloaded')
    ext = FeatureExtractor(
        data_dir=str(DATA_DIR),
        fold_split_path=str(fold_split),
        neg_ratio=10,
    )
    train, test = ext.load_fold_data(0)
    n_train_pos = int((train['labels'] == 1).sum())
    n_test_pos = int((test['labels'] == 1).sum())
    assert len(train['labels']) == n_train_pos * 11
    assert len(test['labels']) == n_test_pos * 11
    assert (train['labels'] == 1).sum() == n_train_pos
    assert (train['labels'] == 0).sum() == n_train_pos * 10
    assert (test['labels'] == 1).sum() == n_test_pos
    assert (test['labels'] == 0).sum() == n_test_pos * 10


@pytest.mark.skipif(not (DATA_DIR / 'complete_hetero_graph.pt').exists(), reason='data not downloaded')
def test_fold_loads_balanced_samples():
    fold_split = Path(__file__).resolve().parents[1] / 'data' / '10fold_cv_split.pkl'
    if not fold_split.exists():
        pytest.skip('official fold split not downloaded')
    ext = FeatureExtractor(data_dir=str(DATA_DIR), fold_split_path=str(fold_split))
    train, test = ext.load_fold_data(0)
    assert len(train['labels']) == 48711
    assert len(test['labels']) == 5413
    assert set(train.keys()) == {'herb_indices', 'adr_indices', 'labels'}
    assert (train['labels'] == 1).sum() > 0
    assert (test['labels'] == 1).sum() > 0
