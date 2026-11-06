import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttl_decomposition import CONDITIONS, decomposed_groups, study
from failure_fingerprints import GROUPS


def test_ttl_feature_decomposition_exclusive_core():
    columns = [c for members in GROUPS.values() for c in members]
    result = decomposed_groups(columns)
    assert set(result["ttl"]) == {"sttl", "dttl", "ct_state_ttl"}
    assert not set(result["ttl"]).intersection(result["protocol_core"])
    assert not set(result["ttl"]).intersection(result["context_core"])
    assert "ct_state_ttl" in result["context_all"]


def test_missing_required_ttl_rejected():
    with pytest.raises(ValueError):
        decomposed_groups(["sttl","dttl","proto","ct_srv_src"])


def test_conditions_explicit_and_distinct():
    assert "protocol_core+context_core" in CONDITIONS
    assert "protocol_all+context_all" in CONDITIONS
    assert CONDITIONS["ttl_only"] == ("ttl",)


def test_synthetic_training_only_study():
    n = 76
    y = np.tile([0,1], n//2)
    rng = np.random.default_rng(7)
    data = {}
    for col in (c for members in GROUPS.values() for c in members):
        if col in ("proto","service","state"):
            data[col] = np.where(y == 0, "tcp", "udp")
        else:
            data[col] = rng.normal(size=n) + y
    data["label"] = y
    data["id"] = np.arange(n)
    df = pd.DataFrame(data)
    expected = df.copy(deep=True)
    output = study(df, split_seeds=(3, 5), perturb_seeds=(10,11), fraction=.2)
    assert len(output["results"]) == 2 * 2 * 2 * 5
    assert all(0<=r["fpr"]<=1 for r in output["results"])
    pd.testing.assert_frame_equal(df, expected)
