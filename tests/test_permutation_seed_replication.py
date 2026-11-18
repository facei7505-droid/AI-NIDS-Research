import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from permutation_seed_replication import run, summarize
from failure_fingerprints import GROUPS


def synthetic(n=72):
    rng=np.random.default_rng(2026)
    y=np.tile([0,1],n//2)
    x={}
    for group in GROUPS.values():
        for col in group:
            if col in ("proto","service","state"):
                x[col]=np.where(y==0,"tcp","udp")
            else:
                x[col]=rng.normal(size=n)+y
    x["label"]=y
    x["id"]=np.arange(n)
    return pd.DataFrame(x)


def test_seed_replication_complete_and_without_test_data():
    source=synthetic()
    before=source.copy(deep=True)
    result=run(source,split_seeds=(3,5),permutation_seeds=(11,17,23),fraction=.25)
    assert result["status"]=="EXPLORATORY_TRAIN_ONLY_PERMUTATION_SEED_REPLICATION"
    assert len(result["rows"])==2*2*3*2
    summaries=summarize(result)
    assert len(summaries)==2*2
    for entry in result["rows"]:
        assert 0 <= entry["joint_fpr"] <= 1
        assert np.isfinite(entry["excess_fpr_pp"])
    pd.testing.assert_frame_equal(source,before)


def test_duplicate_seeds_invalid():
    with pytest.raises(ValueError):
        run(synthetic(),split_seeds=(3,3))
    with pytest.raises(ValueError):
        run(synthetic(),permutation_seeds=(11,11,17))


@pytest.mark.parametrize("fraction",[-.1,0.,1.1])
def test_invalid_fraction(fraction):
    with pytest.raises(ValueError):
        run(synthetic(),fraction=fraction)


def test_summary_rejects_duplicate_records():
    result=run(synthetic(),split_seeds=(3,5),permutation_seeds=(11,17,23))
    result["rows"][0]=result["rows"][1].copy()
    with pytest.raises(ValueError):
        summarize(result)
