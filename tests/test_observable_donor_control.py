import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from observable_donor_control import (
    observable_strata, block_permutation, run_study, DONOR_POLICIES
)
from failure_fingerprints import GROUPS


def test_strata_are_label_blind_and_deterministic():
    x=pd.DataFrame({"dur":np.arange(12), "sbytes":np.arange(12)*2})
    y=observable_strata(x)
    assert y.shape == (12,)
    assert len(set(y))>=3
    np.testing.assert_array_equal(y,observable_strata(x))


def test_matched_blocks_preserve_class_and_observable_stratum():
    df=pd.DataFrame({
        "proto":list("abcdefghij"),
        "service":list("abcdefghij"),
        "dur":np.arange(10), "sbytes":np.arange(10)*3
    })
    labels=np.array([0]*5+[1]*5)
    strata=np.array([0]*3+[1]*2+[2]*3+[3]*2)
    # Validate within-class donors with a minimal patched feature-group definition.
    import observable_donor_control as mod
    original=mod.PAIR
    try:
        mod.PAIR={"protocol":("proto","service"),"context":("dur",)}
        for policy in DONOR_POLICIES:
            new,meta=block_permutation(df,labels,("protocol",),
                        policy=policy,fraction=1.,seed=91,strata=strata)
            assert meta["protocol"]["selected_rows"]==10
            pd.testing.assert_series_equal(new["dur"],df["dur"])
            assert set(zip(new.proto,new.service))==set(zip(df.proto,df.service))
            if policy=="same_class_oracle":
                for k in (0,1):
                    subset=labels==k
                    assert set(new.proto[subset])==set(df.proto[subset])
            if policy=="observable_strata":
                for k in np.unique(strata):
                    subset=strata==k
                    assert set(new.proto[subset])==set(df.proto[subset])
    finally:
        mod.PAIR=original


def synthetic(n=72):
    rng=np.random.default_rng(41)
    y=np.tile([0,1],n//2)
    x={}
    for members in GROUPS.values():
        for col in members:
            x[col] = (np.where(y==1,"udp","tcp") if col in
                     {"proto","service","state"} else rng.normal(size=n)+y)
    x["label"]=y
    x["id"]=np.arange(n)
    return pd.DataFrame(x)


def test_complete_three_policy_study():
    data=synthetic()
    copy=data.copy(deep=True)
    results=run_study(data,splits=(13,29),donor_seeds=(101,211),fraction=.4)
    assert len(results["rows"])==2*2*2*3
    assert results["policies"]==list(DONOR_POLICIES)
    assert all(np.isfinite(r["excess_fpr_pp"]) for r in results["rows"])
    pd.testing.assert_frame_equal(copy,data)


@pytest.mark.parametrize("fraction",[-.1,0,1.1])
def test_invalid_fraction(fraction):
    with pytest.raises(ValueError):
        run_study(synthetic(),fraction=fraction)


def test_missing_matching_feature_rejected():
    with pytest.raises(ValueError):
        run_study(synthetic().drop(columns="sbytes"))
