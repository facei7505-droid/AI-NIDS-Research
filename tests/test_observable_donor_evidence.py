import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from report_observable_donor import summarize

ROOT=Path(__file__).resolve().parents[1]/"results"

def test_executed_observable_donor_report_matches_raw_json():
    raw=json.loads((ROOT/"observable_donor_control.json").read_text(encoding="utf-8"))
    saved=json.loads((ROOT/"observable_donor_analysis.json").read_text(encoding="utf-8"))
    recalculated=summarize(raw)
    assert raw["train_sha256"]==saved["train_sha256"]
    assert len(raw["rows"])==3*3*2*3
    assert len(saved["aggregates"])==6
    assert len(saved["paired_comparisons"])==6
    for row in recalculated["aggregates"]:
        original=next(x for x in saved["aggregates"]
                      if x["model"]==row["model"] and x["policy"]==row["policy"])
        for col in ("mean_excess_fpr_pp","mean_joint_fpr","mean_joint_recall",
                    "mean_exchange_protocol","mean_exchange_context"):
            assert row[col]==pytest.approx(original[col],abs=1e-12)
        assert row["conditions"]==original["conditions"]==9
    for row in recalculated["paired_comparisons"]:
        original=next(x for x in saved["paired_comparisons"]
                      if x["model"]==row["model"] and x["split_seed"]==row["split_seed"])
        for key in ("mean_global_minus_observable_pp","mean_observable_minus_oracle_pp"):
            assert row[key]==pytest.approx(original[key],abs=1e-12)


def test_report_uses_measured_values_without_claiming_novelty():
    report=(ROOT/"OBSERVABLE_DONOR_REPORT.md").read_text(encoding="utf-8")
    assert "Random Forest" in report
    assert "observable_strata" in report
    assert "0.959" in report
    assert "1.610" in report
    assert "independently validated" in report
