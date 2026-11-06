"""Post-hoc TTL-shortcut decomposition for Failure Fingerprints.

Uses ONLY official TRAINING records; the designated test split is not opened.
This analysis was designed after inspecting initial group-pair effects and
is therefore exploratory, not preregistered confirmation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from data_audit import row_hashes
from failure_fingerprints import GROUPS, group_permute, metrics
from run_experiments import load_dataset, models, prepare, sha256

TTL = ("sttl", "dttl", "ct_state_ttl")
CONDITIONS = {
    "ttl_only": ("ttl",),
    "protocol_without_ttl": ("protocol_core",),
    "context_without_ttl": ("context_core",),
    "protocol_core+context_core": ("protocol_core", "context_core"),
    "protocol_all+context_all": ("protocol_all", "context_all"),
}


def decomposed_groups(columns):
    columns = set(columns)
    groups = {
        "ttl": [c for c in TTL if c in columns],
        "protocol_core": [c for c in GROUPS["protocol"] if c not in TTL and c in columns],
        "context_core": [c for c in GROUPS["context"] if c not in TTL and c in columns],
        "protocol_all": [c for c in GROUPS["protocol"] if c in columns],
        "context_all": [c for c in GROUPS["context"] if c in columns],
    }
    if any(not values for values in groups.values()) or len(groups["ttl"]) != 3:
        raise ValueError("Required TTL, protocol and context features are missing")
    return groups


def study(train, *, split_seeds=(13,29,47), perturb_seeds=(101, 211), fraction=.25):
    if not 0 < fraction <= 1 or not split_seeds or not perturb_seeds:
        raise ValueError("Nonempty seeds and fraction (0,1] required")
    x, _, preprocessor, cols = prepare(train, train)
    groups = decomposed_groups(cols)
    labels = train.label.to_numpy()
    fingerprints = row_hashes(x, cols).to_numpy()
    outputs = []
    for split_seed in split_seeds:
        splitter = GroupShuffleSplit(test_size=.2, n_splits=1, random_state=int(split_seed))
        fit, valid = next(splitter.split(x, labels, fingerprints))
        if len(set(labels[fit])) != 2 or len(set(labels[valid])) != 2:
            raise ValueError("Both classes required for each split")
        for model_name, estimator in models().items():
            if model_name == "Majority Dummy":
                continue
            pipe = Pipeline([("preprocess", clone(preprocessor)), ("model", clone(estimator))])
            pipe.fit(x.iloc[fit], labels[fit])
            heldout = x.iloc[valid]
            truth = labels[valid]
            clean = metrics(truth, pipe.predict(heldout))
            for perturb_seed in perturb_seeds:
                for condition, selected in CONDITIONS.items():
                    shifted = group_permute(heldout, groups, selected, seed=int(perturb_seed), fraction=fraction)
                    result = metrics(truth, pipe.predict(shifted))
                    outputs.append({
                        "split_seed":int(split_seed), "perturb_seed":int(perturb_seed),
                        "model":model_name, "condition":condition, "n":int(len(valid)),
                        "delta_fpr_pp":100*(result["fpr"]-clean["fpr"]),
                        "delta_recall_loss_pp":100*(clean["recall"]-result["recall"]),
                        "fpr":result["fpr"], "recall":result["recall"],
                        "clean_fpr":clean["fpr"], "clean_recall":clean["recall"],
                        "tn":result["tn"],"fp":result["fp"],"fn":result["fn"],"tp":result["tp"],
                    })
    return {
        "status":"TRAINING_ONLY_POST_HOC_TTL_SENSITIVITY",
        "split_seeds":list(split_seeds), "perturb_seeds":list(perturb_seeds),
        "fraction":fraction, "feature_groups":groups, "conditions":CONDITIONS,
        "results":outputs,
        "limitations":[
            "Post-hoc analysis, motivated by observing initial group interactions.",
            "All perturbations are synthetic and may create inconsistent flow combinations.",
            "Group-held-out validation is not temporally or network-independent.",
            "Overlapping training splits and perturbations do not provide independent replication.",
            "Observed TTL contributions are association/sensitivity, not causal proof."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--train",type=Path,default=Path("data/UNSW_NB15_training-set.csv"))
    p.add_argument("--output",type=Path,default=Path("results/ttl_decomposition.json"))
    args=p.parse_args()
    train=load_dataset(args.train)
    if len(train) != 175341:
        p.error("Expected original 175341 training rows")
    result=study(train)
    result["train_sha256"]=sha256(args.train)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"Recorded {len(result['results'])} TTL decomposition cases")


if __name__=="__main__":
    main()
