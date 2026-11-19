"""Compare label-blind matching boundaries with strictly paired study settings.

Original study: strata bin edges from validation covariates (transductive).
New study: edges and medians fit only from training covariates.
Both are exploratory studies on overlapping UNSW-NB15 train-only splits.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from statistics import mean

def compare(original, frozen):
    if original.get("status")!="TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL":
        raise ValueError("Original observable donor evidence missing or wrong status")
    if frozen.get("status")!="POST_HOC_TRAIN_FITTED_OBSERVABLE_STRATA":
        raise ValueError("Frozen donor evidence missing or wrong status")
    if original.get("train_sha256")!=frozen.get("train_sha256"):
        raise ValueError("Inputs differ: data SHA256 mismatch")
    if original.get("split_seeds")!=frozen.get("split_seeds") or original.get("donor_seeds")!=frozen.get("donor_seeds"):
        raise ValueError("Unmatched split/permutation seed protocol")
    if original.get("fraction")!=frozen.get("fraction"):
        raise ValueError("Unmatched perturbation dose")
    keys=("split_seed","donor_seed","model","policy")
    def make_index(rows):
        result={}
        for r in rows:
            k=tuple(r[x] for x in keys)
            if k in result:
                raise ValueError(f"Duplicate experimental cell: {k}")
            result[k]=r
        return result
    old=make_index(original["rows"])
    new=make_index(frozen["rows"])
    if not old or set(old)!=set(new):
        raise ValueError("Factorial cells do not match; cannot compare")
    records=[]
    for k in sorted(old):
        a=old[k]
        b=new[k]
        records.append({
            **dict(zip(keys,k)),
            "old_excess_fpr_pp":a["excess_fpr_pp"],
            "frozen_excess_fpr_pp":b["excess_fpr_pp"],
            "frozen_minus_old_pp":b["excess_fpr_pp"]-a["excess_fpr_pp"],
            "old_joint_fpr":a["joint_fpr"],
            "frozen_joint_fpr":b["joint_fpr"],
            "old_joint_recall":a["joint_recall"],
            "frozen_joint_recall":b["joint_recall"],
        })
    models=sorted({r["model"] for r in records})
    policies=sorted({r["policy"] for r in records})
    totals=[]
    for model in models:
        for policy in policies:
            cells=[r for r in records if r["model"]==model and r["policy"]==policy]
            totals.append({
                "model":model,"policy":policy,
                "n_paired_cells":len(cells),
                "mean_frozen_minus_old_excess_fpr_pp":mean(x["frozen_minus_old_pp"] for x in cells),
                "mean_old_excess_fpr_pp":mean(x["old_excess_fpr_pp"] for x in cells),
                "mean_frozen_excess_fpr_pp":mean(x["frozen_excess_fpr_pp"] for x in cells),
                "mean_frozen_minus_old_joint_fpr_pp":100*mean(x["frozen_joint_fpr"]-x["old_joint_fpr"] for x in cells),
                "mean_frozen_minus_old_joint_recall_pp":100*mean(x["frozen_joint_recall"]-x["old_joint_recall"] for x in cells),
            })
    return {
        "status":"POST_HOC_PAIRED_FROZEN_QUANTILE_COMPARISON",
        "train_sha256":original["train_sha256"],
        "n_paired_conditions":len(records),
        "comparisons":records,
        "summary":totals,
        "limits":[
            "A training-fitted quantile rule is less transductive than a validation-fit rule, but group donors are still chosen from held-out validation features.",
            "Even where results differ, the changed bin edges affect synthetic donor selection; this does not prove causal network behavior.",
            "This is one historical corpus with overlapping held-out training splits, not independent external replication.",
            "Same-class label-oracle donors are diagnostic only and cannot be used for inference.",
            "Protocol/Context interaction and the comparison were selected after earlier exploratory observations."
        ],
    }

def report(comparison):
    lines=["# Frozen vs validation-fitted donor quantiles: executed paired comparison",
           "",
           "**Exploratory training-only matched-control analysis.**",
           "",
           f"Matched factorial cells: {comparison['n_paired_conditions']}.",
           f"Data SHA256: `{comparison['train_sha256']}`.",
           "",
           "| Model | Policy | Old excess FPR (pp) | Frozen excess FPR (pp) | Frozen − old (pp) | Paired cells |",
           "|---|---|---:|---:|---:|---:|"]
    for row in comparison["summary"]:
        lines.append(
            f"| {row['model']} | {row['policy']} | {row['mean_old_excess_fpr_pp']:+.3f} | "
            f"{row['mean_frozen_excess_fpr_pp']:+.3f} | "
            f"{row['mean_frozen_minus_old_excess_fpr_pp']:+.3f} | {row['n_paired_cells']} |")
    lines.extend(["","## Interpretive limitations",""])
    lines.extend("- "+x for x in comparison["limits"])
    return "\n".join(lines)+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--old",type=Path,default=Path("results/observable_donor_control.json"))
    parser.add_argument("--frozen",type=Path,default=Path("results/train_fitted_donor_control.json"))
    parser.add_argument("--json",type=Path,default=Path("results/donor_quantile_comparison.json"))
    parser.add_argument("--report",type=Path,default=Path("results/DONOR_QUANTILE_COMPARISON.md"))
    args=parser.parse_args()
    result=compare(json.loads(args.old.read_text()),json.loads(args.frozen.read_text()))
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    args.report.write_text(report(result),encoding="utf-8")

if __name__=="__main__":
    main()
