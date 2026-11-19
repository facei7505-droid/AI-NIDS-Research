"""Produce derived, verified reports for the executed 3-policy donor experiment."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from statistics import mean

POLICIES=("global","observable_strata","same_class_oracle")

def summarize(source):
    if source.get("status")!="TRAINING_ONLY_POST_HOC_OBSERVABLE_DONOR_CONTROL":
        raise ValueError("Input must contain executed 3-policy study")
    idx={}
    for row in source["rows"]:
        key=(row["split_seed"],row["donor_seed"],row["model"],row["policy"])
        if key in idx or row["policy"] not in POLICIES:
            raise ValueError("Duplicated or unrecognized study condition")
        for group in ("protocol","context"):
            if not 0<=row["joint_group_exchange_rate"][group]<=1:
                raise ValueError("Invalid exchange rate")
        idx[key]=row
    models=sorted({r["model"] for r in source["rows"]})
    splits=source["split_seeds"]
    seeds=source["donor_seeds"]
    if len(idx)!=len(models)*len(splits)*len(seeds)*len(POLICIES):
        raise ValueError("Missing study condition")
    aggregates=[]
    comparisons=[]
    for model in models:
        for policy in POLICIES:
            subset=[idx[(split,seed,model,policy)] for split in splits for seed in seeds]
            aggregates.append({
                "model":model,"policy":policy,"conditions":len(subset),
                "mean_excess_fpr_pp":mean(r["excess_fpr_pp"] for r in subset),
                "mean_joint_fpr":mean(r["joint_fpr"] for r in subset),
                "mean_joint_recall":mean(r["joint_recall"] for r in subset),
                "mean_exchange_protocol":mean(r["joint_group_exchange_rate"]["protocol"] for r in subset),
                "mean_exchange_context":mean(r["joint_group_exchange_rate"]["context"] for r in subset),
            })
        for split in splits:
            paired=[]
            for seed in seeds:
                g=idx[(split,seed,model,"global")]
                o=idx[(split,seed,model,"observable_strata")]
                oracle=idx[(split,seed,model,"same_class_oracle")]
                paired.append({
                    "permutation_seed":seed,
                    "global_minus_observable_pp":g["excess_fpr_pp"]-o["excess_fpr_pp"],
                    "observable_minus_oracle_pp":o["excess_fpr_pp"]-oracle["excess_fpr_pp"],
                })
            comparisons.append({
                "model":model,"split_seed":split,"permutation_contrasts":paired,
                "mean_global_minus_observable_pp":mean(r["global_minus_observable_pp"] for r in paired),
                "mean_observable_minus_oracle_pp":mean(r["observable_minus_oracle_pp"] for r in paired),
            })
    return {
        "status":"EXECUTED_POST_HOC_DONOR_POLICY_ANALYSIS",
        "train_sha256":source["train_sha256"],
        "split_seeds":splits,
        "donor_seeds":seeds,
        "aggregates":aggregates,
        "paired_comparisons":comparisons,
        "limitations":[
            "All data are from the official historical training split; overlapping splits do not provide independent population replicates.",
            "Class-matched donor sampling uses true labels as an offline oracle control only, and must not be used as a deployed detector.",
            "Observable strata are computed on validation features (transductive); grouping on duration and bytes does not guarantee physically consistent flows.",
            "Exchange frequency is not an exhaustive measure of distributional perturbation severity.",
            "Protocol/Context pairing and these policy choices are exploratory follow-ups; independent precommitted external replication is still missing.",
        ]
    }


def render(data):
    lines=["# Observable-donor three-policy control — executed results", "",
           "**Historical UNSW-NB15 training-only experiment; exploratory, not independently validated.**", "",
           f"Train file SHA-256: `{data['train_sha256']}`", "",
           "| Model | Donor policy | Excess FPR (pp) | Joint FPR | Joint recall | Protocol exchanged | Context exchanged |",
           "|---|---|---:|---:|---:|---:|---:|"]
    for r in data["aggregates"]:
        lines.append(f"| {r['model']} | {r['policy']} | {r['mean_excess_fpr_pp']:+.3f} | "
                     f"{r['mean_joint_fpr']*100:.2f}% | {r['mean_joint_recall']*100:.2f}% | "
                     f"{r['mean_exchange_protocol']*100:.2f}% | {r['mean_exchange_context']*100:.2f}% |")
    lines+=["","## Paired comparisons by training-only validation split","",
            "| Model | Split | Global − observable (pp) | Observable − oracle (pp) |",
            "|---|---:|---:|---:|"]
    for r in data["paired_comparisons"]:
        lines.append(f"| {r['model']} | {r['split_seed']} | "
                     f"{r['mean_global_minus_observable_pp']:+.3f} | "
                     f"{r['mean_observable_minus_oracle_pp']:+.3f} |")
    lines+=["","## Limits of interpretation",""]
    lines.extend("- "+line for line in data["limitations"])
    lines+=["","This diagnostic quantifies the donor-policy sensitivity of measured NIDS feature interactions, **not** a new algorithm, real-world shift, external validation, or causal explanation.",""]
    return "\n".join(lines)


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/observable_donor_control.json"))
    p.add_argument("--json",type=Path,default=Path("results/observable_donor_analysis.json"))
    p.add_argument("--report",type=Path,default=Path("results/OBSERVABLE_DONOR_REPORT.md"))
    a=p.parse_args(argv)
    evidence=summarize(json.loads(a.input.read_text(encoding="utf-8")))
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    a.report.write_text(render(evidence),encoding="utf-8")

if __name__=="__main__":
    main()
