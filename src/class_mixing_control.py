"""Falsification control: is the Protocol+Context interaction a class-mixing artifact?

TRAINING-SPLIT ONLY, post-hoc diagnostic. Contrast global group permutation
against within-class block permutation with matched model, split and masks.
Class labels used to form donors are forbidden at real IDS inference time.
This control cannot be deployed or interpreted as causal traffic simulation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from data_audit import row_hashes
from failure_fingerprints import GROUPS, metrics
from run_experiments import load_dataset, models, prepare, sha256

PAIR = {
    "protocol": tuple(GROUPS["protocol"]),
    "context": tuple(GROUPS["context"]),
}
CONDITIONS = ("clean", "protocol", "context", "protocol+context")
MODES = ("global", "within_class")


def permute_blocks(
    frame: pd.DataFrame,
    labels,
    *,
    groups=PAIR,
    selected=(),
    mode="global",
    seed=701,
    fraction=.25,
) -> pd.DataFrame:
    """Shuffle whole group blocks; preserve each group's within-block values.

    Each group gets its own seed, independent of whether a partner group is
    permuted. Within-class permutations preserve class membership but use
    ground-truth labels FOR DIAGNOSTIC PURPOSES ONLY.
    """
    labels = np.asarray(labels)
    if labels.ndim != 1 or len(labels) != len(frame):
        raise ValueError("One class label required per row")
    if not np.isin(labels, [0, 1]).all():
        raise ValueError("Only binary 0/1 labels supported")
    if mode not in MODES:
        raise ValueError("Unrecognized permutation mode")
    if not 0 <= fraction <= 1 or not np.isfinite(fraction):
        raise ValueError("fraction must be finite in [0,1]")
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate groups are not permitted")
    if any(k not in groups for k in selected):
        raise ValueError("Unrecognized group")
    output = frame.copy(deep=True)
    for name in selected:
        cols = list(groups[name])
        if any(c not in frame for c in cols):
            raise ValueError(f"Unknown feature in {name}")
        rng = np.random.default_rng(seed + list(groups).index(name) * 100003)
        mask = rng.random(len(frame)) < fraction
        if mode == "global":
            strata = (np.arange(len(frame)),)
        else:
            strata = (np.flatnonzero(labels == 0), np.flatnonzero(labels == 1))
        for ids in strata:
            chosen = ids[mask[ids]]
            if len(chosen) < 2:
                continue
            donors = rng.permutation(chosen)
            # Positional assignment avoids index alignment and maintains
            # original dtype-compatible feature values.
            output.iloc[chosen, output.columns.get_indexer(cols)] = frame.iloc[donors][cols].to_numpy()
    return output


def matched_experiment(train, *, seeds=(13, 29, 47), fraction=.25, perturb_seed=701):
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Distinct nonempty seeds required")
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0,1]")
    x, _, preprocessor, features = prepare(train, train)
    if any(column not in features for group in PAIR.values() for column in group):
        raise ValueError("Missing Protocol or Context feature")
    y = train.label.to_numpy()
    fingerprints = row_hashes(x, features).to_numpy()
    rows = []
    for seed in seeds:
        split = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=int(seed))
        fitting, validating = next(split.split(x, y, fingerprints))
        if set(y[fitting]) != {0,1} or set(y[validating]) != {0,1}:
            raise ValueError("Both classes needed in every split")
        xval = x.iloc[validating]
        yval = y[validating]
        for model_name, estimator in models().items():
            if model_name == "Majority Dummy":
                continue
            fitted = Pipeline([("preprocess", clone(preprocessor)), ("model", clone(estimator))])
            fitted.fit(x.iloc[fitting], y[fitting])
            clean = metrics(yval, fitted.predict(xval))
            rows.append({"seed": int(seed), "model": model_name, "mode": "clean",
                         "condition": "clean", "fraction": 0., "n": len(validating), **clean})
            for mode in MODES:
                for condition, names in (
                    ("protocol", ("protocol",)),
                    ("context", ("context",)),
                    ("protocol+context", ("protocol", "context")),
                ):
                    altered = permute_blocks(xval, yval, selected=names, mode=mode,
                                             fraction=fraction, seed=perturb_seed)
                    measurements = metrics(yval, fitted.predict(altered))
                    rows.append({"seed": int(seed), "model": model_name, "mode": mode,
                                 "condition": condition, "fraction": fraction,
                                 "n": len(validating), **measurements})
    return {
        "status": "TRAIN_ONLY_POST_HOC_CLASS_MIXING_CONTROL",
        "experiment_date_note": "Experiment protocol designed after observing initial group interactions.",
        "split_seeds": list(map(int, seeds)),
        "permutation_seed": perturb_seed,
        "fraction": fraction,
        "groups": PAIR,
        "rows": rows,
        "limitations": [
            "Ground-truth labels inform donor selection only in offline diagnostic; prohibited for deployment.",
            "Global versus within-class perturbations do not preserve joint physical network constraints.",
            "Post-hoc Protocol+Context focus was selected after seeing preliminary results.",
            "One historic corpus and overlapping splits cannot establish external transfer or novelty.",
        ],
    }


def interaction_effects(result):
    lookup = {(r["seed"], r["model"], r["mode"], r["condition"]): r for r in result["rows"]}
    rows = []
    for seed in result["split_seeds"]:
        for model in sorted({r["model"] for r in result["rows"]}):
            clean = lookup[(seed, model, "clean", "clean")]
            for mode in MODES:
                p = lookup[(seed, model, mode, "protocol")]
                c = lookup[(seed, model, mode, "context")]
                joint = lookup[(seed, model, mode, "protocol+context")]
                rows.append({
                    "seed": seed, "model": model, "mode": mode,
                    "clean_fpr": clean["fpr"],
                    "joint_fpr": joint["fpr"],
                    "excess_fpr_pp": 100*(joint["fpr"]-p["fpr"]-c["fpr"]+clean["fpr"]),
                    "joint_recall_loss_pp": 100*(clean["recall"]-joint["recall"]),
                })
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=Path("data/UNSW_NB15_training-set.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/class_mixing_control.json"))
    args=parser.parse_args()
    training=load_dataset(args.train)
    if len(training)!=175341:
        parser.error("Official training split of 175341 rows required")
    result=matched_experiment(training)
    result["train_sha256"]=sha256(args.train)
    result["interactions"]=interaction_effects(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"Recorded {len(result['rows'])} cases and {len(result['interactions'])} effects")


if __name__=="__main__":
    main()
