import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from failure_fingerprints import GROUPS, analyze, group_permute, interaction_table, metrics, resolved_groups


def test_groups_cover_official_declared_features():
    all_features = [feature for group in GROUPS.values() for feature in group]
    assert len(all_features) == len(set(all_features))
    assert resolved_groups(all_features).keys() == GROUPS.keys()


def test_joint_permutation_preserves_marginals_and_original():
    frame = pd.DataFrame({
        "a": [1, 2, 3, 4, 5, 6], "b": [10, 20, 30, 40, 50, 60],
        "other": ["x", "y", "z", "w", "p", "q"],
    })
    original = frame.copy(deep=True)
    groups = {"ab": ["a", "b"], "other": ["other"]}
    permuted = group_permute(frame, groups, ("ab",), seed=101, fraction=1.)
    assert set(zip(permuted.a, permuted.b)) == set(zip(frame.a, frame.b))
    assert permuted.other.tolist() == original.other.tolist()
    pd.testing.assert_frame_equal(frame, original)


def test_corruption_is_deterministic_and_zero_is_identity():
    frame = pd.DataFrame({"a": [1, 2, 3, 4], "b": ["x", "y", "z", "w"]})
    groups = {"a": ["a"], "b": ["b"]}
    x = group_permute(frame, groups, ("a", "b"), seed=13, fraction=.75)
    y = group_permute(frame, groups, ("a", "b"), seed=13, fraction=.75)
    pd.testing.assert_frame_equal(x, y)
    pd.testing.assert_frame_equal(group_permute(frame, groups, ("a",), seed=13, fraction=0), frame)


def test_clean_confusion_counts():
    result = metrics([0, 0, 1, 1], [0, 1, 0, 1])
    assert (result["tn"], result["fp"], result["fn"], result["tp"]) == (1, 1, 1, 1)
    assert result["fpr"] == .5


def test_unknown_group_rejected():
    with pytest.raises(ValueError):
        group_permute(pd.DataFrame({"a": [1, 2]}), {"a": ["a"]},
                      ("absent",), seed=1, fraction=1.)


def test_train_only_study_on_synthetic_records():
    n = 60
    labels = np.array([0, 1] * (n // 2))
    features = [name for members in GROUPS.values() for name in members]
    rng = np.random.default_rng(12)
    sample = {}
    for col in features:
        if col in ("proto", "service", "state"):
            sample[col] = np.where(labels == 0, "tcp", "udp")
        else:
            sample[col] = rng.normal(0, 1, n) + labels
    sample["label"] = labels
    sample["id"] = np.arange(n)
    train = pd.DataFrame(sample)
    original = train.copy(deep=True)
    report = analyze(train, seeds=(17, 23), fraction=.5)
    assert report["status"] == "TRAINING_ONLY_EXPLORATORY_SYNTHETIC_DIAGNOSTIC"
    assert len(report["rows"]) == 2 * 2 * 11
    pairs = interaction_table(report)
    assert len(pairs) == 2 * 2 * 6
    assert all(np.isfinite(x["excess_fpr_pp"]) for x in pairs)
    pd.testing.assert_frame_equal(train, original)
