import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from class_mixing_control import (
    permute_blocks, matched_experiment, interaction_effects
)
from failure_fingerprints import GROUPS


def test_within_class_preserves_label_conditioned_group_blocks():
    data = pd.DataFrame({
        "proto": ["a","b","c","d","e","f","g","h"],
        "sttl": [1,2,3,4,5,6,7,8],
        "other": list("abcdefgh"),
    })
    labels = np.array([0,0,0,0,1,1,1,1])
    groups = {"protocol": ["proto","sttl"]}
    output = permute_blocks(data, labels, groups=groups, selected=("protocol",),
                            mode="within_class", fraction=1.0, seed=30)
    for label in (0,1):
        ids = np.flatnonzero(labels==label)
        assert sorted(map(tuple, output.iloc[ids][["proto","sttl"]].to_numpy())) == sorted(
            map(tuple, data.iloc[ids][["proto","sttl"]].to_numpy())
        )
    assert output["other"].tolist() == data["other"].tolist()
    pd.testing.assert_frame_equal(data, pd.DataFrame({
        "proto": ["a","b","c","d","e","f","g","h"],
        "sttl": [1,2,3,4,5,6,7,8],
        "other": list("abcdefgh"),
    }))


def test_matched_masks_and_determinism():
    frame = pd.DataFrame({"a": list(range(20)), "b": list(range(20,40))})
    labels = np.array([0,1]*10)
    args = dict(groups={"A":["a"],"B":["b"]}, mode="within_class",
                seed=16, fraction=.65)
    full = permute_blocks(frame, labels, selected=("A","B"), **args)
    a = permute_blocks(frame, labels, selected=("A",), **args)
    b = permute_blocks(frame, labels, selected=("B",), **args)
    assert full["a"].tolist() == a["a"].tolist()
    assert full["b"].tolist() == b["b"].tolist()


@pytest.mark.parametrize("mode,fraction", [("bad",.2),("global",-1),("within_class",1.5)])
def test_invalid_parameters(mode,fraction):
    with pytest.raises(ValueError):
        permute_blocks(pd.DataFrame({"a":[1,2]}), [0,1], groups={"p":["a"]},
                       selected=("p",),mode=mode,fraction=fraction)


def toy_training(n=100):
    rng = np.random.default_rng(5)
    y = np.array([0,1]*(n//2))
    data = {}
    for group in GROUPS.values():
        for col in group:
            if col in {"proto","service","state"}:
                data[col] = np.where(y==1, "udp","tcp")
            else:
                data[col] = rng.normal(size=n) + y
    data["label"] = y
    data["id"] = np.arange(n)
    return pd.DataFrame(data)


def test_train_only_experiment_is_complete_and_paired():
    training=toy_training()
    original=training.copy(deep=True)
    output=matched_experiment(training,seeds=(13,29),fraction=.25)
    assert len(output["rows"])==2*2*7
    interactions=interaction_effects(output)
    assert len(interactions)==2*2*2
    for entry in output["rows"]:
        assert entry["tn"]+entry["fp"]+entry["fn"]+entry["tp"]==entry["n"]
    pd.testing.assert_frame_equal(training,original)
