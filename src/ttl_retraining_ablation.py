"""Matched train-only TTL ablation experiment for Failure Fingerprints.

Unlike a TTL feature perturbation, this study RETRAINS each estimator without
TTL-related fields. It uses paired, duplicate-group-held-out split indices,
identical learning algorithms, and matched conditional perturbation seeds.

Official UNSW-NB15 test data are never read. This study is post-hoc,
exploratory and must not be called independent confirmation.
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
from failure_fingerprints import group_permute, metrics
from run_experiments import load_dataset, models, prepare, sha256
from ttl_decomposition import decomposed_groups, TTL


def run_ablation(training, *, split_seeds=(13, 29, 47), permutation_seed=751, fraction=.25):
    if not split_seeds or len(set(split_seeds)) != len(split_seeds):
        raise ValueError("Require distinct, nonempty split seeds")
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be within (0,1]")
    full_x, _, full_preprocess, feature_names = prepare(training, training)
    missing = set(TTL) - set(feature_names)
    if missing:
        raise ValueError(f"Required TTL features missing: {sorted(missing)}")
    reduced = training.drop(columns=list(TTL))
    no_ttl_x, _, reduced_preprocess, _ = prepare(reduced, reduced)
    ttl_groups = decomposed_groups(feature_names)
    core = {
        "protocol_core": ttl_groups["protocol_core"],
        "context_core": ttl_groups["context_core"],
    }
    conditions = {
        "clean": (),
        "protocol_core": ("protocol_core",),
        "context_core": ("context_core",),
        "protocol_core+context_core": ("protocol_core", "context_core"),
    }
    y = training.label.to_numpy()
    hashes = row_hashes(full_x, feature_names).to_numpy()
    records = []
    for seed in split_seeds:
        split = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=int(seed))
        fitting, validation = next(split.split(full_x, y, hashes))
        if set(np.unique(y[fitting])) != {0,1} or set(np.unique(y[validation])) != {0,1}:
            raise ValueError("Both classes required in fit and validation")
        for model_name, estimator in models().items():
            if model_name == "Majority Dummy":
                continue
            for design, x, transform in (
                ("full", full_x, full_preprocess),
                ("no_ttl", no_ttl_x, reduced_preprocess),
            ):
                model = Pipeline([("preprocess", clone(transform)), ("model", clone(estimator))])
                model.fit(x.iloc[fitting], y[fitting])
                baseline = x.iloc[validation]
                for name, selected_groups in conditions.items():
                    if selected_groups:
                        evaluation = group_permute(baseline, core, selected_groups,
                                                   seed=int(permutation_seed), fraction=fraction)
                    else:
                        evaluation = baseline
                    measured = metrics(y[validation], model.predict(evaluation))
                    records.append({
                        "split_seed": int(seed),
                        "permutation_seed": int(permutation_seed),
                        "model": model_name,
                        "training_design": design,
                        "condition": name,
                        "train_rows": int(len(fitting)),
                        "validation_rows": int(len(validation)),
                        "fraction": float(fraction),
                        **measured,
                    })
    return {
        "status": "TRAIN_ONLY_POST_HOC_RETRAINED_TTL_ABLATION",
        "ttl_columns": list(TTL),
        "split_seeds": list(map(int, split_seeds)),
        "permutation_seed": int(permutation_seed),
        "fraction": float(fraction),
        "feature_group_definitions": core,
        "rows": records,
        "scientific_limits": [
            "Retraining without TTL changes feature dimensionality and model fitting; it is a design comparison, not a causal intervention on the network.",
            "Official designated test data are not loaded; all evaluations use grouped training-held-out validation.",
            "This experiment was specified after inspecting earlier Protocol+Context and TTL perturbation effects; it is post-hoc.",
            "Group permutations may violate physical constraints of network flows.",
            "Seeds reuse one dataset, and observations may be correlated within network sessions.",
            "Do not infer an original discovery or external generalization without independent data and literature comparison.",
        ],
    }


def effects(study):
    out = []
    records = {(r["split_seed"], r["model"], r["training_design"], r["condition"]): r
               for r in study["rows"]}
    for seed in study["split_seeds"]:
        for model in sorted({r["model"] for r in study["rows"]}):
            for design in ("full", "no_ttl"):
                ref = records[(seed, model, design, "clean")]
                core = ["protocol_core", "context_core", "protocol_core+context_core"]
                m = {c: records[(seed, model, design, c)] for c in core}
                interaction = 100 * (m["protocol_core+context_core"]["fpr"]
                                     - m["protocol_core"]["fpr"]
                                     - m["context_core"]["fpr"] + ref["fpr"])
                out.append({
                    "split_seed":seed, "model":model, "training_design":design,
                    "clean_fpr":ref["fpr"], "clean_recall":ref["recall"],
                    "joint_delta_fpr_pp":100*(m["protocol_core+context_core"]["fpr"]-ref["fpr"]),
                    "excess_interaction_fpr_pp":interaction,
                    "joint_recall_loss_pp":100*(ref["recall"]-m["protocol_core+context_core"]["recall"]),
                })
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=Path("data/UNSW_NB15_training-set.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/ttl_retraining_ablation.json"))
    args = parser.parse_args()
    training = load_dataset(args.train)
    if len(training) != 175341:
        parser.error("Official training split (175341 rows) required")
    result = run_ablation(training)
    result["train_sha256"] = sha256(args.train)
    result["effect_summaries"] = effects(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Stored", len(result["rows"]), "evaluations and",
          len(result["effect_summaries"]), "interaction contrasts")


if __name__ == "__main__":
    main()
