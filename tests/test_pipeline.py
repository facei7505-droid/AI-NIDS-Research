import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_experiments import load_dataset, prepare, measure, models


def sample():
    train = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "label": [0, 1, 0, 1, 0, 1],
        "attack_cat": ["Normal", "Attack"] * 3,
        "duration": [1.0, 5.0, 2.0, 6.0, 1.5, 5.5],
        "protocol": ["tcp", "udp", "tcp", "udp", "tcp", "udp"],
    })
    test = pd.DataFrame({
        "id": [10, 11],
        "label": [0, 1],
        "attack_cat": ["Normal", "Attack"],
        "duration": [1.0, 8.0],
        "protocol": ["unknown", "udp"],
    })
    return train, test


def test_prepare_excludes_label_id_attack_category():
    train, test = sample()
    xtr, xte, transformer, cols = prepare(train, test)
    assert cols == ["duration", "protocol"]
    assert set(xtr.columns) == set(xte.columns)
    transformer.fit(xtr)
    assert transformer.transform(xte).shape[0] == 2


def test_incompatible_schema_rejected():
    train, test = sample()
    with pytest.raises(ValueError, match="features"):
        prepare(train, test.drop(columns="protocol"))


@pytest.mark.parametrize("values", [[0, 1, 2], [0, 1, None]])
def test_invalid_labels_rejected(tmp_path, values):
    path = tmp_path / "data.csv"
    pd.DataFrame({"label": values, "duration": [1, 2, 3]}).to_csv(path, index=False)
    with pytest.raises((ValueError, TypeError)):
        load_dataset(path)


def test_confusion_invariants():
    train, test = sample()
    xtr, xte, transformer, _ = prepare(train, test)
    result = measure("Logistic Regression", models()["Logistic Regression"],
                     transformer, xtr, train.label.to_numpy(), xte, test.label.to_numpy())
    assert result["tn"] + result["fp"] + result["fn"] + result["tp"] == len(test)
    assert 0 <= result["f1"] <= 1
    assert np.isfinite(result["inference_ms_per_1000"])
