import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_robustness import evaluate, experiment


def fixtures():
    train = pd.DataFrame({"label": [0, 1] * 8, "id": list(range(16)),
                          "duration": [1, 9, 2, 8] * 4,
                          "proto": ["tcp", "udp"] * 8})
    test = pd.DataFrame({"label": [0, 1] * 3, "id": list(range(16, 22)),
                         "duration": [1, 10, 2, 9, 1.5, 8],
                         "proto": ["tcp", "udp"] * 3})
    return train, test


def test_metrics_match_confusion_counts():
    metrics = evaluate([0, 0, 1, 1], [0, 1, 0, 1], [0.1, 0.6, 0.4, 0.9])
    assert (metrics["tn"], metrics["fp"], metrics["fn"], metrics["tp"]) == (1, 1, 1, 1)
    assert metrics["fpr"] == pytest.approx(.5)


def test_real_models_run_and_dont_mutate_data():
    training, testing = fixtures()
    t1, t2 = training.copy(deep=True), testing.copy(deep=True)
    rows, features = experiment(training, testing, severities=(0.0, .25), seed=42)
    assert len(rows) == 3 * (1 + 3 * 2)
    assert features == ["duration", "proto"]
    assert all(x["tn"] + x["fp"] + x["fn"] + x["tp"] == len(testing) for x in rows)
    pd.testing.assert_frame_equal(training, t1)
    pd.testing.assert_frame_equal(testing, t2)


def test_invalid_severity_rejected():
    with pytest.raises(ValueError):
        experiment(*fixtures(), severities=(2.0,))
