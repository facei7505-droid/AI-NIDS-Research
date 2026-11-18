"""Verify internal consistency of published class-mixing and replication evidence."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "results"


def read(name):
    path = ROOT/name
    if not path.is_file():
        pytest.skip(f"Generated research output not yet published: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def test_class_mixing_paired_results_match_raw_experiment():
    source=read("class_mixing_control.json")
    analysis=read("class_mixing_analysis.json")
    assert source["train_sha256"]==analysis["data_sha256"]
    assert len(source["interactions"])==3*2*2
    for row in analysis["results"]:
        assert len(row["paired_global_minus_within_class_pp_by_seed"])==3
        for seed, expected in zip(row["split_seeds"],row["paired_global_minus_within_class_pp_by_seed"]):
            global_v=next(x["excess_fpr_pp"] for x in source["interactions"]
                          if x["seed"]==seed and x["model"]==row["model"] and x["mode"]=="global")
            within_v=next(x["excess_fpr_pp"] for x in source["interactions"]
                          if x["seed"]==seed and x["model"]==row["model"] and x["mode"]=="within_class")
            assert expected==pytest.approx(global_v-within_v)


def test_permutation_replication_is_full_factorial_when_published():
    data=read("permutation_seed_replication.json")
    assert data["status"]=="EXPLORATORY_TRAIN_ONLY_PERMUTATION_SEED_REPLICATION"
    assert len(data["split_seeds"])==3
    assert len(data["permutation_seeds"])==5
    assert len(data["rows"])==60
    keys={(x["split_seed"],x["permutation_seed"],x["model"],x["donor_policy"])
          for x in data["rows"]}
    assert len(keys)==60
    assert len(data["summaries"])==6
    for x in data["rows"]:
        assert 0<=x["joint_fpr"]<=1
        assert 0<=x["joint_recall"]<=1
