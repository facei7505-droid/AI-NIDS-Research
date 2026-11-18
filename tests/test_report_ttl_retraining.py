import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from report_ttl_retraining import compare, render


def example():
    values=[]
    for seed in (13,29):
        for model in ("Logistic Regression","Random Forest"):
            for design,interaction,clean in (
                ("full",2+.01*seed,.10),("no_ttl",1+.01*seed,.12)
            ):
                values.append({
                    "split_seed":seed,"model":model,"training_design":design,
                    "excess_interaction_fpr_pp":interaction,
                    "clean_fpr":clean
                })
    return {
        "status":"TRAIN_ONLY_POST_HOC_RETRAINED_TTL_ABLATION",
        "split_seeds":[13,29],
        "permutation_seed":751,
        "train_sha256":"example-only",
        "effect_summaries":values
    }


def test_paired_contrasts_respect_seed():
    result=compare(example())
    assert len(result)==2
    assert result[0]["mean_difference_in_excess_interaction_pp"]==pytest.approx(1)
    assert result[0]["mean_clean_fpr_difference_pp"]==pytest.approx(-2)
    assert result[0]["sign_consistent"] is True


def test_report_is_explicitly_exploratory():
    data=example()
    report=render(data,compare(data))
    assert "Post-hoc" in report
    assert "not an independent confirmation" in report.lower()
    assert "example-only" in report


def test_incomplete_evidence_rejected():
    x=example()
    x["effect_summaries"].pop()
    with pytest.raises(ValueError):
        compare(x)
