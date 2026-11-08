"""Guard the numerical integrity of versioned scientific evidence.

These tests validate archived records against each other, not their authorship,
dataset representativeness or the truth of scientific conclusions.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TRAIN_SHA = "bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa"
TEST_SHA = "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559"


def load_json(name):
    p = RESULTS / name
    assert p.is_file(), f"Required archived evidence missing: {p}"
    return json.loads(p.read_text(encoding="utf-8"))


def test_benchmark_rows_and_hashes():
    data = pd.read_csv(RESULTS / "metrics_FULL_BENCHMARK.csv")
    metadata = load_json("metadata_FULL_BENCHMARK.json")
    assert metadata["train_sha256"] == TRAIN_SHA
    assert metadata["test_sha256"] == TEST_SHA
    assert metadata["train_rows"] == 175341
    assert metadata["test_rows"] == 82332
    assert set(data["model"]) == {"Majority Dummy", "Logistic Regression", "Random Forest"}
    assert (data["train_rows"] == 175341).all()
    assert (data["test_rows"] == 82332).all()
    for item in data.itertuples():
        assert item.tn + item.fp + item.fn + item.tp == 82332
        assert item.false_positive_rate == pytest.approx(item.fp / (item.fp + item.tn))
        assert item.recall == pytest.approx(item.tp / (item.tp + item.fn))
        assert 0 <= item.f1 <= 1


def test_audit_fraction_is_reconstructable():
    a = load_json("data_audit.json")
    assert a["train_rows"] == 175341 and a["test_rows"] == 82332
    assert a["predictor_columns"] == 42
    assert a["test_overlap_fraction"] == pytest.approx(
        a["test_rows_matching_training_predictors"] / a["test_rows"]
    )


def test_alert_budget_records_and_derived_analysis():
    study = load_json("alert_budget_study.json")
    derived = load_json("alert_budget_analysis.json")
    assert study["train_sha256"] == derived["train_sha256"] == TRAIN_SHA
    assert study["test_sha256"] == derived["test_sha256"] == TEST_SHA
    assert len(study["results"]) == 6
    assert study["nonoverlap_rows"] + study["overlap_rows"] == 82332
    for item in study["results"]:
        if item["status"] != "evaluated":
            continue
        for split, n in (("official_test", 82332), ("nonoverlap_test", study["nonoverlap_rows"])):
            m = item[split]
            assert m["tn"] + m["fp"] + m["fn"] + m["tp"] == n
            assert m["fpr"] == pytest.approx(m["fp"] / (m["tn"] + m["fp"]))
    for row in derived["findings"]:
        baseline = next(i for i in study["results"]
                        if i["model"] == row["model"] and i["policy"] == "default")
        tuned = next(i for i in study["results"]
                     if i["model"] == row["model"] and i["policy"] == "validation_constrained")
        assert row["false_alarms_prevented"] == (
            baseline[row["subset"]]["fp"] - tuned[row["subset"]]["fp"]
        )
        assert row["additional_attacks_missed"] == (
            tuned[row["subset"]]["fn"] - baseline[row["subset"]]["fn"]
        )


def test_failure_fingerprints_all_conditions_and_pairwise_algebra():
    r = load_json("failure_fingerprints.json")
    assert r["train_sha256"] == TRAIN_SHA
    assert r["status"] == "TRAINING_ONLY_EXPLORATORY_SYNTHETIC_DIAGNOSTIC"
    assert len(r["rows"]) == 3 * 2 * 11
    assert len(r["interactions"]) == 3 * 2 * 6
    lookup = {(row["seed"], row["model"], row["condition"]): row
              for row in r["rows"]}
    assert len(lookup) == len(r["rows"])
    for pair in r["interactions"]:
        a, b = pair["pair"].split("+")
        key = (pair["seed"], pair["model"])
        fpr = lambda condition: lookup[(*key, condition)]["fpr"]
        expected = 100 * (fpr(pair["pair"]) - fpr(a) - fpr(b) + fpr("clean"))
        assert pair["excess_fpr_pp"] == pytest.approx(expected)


def test_ttl_decomposition_full_design():
    r = load_json("ttl_decomposition.json")
    assert r["train_sha256"] == TRAIN_SHA
    assert r["status"] == "TRAINING_ONLY_POST_HOC_TTL_SENSITIVITY"
    assert len(r["results"]) == 3 * 2 * 2 * 5
    assert set(r["feature_groups"]["ttl"]) == {"sttl", "dttl", "ct_state_ttl"}
    for record in r["results"]:
        assert record["tn"] + record["fp"] + record["fn"] + record["tp"] == record["n"]
        assert 0 <= record["fpr"] <= 1 and 0 <= record["recall"] <= 1
