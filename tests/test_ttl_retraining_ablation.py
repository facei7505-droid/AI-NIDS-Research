import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttl_retraining_ablation import run_ablation, effects
from failure_fingerprints import GROUPS


def synthetic_training(n=80):
    rng=np.random.default_rng(27)
    labels=np.tile(np.array([0,1]), n//2)
    features={}
    for col in (c for group in GROUPS.values() for c in group):
        if col in {"proto","service","state"}:
            features[col] = np.where(labels==0,"tcp","udp")
        else:
            features[col] = rng.normal(size=n) + labels
    features["id"] = np.arange(n)
    features["label"] = labels
    return pd.DataFrame(features)


def test_ttl_retraining_matched_data_and_no_input_mutation():
    source=synthetic_training()
    original=source.copy(deep=True)
    result=run_ablation(source,split_seeds=(17,23),permutation_seed=13,fraction=.25)
    assert len(result["rows"])==2*2*2*4
    assert len(effects(result))==2*2*2
    assert {r["training_design"] for r in result["rows"]}=={"full","no_ttl"}
    for row in result["rows"]:
        assert row["validation_rows"]+row["train_rows"] == len(source)
        assert 0<=row["fpr"]<=1
        assert row["tn"]+row["fp"]+row["fn"]+row["tp"]==row["validation_rows"]
    pd.testing.assert_frame_equal(source,original)


def test_retraining_uses_same_split_under_both_designs():
    result=run_ablation(synthetic_training(),split_seeds=(17,23),fraction=.4)
    by_split={}
    for row in result["rows"]:
        by_split.setdefault(row["split_seed"],set()).add(
            (row["train_rows"],row["validation_rows"]))
    assert all(len(rows)==1 for rows in by_split.values())


@pytest.mark.parametrize("fraction",[-.1,0,1.1])
def test_invalid_perturbation_rate_rejected(fraction):
    with pytest.raises(ValueError):
        run_ablation(synthetic_training(),fraction=fraction)


def test_missing_ttl_rejected():
    with pytest.raises(ValueError):
        run_ablation(synthetic_training().drop(columns="sttl"))
