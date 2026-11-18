"""Permutation-seed replication and donor-policy falsification for NIDS.

Training-only grouped validation, no official test inspection. The protocol
was designed after inspecting the initial Failure Fingerprints result and is
explicitly exploratory. Ground-truth labels used for donor assignment are
valid ONLY for an offline diagnostic, not deployed inference.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from class_mixing_control import PAIR, permute_blocks
from data_audit import row_hashes
from failure_fingerprints import metrics
from run_experiments import load_dataset, models, prepare, sha256


def run(train, *, split_seeds=(13,29,47), permutation_seeds=(101,211,307,401,503),
        fraction=.25):
    if len(split_seeds)<2 or len(permutation_seeds)<3 or not 0<fraction<=1:
        raise ValueError("At least 2 splits, 3 permutation seeds, valid fraction needed")
    if len(set(split_seeds))!=len(split_seeds) or len(set(permutation_seeds))!=len(permutation_seeds):
        raise ValueError("Random seeds must not be repeated")
    x,_,preprocess,features=prepare(train,train)
    if not set(sum((list(x) for x in PAIR.values()),[])).issubset(features):
        raise ValueError("Required group features not found")
    y=train.label.to_numpy()
    fingerprint=row_hashes(x,features).to_numpy()
    entries=[]
    for split_seed in split_seeds:
        fit,val=next(GroupShuffleSplit(n_splits=1,test_size=.2,
                    random_state=int(split_seed)).split(x,y,fingerprint))
        if set(y[fit])!={0,1} or set(y[val])!={0,1}:
            raise ValueError("Both labels must be present")
        val_x,val_y=x.iloc[val],y[val]
        for model_name,estimator in models().items():
            if model_name=="Majority Dummy":
                continue
            fitted=Pipeline([("preprocess",clone(preprocess)),("model",clone(estimator))])
            fitted.fit(x.iloc[fit],y[fit])
            clean=metrics(val_y,fitted.predict(val_x))
            for perm_seed in permutation_seeds:
                for donor_policy in ("global","within_class"):
                    scores={}
                    for name,selected in (
                        ("protocol",("protocol",)),
                        ("context",("context",)),
                        ("protocol+context",("protocol","context")),
                    ):
                        sample=permute_blocks(val_x,val_y,selected=selected,
                            mode=donor_policy,seed=int(perm_seed),fraction=fraction)
                        scores[name]=metrics(val_y,fitted.predict(sample))
                    p,c,j=scores["protocol"],scores["context"],scores["protocol+context"]
                    excess=100*(j["fpr"]-p["fpr"]-c["fpr"]+clean["fpr"])
                    entries.append({
                        "split_seed":int(split_seed),"permutation_seed":int(perm_seed),
                        "model":model_name,"donor_policy":donor_policy,
                        "validation_rows":int(len(val)),"clean_fpr":clean["fpr"],
                        "single_protocol_fpr":p["fpr"],"single_context_fpr":c["fpr"],
                        "joint_fpr":j["fpr"],"joint_recall":j["recall"],
                        "excess_fpr_pp":float(excess),
                    })
    return {
        "status":"EXPLORATORY_TRAIN_ONLY_PERMUTATION_SEED_REPLICATION",
        "split_seeds":list(map(int,split_seeds)),
        "permutation_seeds":list(map(int,permutation_seeds)),
        "fraction":float(fraction),"rows":entries,
        "limitations":[
            "Protocol and Context were selected post-hoc after previous results.",
            "All folds reuse UNSW-NB15 training data; permutation seeds are not independent populations.",
            "Within-class donor sampling uses ground-truth labels solely for offline falsification.",
            "Neither policy enforces network flow physical plausibility.",
            "Do not claim external generalization or first-in-world novelty from this experiment."
        ],
    }


def summarize(result):
    rows=result["rows"]
    index={(r["split_seed"],r["permutation_seed"],r["model"],r["donor_policy"]):r
           for r in rows}
    if len(index)!=len(rows):
        raise ValueError("Duplicate conditions")
    summary=[]
    for model in sorted({r["model"] for r in rows}):
        for split in result["split_seeds"]:
            global_vals=[]
            class_vals=[]
            for seed in result["permutation_seeds"]:
                global_vals.append(index[(split,seed,model,"global")]["excess_fpr_pp"])
                class_vals.append(index[(split,seed,model,"within_class")]["excess_fpr_pp"])
            diffs=np.asarray(global_vals)-np.asarray(class_vals)
            summary.append({
                "model":model,"split_seed":split,
                "global_excess_fpr_pp":global_vals,
                "within_class_excess_fpr_pp":class_vals,
                "mean_global_excess_fpr_pp":float(np.mean(global_vals)),
                "mean_within_class_excess_fpr_pp":float(np.mean(class_vals)),
                "mean_paired_policy_difference_pp":float(np.mean(diffs)),
                "sd_paired_policy_difference_pp":float(np.std(diffs,ddof=1)),
                "positive_paired_difference_fraction":float(np.mean(diffs>0)),
            })
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--train",type=Path,default=Path("data/UNSW_NB15_training-set.csv"))
    p.add_argument("--output",type=Path,default=Path("results/permutation_seed_replication.json"))
    args=p.parse_args()
    data=load_dataset(args.train)
    if len(data)!=175341:
        p.error("Expected pinned official training split, 175341 rows")
    output=run(data)
    output["train_sha256"]=sha256(args.train)
    output["summaries"]=summarize(output)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf8")
    print(len(output["rows"]),"permutation-policy records written")


if __name__=="__main__":
    main()
