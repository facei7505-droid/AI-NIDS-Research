import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "src"))
from report_alert_budget import render

def test_report_does_not_invent_results():
    record={
        "fpr_budget":.05,"fit_rows":80,"validation_rows":20,"test_rows":15,
        "overlap_rows":4,"nonoverlap_rows":11,"train_sha256":"abc",
        "test_sha256":"def","caveats":["Synthetic example"],
        "results":[
            {"model":"Random Forest","policy":"validation_constrained",
             "status":"evaluated","validation":{"validation_fpr_upper":.049},
             "official_test":{"fpr":.1,"recall":.8,"f1":.7},
             "nonoverlap_test":{"fpr":.15,"recall":.75}},
            {"model":"Majority Dummy","policy":"validation_constrained",
             "status":"infeasible_on_validation","validation":{"feasible":False}}
        ]
    }
    content=render(record)
    assert "10.00%" in content
    assert "15.00%" in content
    assert "infeasible" in content
    assert "Scientific novelty has not been established" in content
