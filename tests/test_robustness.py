import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from robustness import corrupt_features


@pytest.fixture
def pairs():
    training = pd.DataFrame({"value": [1., 2., 3., 4.], "proto": ["tcp", "udp", "tcp", "icmp"]})
    testing = pd.DataFrame({"value": [1., 3., 2., 4.], "proto": ["tcp", "udp", "tcp", "udp"]})
    return training, testing


@pytest.mark.parametrize("mode", ["numeric_noise", "missingness", "novel_categories"])
def test_severity_zero_is_identity(pairs, mode):
    train, test = pairs
    result = corrupt_features(train, test, severity=0, mode=mode)
    pd.testing.assert_frame_equal(result, test)
    assert result is not test


def test_missingness_all_cells(pairs):
    train, test = pairs
    result = corrupt_features(train, test, severity=1, mode="missingness")
    assert result.isna().all().all()
    assert not test.isna().any().any()


def test_novel_categories_deterministic(pairs):
    train, test = pairs
    first = corrupt_features(train, test, severity=.7, mode="novel_categories", seed=123)
    second = corrupt_features(train, test, severity=.7, mode="novel_categories", seed=123)
    pd.testing.assert_frame_equal(first, second)


def test_gaussian_noise_is_seeded_and_copy_on_write(pairs):
    train, test = pairs
    original = test.copy(deep=True)
    changed = corrupt_features(train, test, severity=1, mode="numeric_noise", seed=55)
    changed2 = corrupt_features(train, test, severity=1, mode="numeric_noise", seed=55)
    pd.testing.assert_frame_equal(changed, changed2)
    pd.testing.assert_frame_equal(test, original)
    assert np.any(changed["value"] != original["value"])


def test_invalid_severity(pairs):
    with pytest.raises(ValueError):
        corrupt_features(*pairs, severity=1.1, mode="missingness")


def test_mismatched_columns(pairs):
    train, test = pairs
    with pytest.raises(ValueError):
        corrupt_features(train, test.drop(columns="proto"), severity=.5, mode="missingness")
