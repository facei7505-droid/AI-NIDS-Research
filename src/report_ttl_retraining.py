"""Summarize *executed* matched TTL retraining ablation without inventing effects.

Subtraction is matched by split seed and estimator, not by distinct test rows.
These are post-hoc exploratory contrasts, not causal or independent validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, stdev


def compare(study: dict) -> list[dict]:
    if study.get("status") != "TRAIN_ONLY_POST_HOC_RETRAINED_TTL_ABLATION":
        raise ValueError("Expected executed matched TTL retraining study")
    expected = len(study["split_seeds"]) * 2 * 2
    items = study.get("effect_summaries", [])
    if len(items) != expected:
        raise ValueError(f"Incomplete effect summaries: {len(items)} of {expected}")
    index = {}
    for item in items:
        key = (item["split_seed"], item["model"], item["training_design"])
        if key in index:
            raise ValueError(f"Duplicate ablation record: {key}")
        index[key] = item
    rows = []
    models = sorted({r["model"] for r in items})
    for model in models:
        diffs = []
        fpr_clean_diffs = []
        for seed in study["split_seeds"]:
            full = index[(seed, model, "full")]
            ablated = index[(seed, model, "no_ttl")]
            diffs.append(full["excess_interaction_fpr_pp"]-ablated["excess_interaction_fpr_pp"])
            fpr_clean_diffs.append(100*(full["clean_fpr"]-ablated["clean_fpr"]))
        rows.append({
            "model": model,
            "split_seeds": list(study["split_seeds"]),
            "difference_in_excess_interaction_pp_per_seed": diffs,
            "mean_difference_in_excess_interaction_pp": mean(diffs),
            "sd_difference_in_excess_interaction_pp": stdev(diffs) if len(diffs)>1 else None,
            "clean_fpr_difference_pp_per_seed": fpr_clean_diffs,
            "mean_clean_fpr_difference_pp": mean(fpr_clean_diffs),
            "sign_consistent": all(v>0 for v in diffs) or all(v<0 for v in diffs),
        })
    return rows


def render(study: dict, rows: list[dict]) -> str:
    lines = [
        "# Matched TTL retraining ablation — executed exploratory findings",
        "",
        "**Post-hoc on the UNSW-NB15 training split only. Not an independent confirmation.**",
        "",
        f"Input training SHA-256: `{study.get('train_sha256', 'missing')}`.",
        f"Split seeds: `{study['split_seeds']}`, shared permutation seed: `{study['permutation_seed']}`.",
        "",
        "| Model | Excess pair interaction: full minus no-TTL (mean pp) | Clean FPR: full minus no-TTL (mean pp) | Same effect sign all splits? |",
        "|---|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['model']} | {r['mean_difference_in_excess_interaction_pp']:+.3f} | "
            f"{r['mean_clean_fpr_difference_pp']:+.3f} | "
            f"{'Yes' if r['sign_consistent'] else 'No'} |"
        )
    lines += [
        "",
        "## What the comparison establishes",
        "",
        "Models were **retrained** using full or TTL-removed predictor sets on identical",
        "group-held-out training/validation split indices. Positive interaction contrast",
        "means the original full-feature model had a larger nonadditive pair effect than",
        "the TTL-removed model under this synthetic experimental procedure.",
        "",
        "## What it does not establish",
        "",
        "- Excluding TTL features changes model fitting and is not a causal intervention on real traffic.",
        "- These split seeds share the same source data and are not independent populations.",
        "- The joint row permutations can generate physically unrealistic cross-feature combinations.",
        "- This was designed after the relevant feature pair was identified; selection bias matters.",
        "- No verified first-in-world novelty, external deployment quality or guarantee of low false alarms.",
        "",
        "Use `results/ttl_retraining_ablation.json` for all individual model/split metrics and raw contrasts.",
    ]
    return "\n".join(lines)+"\n"


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/ttl_retraining_ablation.json"))
    p.add_argument("--output", type=Path, default=Path("results/TTL_RETRAINING_REPORT.md"))
    args=p.parse_args(argv)
    study=json.loads(args.input.read_text(encoding="utf-8"))
    report=render(study, compare(study))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(args.output)


if __name__=="__main__":
    main()
