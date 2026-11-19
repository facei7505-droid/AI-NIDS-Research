"""Independent integrity checks for published frozen donor comparison."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from compare_matching_boundaries import compare

RESULTS=Path(__file__).resolve().parents[1]/"results"


def load(name):
    return json.loads((RESULTS/name).read_text(encoding="utf-8"))


def test_full_paired_frozen_donor_evidence():
    original=load("observable_donor_control.json")
    frozen=load("train_fitted_donor_control.json")
    published=load("donor_quantile_comparison.json")
    fresh=compare(original,frozen)
    assert len(frozen["rows"])==54
    assert len(frozen["frozen_strata_parameters"])==3
    assert published["train_sha256"]==fresh["train_sha256"]
    assert published["n_paired_conditions"]==54
    assert len(published["comparisons"])==54
    assert len(published["summary"])==6
    for a,b in zip(published["summary"],fresh["summary"]):
        assert a["model"]==b["model"] and a["policy"]==b["policy"]
        assert a["n_paired_cells"]==b["n_paired_cells"]==9
        for key in (
            "mean_old_excess_fpr_pp",
            "mean_frozen_excess_fpr_pp",
            "mean_frozen_minus_old_excess_fpr_pp",
            "mean_frozen_minus_old_joint_fpr_pp",
            "mean_frozen_minus_old_joint_recall_pp",
        ):
            assert a[key]==pytest.approx(b[key],abs=1e-12)


def test_report_exposes_provenance_and_limitations():
    report=(RESULTS/"DONOR_QUANTILE_COMPARISON.md").read_text(encoding="utf-8")
    assert "Executed post-hoc" in report
    assert "Random Forest" in report
    assert "Logistic Regression" in report
    assert "No independent dataset" in report
