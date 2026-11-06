import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze_alert_budget import analyze, wilson_interval, render


def study():
    return {
        "fpr_budget": .05, "train_sha256": "a", "test_sha256": "b",
        "results": [
            {"model": "RF", "policy": "default", "status": "evaluated",
             "official_test": {"tn": 70, "fp": 30, "fn": 2, "tp": 98, "fpr": .3, "recall": .98},
             "nonoverlap_test": {"tn": 35, "fp": 15, "fn": 2, "tp": 48, "fpr": .3, "recall": .96}},
            {"model": "RF", "policy": "validation_constrained", "status": "evaluated",
             "threshold": .7,
             "validation": {"validation_fpr": .04, "validation_fpr_upper": .049},
             "official_test": {"tn": 85, "fp": 15, "fn": 10, "tp": 90, "fpr": .15, "recall": .9},
             "nonoverlap_test": {"tn": 43, "fp": 7, "fn": 8, "tp": 42, "fpr": .14, "recall": .84}},
        ],
    }


def test_wilson_boundary():
    lo, hi = wilson_interval(0, 100)
    assert lo == 0
    assert 0 < hi < .1
    lo, hi = wilson_interval(100, 100)
    assert lo > .9
    assert hi == 1


def test_transfer_records_actual_tradeoff():
    data = analyze(study())
    records = data["findings"]
    assert len(records) == 2
    assert records[0]["false_alarms_prevented"] == 15
    assert records[0]["additional_attacks_missed"] == 8
    assert records[0]["budget_violated"] is True
    assert records[0]["recall_cost_pp"] == pytest.approx(8)
    assert records[1]["budget_overshoot_pp"] == pytest.approx(9)


def test_report_labels_as_exploratory():
    output = render(analyze(study()))
    assert "Executed exploratory analysis" in output
    assert "False alarms avoided" in output
    assert "15.00%" in output


@pytest.mark.parametrize("fp,total", [(-1, 10), (11, 10), (0, 0)])
def test_invalid_binomial(fp, total):
    with pytest.raises(ValueError):
        wilson_interval(fp, total)
