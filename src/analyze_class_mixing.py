"""Analyze executed class-mixing falsification evidence without re-running models.

Paired differences use the SAME validation split and fitted model across
permutation modes, not independent observation-level confidence intervals.
All results remain exploratory and specific to UNSW-NB15 training data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def validate_and_summarize(data):
    if data.get("status") != "TRAIN_ONLY_POST_HOC_CLASS_MIXING_CONTROL":
        raise ValueError("Wrong research protocol / missing executed evidence")
    seeds = data.get("split_seeds")
    if not isinstance(seeds, list) or len(seeds) < 2 or len(set(seeds)) != len(seeds):
        raise ValueError("At least 2 unique split seeds required")
    records = data.get("interactions")
    if not isinstance(records, list) or not records:
        raise ValueError("Interactions missing")
    models = sorted({item["model"] for item in records})
    if not models:
        raise ValueError("No evaluated model")
    if len(records) != len(seeds)*len(models)*2:
        raise ValueError("Study missing a mode/model/seed result")
    lookup = {}
    for item in records:
        k = (item["seed"], item["model"], item["mode"])
        if k in lookup:
            raise ValueError("Duplicate interaction record")
        if item["mode"] not in ("global", "within_class"):
            raise ValueError("Unknown perturbation mode")
        if not np.isfinite(item["excess_fpr_pp"]):
            raise ValueError("Non-finite excess FPR")
        lookup[k] = float(item["excess_fpr_pp"])
    output = []
    for model in models:
        global_effects, within_effects = [], []
        for seed in seeds:
            global_effects.append(lookup[(seed, model, "global")])
            within_effects.append(lookup[(seed, model, "within_class")])
        diff = np.asarray(global_effects) - np.asarray(within_effects)
        output.append({
            "model": model,
            "split_seeds": seeds,
            "global_excess_fpr_pp_by_seed": global_effects,
            "within_class_excess_fpr_pp_by_seed": within_effects,
            "paired_global_minus_within_class_pp_by_seed": diff.tolist(),
            "mean_global_excess_fpr_pp": float(np.mean(global_effects)),
            "mean_within_class_excess_fpr_pp": float(np.mean(within_effects)),
            "mean_paired_difference_pp": float(np.mean(diff)),
            "sd_paired_difference_pp": float(np.std(diff, ddof=1)),
            "paired_difference_positive_all_splits": bool(np.all(diff > 0)),
        })
    return {
        "status": "DESCRIPTIVE_POST_HOC_CLASS_MIXING_ANALYSIS",
        "data_sha256": data.get("train_sha256"),
        "n_models": len(models),
        "n_splits": len(seeds),
        "results": output,
        "limitations": [
            "Ground-truth class labels define the within-class permutation donor pool. This is an offline diagnostic, not an inference-time operation.",
            "The mean paired difference is not a formal inferential effect estimate across independent networks.",
            "The sample contains just three overlapping training-held-out splits; no independent dataset replication.",
            "Global permutation mixes labels and can generate physically inconsistent joint feature values.",
            "The Protocol+Context pairing was chosen after inspecting earlier effects: all findings are post-hoc exploratory.",
            "A shift in nonadditive excess FPR is not proof that class mixing is the unique cause of differences.",
        ],
    }


def render(result):
    out = [
        "# Class-mixing falsification control — executed, exploratory",
        "",
        "Source: `results/class_mixing_control.json` (official UNSW-NB15 **training split only**).",
        "",
        "| Model | Global excess FPR | Within-class excess FPR | Paired difference | Positive difference in every split? |",
        "|---|---:|---:|---:|---|",
    ]
    for r in result["results"]:
        out.append(
            f"| {r['model']} | {r['mean_global_excess_fpr_pp']:+.3f} pp | "
            f"{r['mean_within_class_excess_fpr_pp']:+.3f} pp | "
            f"{r['mean_paired_difference_pp']:+.3f} pp | "
            f"{'Yes' if r['paired_difference_positive_all_splits'] else 'No'} |"
        )
    out += [
        "",
        "## All paired differences (percentage points)",
        "",
    ]
    for r in result["results"]:
        out.append(
            f"- {r['model']}: " + ", ".join(
                f"seed {seed}: {diff:+.3f}"
                for seed, diff in zip(r["split_seeds"], r["paired_global_minus_within_class_pp_by_seed"])
            )
        )
    out += [
        "",
        "## How to interpret this",
        "",
        "A positive paired difference means **global cross-class permutation**",
        "produced more nonadditive false-alarm interaction than within-class",
        "permutation for the same model and training-held-out split.",
        "It suggests an evaluation-method artifact worth investigation.",
        "It does **not** demonstrate a new network mechanism or generalizable",
        "causal attribution.",
        "",
        "## Threats to validity",
        "",
    ]
    out.extend("- " + text for text in result["limitations"])
    out += [
        "",
        "This paper-worthy observation requires (1) repeat *perturbation* seeds,",
        "(2) physical or conditional consistency checks, (3) a strictly untouched",
        "external test corpus, and (4) review against conditional permutation",
        "and interaction-importance literature before a novelty claim.",
        "",
    ]
    return "\n".join(out)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/class_mixing_control.json"))
    p.add_argument("--json", type=Path, default=Path("results/class_mixing_analysis.json"))
    p.add_argument("--report", type=Path, default=Path("results/CLASS_MIXING_ANALYSIS.md"))
    args=p.parse_args()
    source=json.loads(args.input.read_text(encoding="utf-8"))
    analysis=validate_and_summarize(source)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(analysis, indent=2)+"\n",encoding="utf-8")
    args.report.write_text(render(analysis),encoding="utf-8")


if __name__ == "__main__":
    main()
