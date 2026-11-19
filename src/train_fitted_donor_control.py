"""Training-fitted, strictly label-blind donor strata for NIDS reliability.

This module fixes a crucial methodological weakness in the earlier
observable_donor_control study: quantile boundaries MUST be estimated on the
fitting subset only, then frozen for held-out validation. The oracle control
remains separate and may use labels solely as a retrospective benchmark.

No designated official UNSW-NB15 test data are ever read. This is post-hoc
synthetic diagnostic research, not a new IDS deployment algorithm.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from class_mixing_control import PAIR
from data_audit import row_hashes
from failure_fingerprints import metrics
from observable_donor_control import block_permutation
from run_experiments import load_dataset, models, prepare, sha256

MATCH = ("dur", "sbytes")
POLICIES = ("global", "observable_strata", "same_class_oracle")
CONDITIONS = {
    "protocol": ("protocol",),
    "context": ("context",),
    "protocol+context": ("protocol", "context"),
}


class FrozenQuantileStrata:
    """Learn matching-bin boundaries and missing-value medians on TRAIN only."""

    def __init__(self, columns=MATCH, bins=3):
        if int(bins) != bins or bins < 2:
            raise ValueError("bins must be integer >= 2")
        self.columns = tuple(columns)
        self.bins = int(bins)
        self.bounds = None
        self.medians = None

    def fit(self, frame):
        if any(c not in frame for c in self.columns):
            raise ValueError("Missing matching column")
        bounds, medians = {}, {}
        for col in self.columns:
            values = np.asarray(frame[col], dtype=float)
            finite = values[np.isfinite(values)]
            if len(finite) < 2:
                raise ValueError(f"Not enough training observations for {col}")
            median = float(np.median(finite))
            values = np.where(np.isfinite(values), values, median)
            bounds[col] = np.unique(np.quantile(values, np.linspace(0, 1, self.bins+1)[1:-1])).tolist()
            medians[col] = median
        self.bounds, self.medians = bounds, medians
        return self

    def transform(self, frame):
        if self.bounds is None or self.medians is None:
            raise ValueError("Must fit training boundaries first")
        codes = np.zeros(len(frame), dtype=np.int64)
        for col in self.columns:
            if col not in frame:
                raise ValueError(f"Missing matching column {col}")
            vals = np.asarray(frame[col], dtype=float)
            vals = np.where(np.isfinite(vals), vals, self.medians[col])
            codes = codes*self.bins + np.searchsorted(self.bounds[col], vals, side="right")
        return codes

    def export(self):
        if self.bounds is None:
            raise ValueError("Must fit before export")
        return {"columns":list(self.columns),"bins":self.bins,
                "boundaries":self.bounds,"train_medians":self.medians}


def run_experiment(training, *, split_seeds=(13,29,47), donor_seeds=(101,211,307), fraction=.25):
    if len(split_seeds)<2 or len(donor_seeds)<2 or not 0<fraction<=1:
        raise ValueError("Repeated nonempty seeds and valid fraction required")
    if len(set(split_seeds)) != len(split_seeds) or len(set(donor_seeds)) != len(donor_seeds):
        raise ValueError("Seed values must be distinct")
    x,_,preprocessor,features=prepare(training,training)
    required=set(MATCH)|set(PAIR["protocol"])|set(PAIR["context"])
    if not required.issubset(features):
        raise ValueError("Missing required features")
    labels=training.label.to_numpy()
    fingerprints=row_hashes(x,features).to_numpy()
    rows=[]
    split_info=[]
    for split_seed in split_seeds:
        fit_ids,val_ids=next(GroupShuffleSplit(n_splits=1,test_size=.2,
            random_state=int(split_seed)).split(x,labels,fingerprints))
        if set(labels[fit_ids])!={0,1} or set(labels[val_ids])!={0,1}:
            raise ValueError("Need both classes in fitting and validation")
        fit_x,val_x=x.iloc[fit_ids],x.iloc[val_ids]
        val_y=labels[val_ids]
        frozen=FrozenQuantileStrata().fit(fit_x)
        donor_strata=frozen.transform(val_x)
        split_info.append({
            "split_seed":int(split_seed),"fit_rows":len(fit_ids),
            "validation_rows":len(val_ids),"strata_parameters_fit_on":"training_rows_only",
            "strata":frozen.export(),
            "validation_stratum_counts":{str(k):int(v) for k,v in zip(*np.unique(donor_strata,return_counts=True))},
        })
        for model_name,estimator in models().items():
            if model_name=="Majority Dummy":
                continue
            model=Pipeline([("preprocess",clone(preprocessor)),("model",clone(estimator))])
            model.fit(fit_x,labels[fit_ids])
            clean=metrics(val_y,model.predict(val_x))
            for donor_seed in donor_seeds:
                for policy in POLICIES:
                    outcome={}
                    for condition,selected in CONDITIONS.items():
                        # The donor algorithm explicitly ignores labels for
                        # global and observable_strata; labels are used for
                        # scoring, and for same_class_oracle control ONLY.
                        shifted,detail=block_permutation(
                            val_x,val_y,selected,policy=policy,
                            fraction=fraction,seed=int(donor_seed),
                            strata=donor_strata,
                        )
                        outcome[condition]=(metrics(val_y,model.predict(shifted)),detail)
                    p,_=outcome["protocol"]
                    c,_=outcome["context"]
                    joint,exchanges=outcome["protocol+context"]
                    rows.append({
                        "split_seed":int(split_seed),"donor_seed":int(donor_seed),
                        "model":model_name,"policy":policy,
                        "clean_fpr":clean["fpr"],"joint_fpr":joint["fpr"],
                        "joint_recall":joint["recall"],
                        "excess_fpr_pp":100*(joint["fpr"]-p["fpr"]-c["fpr"]+clean["fpr"]),
                        "exchange_protocol":exchanges["protocol"]["exchange_rate"],
                        "exchange_context":exchanges["context"]["exchange_rate"],
                    })
    return {
        "status":"POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA",
        "split_seeds":list(map(int,split_seeds)),
        "donor_seeds":list(map(int,donor_seeds)),
        "fraction":fraction,"policies":list(POLICIES),
        "frozen_strata_parameters":split_info,
        "rows":rows,
        "limitations":[
            "This is a post-hoc diagnostic developed after inspecting donor-policy results.",
            "All experiments use UNSW-NB15 training records; no external dataset replication.",
            "Only source duration and byte counts define matching; semantically valid network-flow synthesis is not guaranteed.",
            "The same-class oracle may use ground-truth labels only as an offline methodological control.",
            "Validation labels are used in performance measurement, not to fit observable matching quantile boundaries.",
            "Models are trained on each split's fitting subset; successive splits are correlated, not independent populations."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--train",type=Path,default=Path("data/UNSW_NB15_training-set.csv"))
    p.add_argument("--output",type=Path,default=Path("results/train_fitted_donor_control.json"))
    args=p.parse_args()
    data=load_dataset(args.train)
    if len(data)!=175341:
        p.error("Official UNSW-NB15 training split requires 175341 rows")
    result=run_experiment(data)
    result["train_sha256"]=sha256(args.train)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Executed",len(result["rows"]),"training-fitted donor policy conditions")


if __name__ == "__main__":
    main()
