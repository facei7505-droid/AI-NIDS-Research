import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_audit import audit_splits, row_hashes


def test_overlap_and_conflicts_are_flagged():
    train = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "duration": [1, 2, 2, 3],
        "proto": ["tcp", "udp", "udp", "icmp"],
        "label": [0, 0, 1, 1],
    })
    test = pd.DataFrame({
        "id": [11, 12, 13],
        "duration": [2, 4, 1],
        "proto": ["udp", "tcp", "tcp"],
        "label": [1, 0, 0],
    })
    results = audit_splits(train, test)
    assert results["train_rows"] == 4
    assert results["test_rows_matching_training_predictors"] == 2
    assert results["duplicate_train_rows"] == 1
    assert results["conflicting_duplicate_feature_groups_train"] == 1
    assert results["conflicting_feature_groups_pooled"] == 1


def test_reordered_columns_have_matching_hash():
    first = pd.DataFrame({"label": [0], "proto": ["tcp"], "duration": [3]})
    second = pd.DataFrame({"duration": [3], "proto": ["tcp"], "label": [0]})
    assert audit_splits(first, second)["test_overlap_fraction"] == 1.0


def test_missing_columns_rejected():
    a = pd.DataFrame({"label": [0], "duration": [1]})
    b = pd.DataFrame({"label": [0], "different": [1]})
    with pytest.raises(ValueError, match="schemas"):
        audit_splits(a, b)


def test_no_predictor_columns_rejected():
    with pytest.raises(ValueError, match="No predictor"):
        row_hashes(pd.DataFrame({"label": [1]}), [])


def test_original_frames_unchanged():
    a = pd.DataFrame({"label": [0, 1], "duration": [1.0, None]})
    b = pd.DataFrame({"label": [1], "duration": [None]})
    baseline_a = a.copy(deep=True)
    baseline_b = b.copy(deep=True)
    audit_splits(a, b)
    pd.testing.assert_frame_equal(a, baseline_a)
    pd.testing.assert_frame_equal(b, baseline_b)
