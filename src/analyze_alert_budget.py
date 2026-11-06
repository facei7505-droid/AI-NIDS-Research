"""Quantify validation-to-test transfer of an offline FPR budget.

Conservative descriptive uncertainty only. Wilson intervals assume independent
Bernoulli observations; network-flow dependence and shift violate that ideal.
"""
from __future__ import annotations

import argparse
import json
from math import sqrt
from pathlib import Path
from statistics import NormalDist


def wilson_interval(successes: int, total: int, confidence: float = .95):
    if not isinstance(total, int) or not isinstance(successes, int) or total <= 0 or not 0 <= successes <= total:
        raise ValueError("Valid nonempty binomial counts required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = successes / total
    d = 1 + z*z / total
    center = (p + z*z/(2*total)) / d
    radius = z*sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return max(0.,center-radius), min(1.,center+radius)


def analyze(study: dict) -> dict:
    if "results" not in study or not 0 < study["fpr_budget"] < 1:
        raise ValueError("Study must include results and a valid FPR budget")
    entries = []
    by_model = {}
    for item in study["results"]:
        if item["status"] == "evaluated":
            by_model.setdefault(item["model"], {})[item["policy"]] = item
    for name, choices in by_model.items():
        if "default" not in choices or "validation_constrained" not in choices:
            continue
        base = choices["default"]
        tuned = choices["validation_constrained"]
        policy = tuned["validation"]
        for sample_name in ("official_test", "nonoverlap_test"):
            original = base[sample_name]
            revised = tuned[sample_name]
            denominator = revised["tn"] + revised["fp"]
            ci = wilson_interval(int(revised["fp"]), int(denominator))
            entries.append({
                "model": name,
                "subset": sample_name,
                "threshold": tuned["threshold"],
                "validation_fpr": policy["validation_fpr"],
                "validation_fpr_upper_one_sided": policy["validation_fpr_upper"],
                "default_fpr": original["fpr"],
                "constrained_fpr": revised["fpr"],
                "fpr_reduction_pp": 100*(original["fpr"]-revised["fpr"]),
                "constrained_test_fpr_95pct_wilson": [ci[0],ci[1]],
                "budget_violated": revised["fpr"] > study["fpr_budget"],
                "budget_overshoot_pp": 100*(revised["fpr"]-study["fpr_budget"]),
                "default_recall": original["recall"],
                "constrained_recall": revised["recall"],
                "recall_cost_pp": 100*(original["recall"]-revised["recall"]),
                "false_alarms_prevented": original["fp"]-revised["fp"],
                "additional_attacks_missed": revised["fn"]-original["fn"],
                "normal_rows": denominator,
                "attack_rows": revised["tp"]+revised["fn"],
            })
    return {
        "mode": "DESCRIPTIVE_POST_HOC_ANALYSIS",
        "fpr_budget": study["fpr_budget"],
        "train_sha256": study.get("train_sha256"),
        "test_sha256": study.get("test_sha256"),
        "findings": entries,
        "caution": [
            "The validation budget is not guaranteed under test distribution shift.",
            "Wilson intervals are descriptive under iid row assumptions; correlated network flows can make them too narrow.",
            "Comparisons use a previously inspected test split and are exploratory, not confirmatory.",
            "The nonoverlap subset is selected by train-match status and is not a random external sample.",
            "No assertion of new algorithm, novelty, live deployment performance, or guaranteed future FPR."
        ]
    }


def pct(value):
    return f"{100*value:.2f}%"


def render(result: dict) -> str:
    out = [
        "# False-positive-budget transfer: descriptive findings",
        "",
        "**Executed exploratory analysis, not peer-reviewed or externally validated.**",
        "",
        f"Training-validation target FPR: **{pct(result['fpr_budget'])}**.",
        "",
        "| Model | Subset | Default FPR | Constrained FPR | FPR overshoot vs 5% | Constrained Recall | Recall cost | False alarms avoided | Extra missed attacks |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for f in result["findings"]:
        out.append(f"| {f['model']} | {f['subset']} | {pct(f['default_fpr'])} | "
                   f"{pct(f['constrained_fpr'])} | {f['budget_overshoot_pp']:+.2f} pp | "
                   f"{pct(f['constrained_recall'])} | {f['recall_cost_pp']:+.2f} pp | "
                   f"{f['false_alarms_prevented']:,} | {f['additional_attacks_missed']:,} |")
    out += ["", "## FPR confidence intervals (descriptive)", "",
            "Two-sided 95% Wilson intervals computed from benign-row false positives/true negatives. "
            "They **do not** correct for dependence, covariate shift, test reuse or post-hoc analysis.", ""]
    for f in result["findings"]:
        lo,hi = f["constrained_test_fpr_95pct_wilson"]
        out.append(f"- {f['model']}, {f['subset']}: FPR {pct(f['constrained_fpr'])}, "
                   f"95% Wilson [{pct(lo)}, {pct(hi)}], benign rows n={f['normal_rows']:,}.")
    out += ["", "## Interpretation", "",
            "The conservative validation-only thresholds reduce false alarms, but the recorded test FPR "
            "must be checked against the prespecified budget. A reduction in FPR can incur additional missed attacks.",
            "No positive novelty or real-world transfer claim follows without independent comparison and untouched external data.",
            "", "## Limitations", ""]
    out.extend("- "+c for c in result["caution"])
    return "\n".join(out)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("results/alert_budget_study.json"))
    parser.add_argument("--json-output",type=Path,default=Path("results/alert_budget_analysis.json"))
    parser.add_argument("--report",type=Path,default=Path("results/ALERT_BUDGET_ANALYSIS.md"))
    a=parser.parse_args()
    result=analyze(json.loads(a.input.read_text(encoding="utf-8")))
    a.json_output.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.json_output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    a.report.write_text(render(result),encoding="utf-8")


if __name__ == "__main__":
    main()
