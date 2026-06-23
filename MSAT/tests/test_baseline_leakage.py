import numpy as np

from baselines.common import pair_features


def test_pair_features_exclude_edge_attr_by_default():
    herb_x = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    adr_x = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
    h = np.array([0, 1])
    a = np.array([1, 0])
    edge_attr_map = {
        (0, 1): np.ones(6, dtype=np.float32),
        (1, 0): np.ones(6, dtype=np.float32),
    }

    features = pair_features(herb_x, adr_x, h, a, edge_attr_map)

    assert features.shape == (2, 4)
    np.testing.assert_array_equal(
        features,
        np.array(
            [
                [1.0, 2.0, 7.0, 8.0],
                [3.0, 4.0, 5.0, 6.0],
            ],
            dtype=np.float32,
        ),
    )


def test_pair_features_can_include_edge_attr_for_explicit_diagnostics():
    herb_x = np.array([[1.0, 2.0]], dtype=np.float32)
    adr_x = np.array([[3.0, 4.0]], dtype=np.float32)
    h = np.array([0])
    a = np.array([0])
    edge_attr = np.arange(6, dtype=np.float32)

    features = pair_features(
        herb_x,
        adr_x,
        h,
        a,
        {(0, 0): edge_attr},
        include_edge_attr=True,
    )

    assert features.shape == (1, 10)
    np.testing.assert_array_equal(features[0, -6:], edge_attr)
