import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from train_fitted_donor_control import FrozenQuantileStrata,run_experiment
from observable_donor_control import block_permutation
from failure_fingerprints import GROUPS


def test_bins_learn_only_from_fitting_rows():
    train=pd.DataFrame({"dur":np.arange(1,31),"sbytes":np.arange(1,31)*10})
    frozen=FrozenQuantileStrata().fit(train)
    baseline=frozen.export()
    test=pd.DataFrame({"dur":[3,15,35,100000],"sbytes":[30,150,350,10000000]})
    predictions=frozen.transform(test)
    extra=pd.DataFrame({"dur":[-100,-10000,999999],"sbytes":[-1,8888,99999]})
    predictions_with_more_test_rows=frozen.transform(pd.concat([test,extra],ignore_index=True))[:len(test)]
    np.testing.assert_array_equal(predictions,predictions_with_more_test_rows)
    assert frozen.export()==baseline


def test_strata_never_require_labels():
    x=pd.DataFrame({"dur":[1,2,3,4,5,6],"sbytes":[10,20,30,40,50,60]})
    grouping=FrozenQuantileStrata().fit(x)
    classes_a=np.array([0,1,0,1,0,1])
    classes_b=1-classes_a
    np.testing.assert_array_equal(grouping.transform(x),grouping.transform(x))
    assert not hasattr(grouping,"labels")
    assert not hasattr(grouping,"target")


def test_observable_donor_policy_independent_of_target_labels():
    import observable_donor_control as mod
    original=mod.PAIR
    try:
        mod.PAIR={"protocol":("proto",),"context":("context",)}
        df=pd.DataFrame({
            "proto":list("abcdefghijkl"),
            "context":list("mnopqrstuvwx"),
            "dur":np.arange(12),"sbytes":np.arange(12)*2,
        })
        strata=FrozenQuantileStrata().fit(df).transform(df)
        y=np.tile([0,1],6)
        for policy in ("global","observable_strata"):
            a,_=block_permutation(df,y,("protocol","context"),policy=policy,
                                  seed=99,fraction=1.0,strata=strata)
            b,_=block_permutation(df,1-y,("protocol","context"),policy=policy,
                                  seed=99,fraction=1.0,strata=strata)
            pd.testing.assert_frame_equal(a,b)
    finally:
        mod.PAIR=original


def make_data(n=74):
    rng=np.random.default_rng(419)
    labels=np.tile([0,1],n//2)
    data={}
    for columns in GROUPS.values():
        for col in columns:
            data[col]=np.where(labels==0,"tcp","udp") if col in ("proto","service","state") else rng.normal(size=n)+labels
    data["label"]=labels
    data["id"]=np.arange(n)
    return pd.DataFrame(data)


def test_training_fitted_study_full_design():
    data=make_data()
    unchanged=data.copy(deep=True)
    study=run_experiment(data,split_seeds=(13,29),donor_seeds=(101,211),fraction=.25)
    assert study["status"]=="POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA"
    assert len(study["rows"])==2*2*2*3
    assert len(study["frozen_strata_parameters"])==2
    for split in study["frozen_strata_parameters"]:
        assert split["strata_parameters_fit_on"]=="training_rows_only"
        assert split["fit_rows"]+split["validation_rows"]==len(data)
    pd.testing.assert_frame_equal(unchanged,data)


def test_unfitted_bins_and_missing_feature_rejected():
    x=pd.DataFrame({"dur":[1,2,3],"sbytes":[10,20,30]})
    with pytest.raises(ValueError):
        FrozenQuantileStrata().transform(x)
    with pytest.raises(ValueError):
        FrozenQuantileStrata().fit(x.drop(columns="dur"))


@pytest.mark.parametrize("fraction",[-1,0,1.1])
def test_invalid_fraction(fraction):
    with pytest.raises(ValueError):
        run_experiment(make_data(),fraction=fraction)
