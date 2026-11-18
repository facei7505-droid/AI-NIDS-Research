import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from analyze_class_mixing import validate_and_summarize,render


def sample():
    rows=[]
    for seed in [13,29,47]:
        for model in ["Random Forest","Logistic Regression"]:
            for mode,value in [("global",1.5),("within_class",-.2)]:
                rows.append({"seed":seed,"model":model,"mode":mode,"excess_fpr_pp":value})
    return {"status":"TRAIN_ONLY_POST_HOC_CLASS_MIXING_CONTROL",
            "split_seeds":[13,29,47],"interactions":rows,"train_sha256":"example"}


def test_paired_comparisons_are_correct():
    result=validate_and_summarize(sample())
    assert len(result["results"])==2
    for row in result["results"]:
        assert row["mean_paired_difference_pp"]==pytest.approx(1.7)
        assert row["paired_difference_positive_all_splits"] is True
    assert "post-hoc" in render(result).lower()


def test_missing_mode_rejected():
    s=sample()
    s["interactions"].pop()
    with pytest.raises(ValueError):
        validate_and_summarize(s)


def test_duplicate_record_rejected():
    s=sample()
    s["interactions"][-1]=s["interactions"][0].copy()
    with pytest.raises(ValueError):
        validate_and_summarize(s)


def test_unexecuted_rejected():
    s=sample()
    s["status"]="PENDING"
    with pytest.raises(ValueError):
        validate_and_summarize(s)
