"""Leakage-conscious, validation-only alert-budget study for offline UNSW-NB15.

Prospective research question: does a threshold constrained by VALIDATION
false-positive rate preserve its intended alarm budget on the designated
test split, including test records not duplicated in the training pool?

This is NOT an original detector, deployment guarantee, or confirmed result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from data_audit import row_hashes
from run_experiments import OFFICIAL_ROWS, load_dataset, models, prepare, sha256


def wilson_upper(successes: np.ndarray, total: int, confidence: float = .95) -> np.ndarray:
    """One-sided Wilson upper bound on a Bernoulli proportion."""
    if total < 1 or not 0 <= successes.min() <= successes.max() <= total:
        raise ValueError("Invalid binomial counts")
    z = NormalDist().inv_cdf(confidence)
    p = successes / total
    denom = 1 + z*z/total
    centre = p + z*z/(2*total)
    rad = z * np.sqrt(p*(1-p)/total + z*z/(4*total*total))
    return np.minimum(1., (centre + rad)/denom)


def choose_threshold(scores, labels, *, max_fpr=.05, confidence=.95):
    """Maximize validation alert sensitivity subject to one-sided FPR bound.

    Threshold chosen from training-only held-out validation data; ties get
    the strictest required cutoff. Infeasible budgets are reported, not hidden.
    """
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels)
    if scores.ndim != 1 or labels.shape != scores.shape or len(scores) == 0:
        raise ValueError("Expected matched one-dimensional scores and labels")
    if not np.isfinite(scores).all() or not np.isin(labels,[0,1]).all():
        raise ValueError("Expected finite scores and binary labels")
    negatives = np.sort(scores[labels == 0])
    positives = scores[labels == 1]
    if not len(negatives) or not len(positives):
        raise ValueError("Both classes required in validation")
    if not (0 < max_fpr < 1):
        raise ValueError("max_fpr must lie strictly between 0 and 1")
    # Explicit above-max option means no alerts at all; essential for low budgets.
    candidates = np.unique(np.concatenate((scores, [np.nextafter(scores.max(), np.inf)])))
    fp = len(negatives) - np.searchsorted(negatives, candidates, side="left")
    upper = wilson_upper(fp, len(negatives), confidence=confidence)
    valid = np.flatnonzero(upper <= max_fpr)
    if not len(valid):
        return {"threshold": None, "feasible": False, "reason": "No cutoff meets upper confidence bound",
                "validation_negatives": int(len(negatives))}
    # Lowest admissible threshold maximizes recall (non-increasing with cutoff).
    i = int(valid[0])
    cutoff = float(candidates[i])
    tp = int(np.count_nonzero(positives >= cutoff))
    return {"threshold": cutoff, "feasible": True, "validation_fpr": float(fp[i]/len(negatives)),
            "validation_fpr_upper": float(upper[i]), "validation_recall": float(tp/len(positives)),
            "validation_negatives": int(len(negatives)), "validation_positives": int(len(positives)),
            "fpr_budget": max_fpr, "confidence": confidence}


def evaluate(y, scores, threshold):
    pred = np.asarray(scores) >= threshold
    tn, fp, fn, tp = map(int, confusion_matrix(y, pred, labels=[0,1]).ravel())
    return {"n": int(len(y)), "f1": float(f1_score(y, pred, zero_division=0)),
            "precision": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)),
            "fpr": float(fp/(fp+tn)) if fp+tn else None,
            "tn":tn,"fp":fp,"fn":fn,"tp":tp}


def run_study(train, test, max_fpr=.05, seed=42):
    x_train, x_test, preprocess, features = prepare(train, test)
    groups = row_hashes(x_train, features).to_numpy()
    splitter = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=seed)
    fit_idx, val_idx = next(splitter.split(x_train, train.label.to_numpy(), groups))
    fit_x, val_x = x_train.iloc[fit_idx], x_train.iloc[val_idx]
    fit_y, val_y = train.label.to_numpy()[fit_idx], train.label.to_numpy()[val_idx]
    test_y = test.label.to_numpy()
    if len(set(fit_y))!=2 or len(set(val_y))!=2:
        raise ValueError("Group-based split did not preserve both label classes")
    # Compare test predictor rows to ALL training rows, not only training fit subset.
    train_hashes = set(groups.tolist())
    unseen = ~row_hashes(x_test, features).isin(train_hashes).to_numpy()
    if not np.any(unseen):
        raise ValueError("All test rows overlap the training predictors")
    records = []
    for name, estimator in models().items():
        pipeline = Pipeline([("preprocess",clone(preprocess)), ("model",clone(estimator))])
        pipeline.fit(fit_x, fit_y)
        val_scores = pipeline.predict_proba(val_x)[:,1]
        policy = choose_threshold(val_scores, val_y, max_fpr=max_fpr)
        for choice, threshold in (("default", .5), ("validation_constrained", policy["threshold"])):
            if threshold is None:
                records.append({"model":name,"policy":choice,"status":"infeasible_on_validation","validation":policy})
                continue
            test_scores = pipeline.predict_proba(x_test)[:,1]
            records.append({"model":name, "policy":choice,"status":"evaluated",
                            "threshold":float(threshold),"validation":policy if choice=="validation_constrained" else None,
                            "official_test":evaluate(test_y,test_scores,threshold),
                            "nonoverlap_test":evaluate(test_y[unseen],test_scores[unseen],threshold)})
    return {"question":"Does training-only constrained FPR transfer to official and non-overlap test records?",
            "seed": seed,"fpr_budget":max_fpr,
            "fit_rows":int(len(fit_idx)),"validation_rows":int(len(val_idx)),
            "test_rows":int(len(test)),"nonoverlap_rows":int(unseen.sum()),
            "overlap_rows":int((~unseen).sum()),"features":features,
            "caveats":["Fingerprint matching is not proof of semantic record identity.",
                       "GroupShuffleSplit is not a time- or network-group shift.",
                       "Official test performance is exploratory after previous test analyses.",
                       "A validation FPR constraint is not guaranteed to transfer to shifted test data.",
                       "Results are offline historical benchmark data, not live IDS proof."],
            "results":records}


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--train",type=Path,default=Path("data/UNSW_NB15_training-set.csv"))
    p.add_argument("--test",type=Path,default=Path("data/UNSW_NB15_testing-set.csv"))
    p.add_argument("--output",type=Path,default=Path("results/alert_budget_study.json"))
    p.add_argument("--max-fpr",type=float,default=.05)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--exploratory",action="store_true")
    args=p.parse_args(argv)
    train,test=load_dataset(args.train),load_dataset(args.test)
    if not args.exploratory and (len(train)!=OFFICIAL_ROWS["train"] or len(test)!=OFFICIAL_ROWS["test"]):
        p.error("Split sizes differ from official benchmark; pass --exploratory to acknowledge alternative data")
    output=run_study(train,test,max_fpr=args.max_fpr,seed=args.seed)
    output["mode"]="EXPLORATORY" if args.exploratory else "OFFICIAL_SPLIT_EXPLORATORY_ANALYSIS"
    output["train_sha256"]=sha256(args.train)
    output["test_sha256"]=sha256(args.test)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("Wrote",args.output)

if __name__=="__main__":
    main()
