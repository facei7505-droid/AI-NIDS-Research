import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from alert_budget_study import choose_threshold, evaluate, run_study, wilson_upper


def toy():
    rows = 80
    train = pd.DataFrame({
        "id": np.arange(rows),
        "label": np.tile([0, 1], rows // 2),
        "duration": np.linspace(1, 12, rows),
        "proto": np.tile(["tcp", "udp"], rows // 2),
    })
    test = pd.DataFrame({
        "id": np.arange(1000, 1020),
        "label": [0, 1] * 10,
        "duration": np.linspace(1.4, 11, 20),
        "proto": ["tcp", "udp"] * 10,
    })
    return train, test


def test_wilson_upper_increases_with_false_positives():
    values = wilson_upper(np.array([0, 1, 10]), 100)
    assert 0 < values[0] < values[1] < values[2] < 1


def test_budget_infeasible_when_too_few_negatives():
    result = choose_threshold([0.1, 0.7, 0.8, 0.9], [0, 0, 1, 1], max_fpr=.01)
    assert not result["feasible"]
    assert result["threshold"] is None


def test_all_scores_below_strict_threshold_means_no_alert():
    scores = [0.1] * 100 + [0.9] * 50
    labels = [0] * 100 + [1] * 50
    chosen = choose_threshold(scores, labels, max_fpr=.05)
    assert chosen["feasible"]
    assert chosen["validation_fpr_upper"] <= .05
    assert chosen["validation_recall"] == 1.0


def test_threshold_uses_no_test_labels():
    scores = [0.1] * 200 + [0.8] * 100
    labels = [0] * 200 + [1] * 100
    result = choose_threshold(scores, labels, max_fpr=.05)
    assert result["feasible"]
    assert result["validation_fpr"] <= .05


def test_evaluate_confusion():
    result = evaluate([0, 0, 1, 1], [0.1, 0.9, 0.2, 0.8], .5)
    assert (result["tn"], result["fp"], result["fn"], result["tp"]) == (1, 1, 1, 1)


def test_study_on_toy_and_nonoverlap():
    train, test = toy()
    original = train.copy(deep=True)
    result = run_study(train, test, max_fpr=.3, seed=42)
    assert result["test_rows"] == 20
    assert result["fit_rows"] + result["validation_rows"] == 80
    assert result["nonoverlap_rows"] <= 20
    assert len(result["results"]) == 6
    for entry in result["results"]:
        if entry["status"] == "evaluated":
            m = entry["official_test"]
            assert m["tn"] + m["fp"] + m["fn"] + m["tp"] == 20
    pd.testing.assert_frame_equal(train, original)
