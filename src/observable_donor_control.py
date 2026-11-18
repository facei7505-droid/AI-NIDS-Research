"""Class-blind, observable-stratified donors for feature-interaction diagnostics.

The matching features 'dur' and 'sbytes' are NEVER permuted in this
Protocol+Context analysis. Their validation-only quantile strata do not use
ground-truth class labels. Matched donor-pool shuffling is *not* a guarantee
of physically plausible traffic or a deployment-quality IDS intervention.

Research status: exploratory post-hoc extension; original official TEST is
never read here.
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

from class_mixing_control import PAIR
from data_audit import row_hashes
from failure_fingerprints import metrics
from run_experiments import load_dataset, models, prepare, sha256

MATCHING_FEATURES = ("dur", "sbytes")
DONOR_POLICIES = ("global", "observable_strata", "same_class_oracle")
PERTURBATIONS = {
    "protocol": ("protocol",),
    "context": ("context",),
    "protocol+context": ("protocol", "context"),
}


def observable_strata(frame: pd.DataFrame, *, columns=MATCHING_FEATURES, bins=3):
    """Create class-blind strata from unperturbed observed input features."""
    if bins < 2:
        raise ValueError("Need at least two possible quantile bins")
    n = len(frame)
    code = np.zeros(n, dtype=np.int64)
    for column in columns:
        if column not in frame.columns:
            raise ValueError(f"Matching feature unavailable: {column}")
        x = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)
        finite = x[np.isfinite(x)]
        if not len(finite):
            raise ValueError(f"No finite values for matching feature {column}")
        median = np.median(finite)
        x = np.where(np.isfinite(x), x, median)
        cuts = np.unique(np.quantile(x, np.linspace(0, 1, bins + 1))[1:-1])
        code = code * bins + np.searchsorted(cuts, x, side="right")
    return code


def block_permutation(frame, labels, selected_groups, *, policy, fraction,
                      seed, strata=None):
    """Matched mask for each feature group under the three donor policies.

    Returns the transformed data and metadata on *index exchanges* attempted.
    Ground-truth labels are accessed ONLY when policy is same_class_oracle.
    """
    if policy not in DONOR_POLICIES:
        raise ValueError("Unknown donor policy")
    if not 0 <= fraction <= 1:
        raise ValueError("Invalid perturbation fraction")
    n = len(frame)
    labels = np.asarray(labels)
    if labels.shape != (n,):
        raise ValueError("Expected one ground-truth label per row")
    if policy == "same_class_oracle" and not np.isin(labels, [0, 1]).all():
        raise ValueError("Oracle policy requires binary labels")
    if policy == "observable_strata":
        if strata is None:
            raise ValueError("Observable strata required")
        strata = np.asarray(strata)
        if strata.shape != (n,):
            raise ValueError("Observable strata must match row count")
    if len(set(selected_groups)) != len(selected_groups):
        raise ValueError("Duplicate feature groups")
    result = frame.copy(deep=True)
    stats = {}
    for name in selected_groups:
        if name not in PAIR:
            raise ValueError(f"Unknown feature group: {name}")
        columns = list(PAIR[name])
        if not set(columns).issubset(frame.columns):
            raise ValueError("Missing feature block")
        rng = np.random.default_rng(seed + list(PAIR).index(name) * 100003)
        mask = rng.random(n) < fraction
        if policy == "global":
            pools = (np.arange(n),)
        else:
            group_keys = labels if policy == "same_class_oracle" else strata
            pools = tuple(np.flatnonzero(group_keys == k) for k in np.unique(group_keys))
        exchanged = 0
        for pool in pools:
            source_indices = pool[mask[pool]]
            if len(source_indices) < 2:
                continue
            donor_indices = rng.permutation(source_indices)
            exchanged += int(np.count_nonzero(donor_indices != source_indices))
            result.iloc[source_indices, result.columns.get_indexer(columns)] = (
                frame.iloc[donor_indices][columns].to_numpy()
            )
        stats[name] = {
            "selected_rows": int(np.sum(mask)),
            "exchanged_indices": exchanged,
            "exchange_rate": float(exchanged / n) if n else 0.0,
        }
    return result, stats


def run_study(train, *, splits=(13,29,47), donor_seeds=(101,211,307),
              fraction=.25):
    if len(splits)<2 or len(donor_seeds)<2:
        raise ValueError("Multiple splits and donor seeds required")
    if not (0 < fraction <= 1):
        raise ValueError("Fraction must be within (0,1]")
    x, _, preprocess, features = prepare(train, train)
    required = set(MATCHING_FEATURES) | set(PAIR["protocol"]) | set(PAIR["context"])
    if not required.issubset(features):
        raise ValueError("Missing required matching or tested features")
    y = train.label.to_numpy()
    fingerprint = row_hashes(x, features).to_numpy()
    rows = []
    for split_seed in splits:
        fit, val = next(GroupShuffleSplit(n_splits=1, test_size=.2,
                              random_state=int(split_seed)).split(x, y, fingerprint))
        if set(y[fit]) != {0,1} or set(y[val]) != {0,1}:
            raise ValueError("Both classes required in train and validation")
        val_x, val_y = x.iloc[val], y[val]
        strata = observable_strata(val_x)
        for model_name, estimator in models().items():
            if model_name == "Majority Dummy":
                continue
            model = Pipeline([("preprocess", clone(preprocess)), ("model", clone(estimator))])
            model.fit(x.iloc[fit], y[fit])
            clean = metrics(val_y, model.predict(val_x))
            for donor_seed in donor_seeds:
                for policy in DONOR_POLICIES:
                    record = {}
                    for condition, selected in PERTURBATIONS.items():
                        corrupted, exchanges = block_permutation(
                            val_x, val_y, selected, policy=policy,
                            fraction=fraction, seed=int(donor_seed), strata=strata)
                        record[condition] = {
                            **metrics(val_y, model.predict(corrupted)),
                            "exchange_rate_by_group": {k:v["exchange_rate"] for k,v in exchanges.items()},
                        }
                    p,c,j = (record[key] for key in PERTURBATIONS)
                    rows.append({
                        "split_seed":int(split_seed),"donor_seed":int(donor_seed),
                        "model":model_name,"policy":policy,
                        "validation_rows":int(len(val)),
                        "clean_fpr":clean["fpr"],
                        "protocol_fpr":p["fpr"],"context_fpr":c["fpr"],
                        "joint_fpr":j["fpr"],"joint_recall":j["recall"],
                        "excess_fpr_pp":100*(j["fpr"]-p["fpr"]-c["fpr"]+clean["fpr"]),
                        "joint_group_exchange_rate":j["exchange_rate_by_group"],
                    })
    return {
        "status":"TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL",
        "split_seeds":list(map(int,splits)),
        "donor_seeds":list(map(int,donor_seeds)),
        "policies":list(DONOR_POLICIES),
        "matching_features":list(MATCHING_FEATURES),
        "quantile_bins_per_feature":3,
        "fraction":fraction,"rows":rows,
        "caveats":[
            "Within-class policy is an oracle control and not usable without ground-truth labels.",
            "Observable matching is label-blind but bins are computed on the held-out validation features, so it is a transductive evaluation diagnostic, not a learned production sampler.",
            "Stratification on two features does not guarantee realistic joint flows or complete feature-conditional draws.",
            "Per-stratum donor pool sizes change exchange frequency; exchange-rate metadata must be compared.",
            "Protocol+Context was selected after prior results. No independent external dataset used."
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--train",type=Path,default=Path("data/UNSW_NB15_training-set.csv"))
    parser.add_argument("--output",type=Path,default=Path("results/observable_donor_control.json"))
    args=parser.parse_args()
    training=load_dataset(args.train)
    if len(training)!=175341:
        parser.error("Requires official training split of 175341 rows")
    result=run_study(training)
    result["train_sha256"]=sha256(args.train)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n",encoding="utf-8")
    print(f"Recorded {len(result['rows'])} policy/split/seed/model conditions")


if __name__ == "__main__":
    main()
