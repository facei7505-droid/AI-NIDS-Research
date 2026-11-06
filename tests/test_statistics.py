import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uncertainty import binary_metrics, paired_bootstrap_difference


def test_binary_confusion_matrix():
    result = binary_metrics([0, 0, 1, 1], [0, 1, 0, 1])
    assert (result["tn"], result["fp"], result["fn"], result["tp"]) == (1, 1, 1, 1)
    assert result["fpr"] == pytest.approx(0.5)


def test_identical_models_have_zero_difference():
    predictions = [0, 1, 0, 1, 1, 0, 1, 0]
    result = paired_bootstrap_difference(
        [0, 1, 0, 1, 0, 0, 1, 1], predictions, predictions,
        n_resamples=100, seed=13)
    assert result["estimate_a_minus_b"] == 0
    assert result["ci_low"] == 0
    assert result["ci_high"] == 0


def test_bootstrap_is_reproducible():
    args = ([0, 1, 0, 1, 0, 1], [0, 1, 1, 1, 0, 1], [0, 0, 0, 1, 0, 1])
    first = paired_bootstrap_difference(*args, n_resamples=100, seed=9)
    second = paired_bootstrap_difference(*args, n_resamples=100, seed=9)
    assert first == second


def test_invalid_vectors_rejected():
    with pytest.raises(ValueError):
        binary_metrics([0, 1], [0])


def test_invalid_metric_rejected():
    with pytest.raises(ValueError):
        paired_bootstrap_difference([0, 1], [0, 1], [0, 1], metric="accuracy")
