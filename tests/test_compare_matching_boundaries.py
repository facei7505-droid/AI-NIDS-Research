import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from compare_matching_boundaries import compare,report


def example(status,shift=0.):
    rows=[]
    for split in (13,29):
        for seed in (101,211):
            for model in ("Random Forest","Logistic Regression"):
                for policy in ("global","observable_strata","same_class_oracle"):
                    rows.append({
                        "split_seed":split,"donor_seed":seed,"model":model,"policy":policy,
                        "excess_fpr_pp":1.+shift,"joint_fpr":.1+shift*.01,
                        "joint_recall":.9-shift*.01,
                    })
    return {
        "status":status,"train_sha256":"toy-sha",
        "split_seeds":[13,29],"donor_seeds":[101,211],
        "fraction":.25,"rows":rows,
    }


def test_all_cells_paired_and_numerically_reproducible():
    old=example("TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL")
    new=example("POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA",shift=.3)
    found=compare(old,new)
    assert found["n_paired_conditions"]==24
    assert len(found["summary"])==6
    assert all(s["mean_frozen_minus_old_excess_fpr_pp"]==pytest.approx(.3) for s in found["summary"])
    assert "Exploratory" in report(found)


def test_hash_mismatch_rejected():
    old=example("TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL")
    new=example("POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA")
    new["train_sha256"]="different"
    with pytest.raises(ValueError):
        compare(old,new)


def test_seed_mismatch_rejected():
    old=example("TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL")
    new=example("POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA")
    new["donor_seeds"]=[211,101]
    with pytest.raises(ValueError):
        compare(old,new)


def test_incomplete_or_duplicate_cells_rejected():
    old=example("TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL")
    new=example("POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA")
    new["rows"].pop()
    with pytest.raises(ValueError):
        compare(old,new)
    new=example("POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA")
    new["rows"][0]=new["rows"][1].copy()
    with pytest.raises(ValueError):
        compare(old,new)
