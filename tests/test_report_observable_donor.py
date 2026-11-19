import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from report_observable_donor import summarize, render


def example():
    rows=[]
    for split in (13,29):
        for seed in (101,211):
            for model in ("Random Forest","Logistic Regression"):
                for policy,value in (("global",1.5),("observable_strata",1.0),("same_class_oracle",-.2)):
                    rows.append({
                        "split_seed":split,"donor_seed":seed,"model":model,"policy":policy,
                        "excess_fpr_pp":value,"joint_fpr":.2,"joint_recall":.9,
                        "joint_group_exchange_rate":{"protocol":.24,"context":.25},
                    })
    return {
        "status":"TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL",
        "train_sha256":"toy","rows":rows,"split_seeds":[13,29],"donor_seeds":[101,211],
    }


def test_summary_complete_and_matched():
    result=summarize(example())
    assert len(result["aggregates"])==6
    assert len(result["paired_comparisons"])==4
    for p in result["paired_comparisons"]:
        assert p["mean_global_minus_observable_pp"]==pytest.approx(.5)
        assert p["mean_observable_minus_oracle_pp"]==pytest.approx(1.2)
    assert "training-only" in render(result).lower()


def test_missing_experiment_rejected():
    data=example()
    data["rows"].pop()
    with pytest.raises((ValueError,KeyError)):
        summarize(data)


def test_duplicate_experiment_rejected():
    data=example()
    data["rows"][-1]=data["rows"][0].copy()
    with pytest.raises(ValueError):
        summarize(data)


def test_unexecuted_rejected():
    data=example()
    data["status"]="PENDING"
    with pytest.raises(ValueError):
        summarize(data)
