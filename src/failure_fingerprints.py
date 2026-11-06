"""Failure Fingerprints: validation-only group-permutation interaction experiment.

The official UNSW-NB15 test set is NEVER loaded. Perturbations are synthetic
joint row permutations within feature groups, not physical network events.
This is an exploratory diagnostic, not an adversarial attack or deployment test.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import confusion_matrix, f1_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from data_audit import row_hashes
from run_experiments import load_dataset, models, prepare, sha256

GROUPS = {
    "timing": ("dur", "sinpkt", "dinpkt", "sjit", "djit", "tcprtt", "synack", "ackdat"),
    "volume": ("sbytes", "dbytes", "spkts", "dpkts", "sload", "dload", "sloss", "dloss", "smean", "dmean"),
    "protocol": ("proto", "service", "state", "sttl", "dttl", "swin", "dwin", "stcpb", "dtcpb"),
    "context": ("ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm", "ct_dst_src_ltm",
                "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_state_ttl", "ct_flw_http_mthd",
                "ct_ftp_cmd", "is_ftp_login", "is_sm_ips_ports", "trans_depth", "response_body_len", "rate"),
}


def resolved_groups(columns):
    columns = set(columns)
    groups = {name: [col for col in candidates if col in columns] for name, candidates in GROUPS.items()}
    missing = sorted(columns - set(sum(groups.values(), [])))
    if missing:
        raise ValueError(f"Unassigned features require a deliberate protocol update: {missing}")
    if any(not values for values in groups.values()):
        raise ValueError("All four feature groups must be present")
    return groups


def group_permute(frame: pd.DataFrame, groups: dict, names: tuple[str, ...], *, seed: int, fraction: float):
    """Jointly replace selected rows' feature-group block from donor rows.

    A shared permutation per group preserves internal group co-occurrence
    while breaking correlations between this group and other groups.
    Group-specific seeds make single- and joint-group conditions comparable.
    """
    if not 0 <= fraction <= 1:
        raise ValueError("fraction must lie between 0 and 1")
    output = frame.copy(deep=True)
    if fraction == 0:
        return output
    for name in names:
        if name not in groups:
            raise ValueError(f"Unknown group {name}")
        cols = groups[name]
        group_seed = seed + list(groups).index(name) * 100003
        rng = np.random.default_rng(group_seed)
        selected = np.flatnonzero(rng.random(len(frame)) < fraction)
        if len(selected) < 2:
            continue
        # Shuffling the selected rows avoids introducing new marginal values.
        donors = rng.permutation(selected)
        output.loc[output.index[selected], cols] = frame.iloc[donors][cols].to_numpy()
    return output


def metrics(y, pred):
    tn, fp, fn, tp = map(int, confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return {"fpr": fp / (fp + tn) if tn + fp else None,
            "recall": float(recall_score(y, pred, zero_division=0)),
            "f1": float(f1_score(y, pred, zero_division=0)),
            "tn": tn, "fp": fp, "fn": fn, "tp": tp}


def analyze(train: pd.DataFrame, *, seeds=(13, 29, 47), fraction=.25):
    """Run only on pre-existing TRAINING split with duplicate-group holdouts."""
    if len(seeds) < 2 or not 0 < fraction <= 1:
        raise ValueError("At least 2 split seeds and a positive perturbation fraction are needed")
    # Training CSV is the sole data input. A dummy schema copy is used only by
    # prepare() so transformations retain consistent column order.
    x, _, transformer, columns = prepare(train, train)
    groups = resolved_groups(columns)
    target = train["label"].to_numpy()
    if set(np.unique(target)) != {0, 1}:
        raise ValueError("Both classes required")
    fingerprints = row_hashes(x, columns).to_numpy()
    rows = []
    for split_seed in seeds:
        splitter = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=int(split_seed))
        fit_idx, val_idx = next(splitter.split(x, target, fingerprints))
        if len(set(target[fit_idx])) != 2 or len(set(target[val_idx])) != 2:
            raise ValueError("Split requires both classes")
        fit_x, val_x = x.iloc[fit_idx], x.iloc[val_idx]
        fit_y, val_y = target[fit_idx], target[val_idx]
        for model_name, model in models().items():
            if model_name == "Majority Dummy":
                continue
            pipeline = Pipeline([("preprocess", clone(transformer)), ("model", clone(model))])
            pipeline.fit(fit_x, fit_y)
            clean = metrics(val_y, pipeline.predict(val_x))
            rows.append({"seed": int(split_seed), "model": model_name, "condition": "clean",
                         "features": [], "fraction": 0., **clean})
            for names in [(k,) for k in groups] + list(combinations(groups, 2)):
                permuted = group_permute(val_x, groups, names, seed=int(split_seed), fraction=fraction)
                result = metrics(val_y, pipeline.predict(permuted))
                rows.append({"seed": int(split_seed), "model": model_name,
                             "condition": "+".join(names), "features": list(names),
                             "fraction": float(fraction), **result})
    return {
        "status": "TRAINING_ONLY_EXPLORATORY_SYNTHETIC_DIAGNOSTIC",
        "split_seeds": list(map(int, seeds)), "fraction": fraction,
        "groups": groups, "rows": rows,
        "notes": [
            "Only the official training CSV is used, never the official test CSV.",
            "Validation groups are separated by predictor fingerprints; not temporal or independent-network separation.",
            "A joint shuffle preserves within-group values, but can create physically impossible cross-group feature combinations.",
            "Changes in performance are sensitivity diagnostics, not causal feature attribution.",
            "Paired-group interaction is delta(A+B)-delta(A)-delta(B), using clean validation metric as reference.",
            "A replication or novelty claim requires external untouched data and literature comparison."
        ]
    }


def interaction_table(result):
    """Pair interactions: excess deterioration beyond single-group sum."""
    output = []
    for seed in result["split_seeds"]:
        for model in sorted({r["model"] for r in result["rows"]}):
            subset = {r["condition"]: r for r in result["rows"]
                      if r["seed"] == seed and r["model"] == model}
            baseline = subset["clean"]
            for a, b in combinations(result["groups"], 2):
                both, first, second = subset[f"{a}+{b}"], subset[a], subset[b]
                output.append({
                    "seed": seed, "model": model, "pair": f"{a}+{b}",
                    "excess_fpr_pp": 100 * (both["fpr"] - first["fpr"] - second["fpr"] + baseline["fpr"]),
                    "excess_recall_loss_pp": 100 * (-both["recall"] + first["recall"] + second["recall"] - baseline["recall"]),
                })
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=Path("data/UNSW_NB15_training-set.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/failure_fingerprints.json"))
    parser.add_argument("--fraction", type=float, default=.25)
    args = parser.parse_args()
    train = load_dataset(args.train)
    if len(train) != 175341:
        parser.error("Expected official training split (175341 rows)")
    report = analyze(train, fraction=args.fraction)
    report["train_sha256"] = sha256(args.train)
    report["interactions"] = interaction_table(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(report['rows'])} cases and {len(report['interactions'])} pair interactions")


if __name__ == "__main__":
    main()
