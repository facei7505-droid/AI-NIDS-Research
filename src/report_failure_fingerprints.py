"""Write descriptive tables for executed Failure Fingerprints diagnostics.

No precomputed measurements: all values come from generated experiment JSON.
Seed replicates reflect split variability, not independent dataset replication.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def summarize(study):
    if study.get("status") != "TRAINING_ONLY_EXPLORATORY_SYNTHETIC_DIAGNOSTIC":
        raise ValueError("Only executed training-only study files are accepted")
    rows = pd.DataFrame(study["rows"])
    interactions = pd.DataFrame(study["interactions"])
    expected = {"seed", "model", "condition", "fpr", "recall"}
    if rows.empty or not expected.issubset(rows):
        raise ValueError("Missing evaluated rows")
    clean = rows[rows["condition"] == "clean"][["seed", "model", "fpr", "recall"]].rename(
        columns={"fpr": "clean_fpr", "recall": "clean_recall"}
    )
    compared = rows.merge(clean, on=["seed", "model"], validate="many_to_one")
    compared["fpr_increase_pp"] = 100 * (compared["fpr"] - compared["clean_fpr"])
    compared["recall_loss_pp"] = 100 * (compared["clean_recall"] - compared["recall"])
    effects = compared.groupby(["model", "condition"], as_index=False).agg(
        mean_fpr_increase_pp=("fpr_increase_pp", "mean"),
        sd_fpr_increase_pp=("fpr_increase_pp", "std"),
        mean_recall_loss_pp=("recall_loss_pp", "mean"),
        sd_recall_loss_pp=("recall_loss_pp", "std"),
        repeats=("seed", "nunique"),
    )
    interaction_summary = interactions.groupby(["model", "pair"], as_index=False).agg(
        mean_excess_fpr_pp=("excess_fpr_pp", "mean"),
        sd_excess_fpr_pp=("excess_fpr_pp", "std"),
        mean_excess_recall_loss_pp=("excess_recall_loss_pp", "mean"),
        repeats=("seed", "nunique"),
    )
    return effects, interaction_summary


def render(study, effects, interactions):
    lines = [
        "# Failure Fingerprints: training-only exploratory results",
        "",
        "**No official test data were used in this experiment.** The same",
        "official training dataset is repeatedly split, so seeds are not",
        "independent populations. Results do not establish novel scientific discovery.",
        "",
        f"- Input SHA-256: `{study.get('train_sha256','not provided')}`",
        f"- Grouped validation seeds: `{study['split_seeds']}`",
        f"- Perturbed-row probability: `{study['fraction']}`",
        "",
        "## Mean changes relative to clean validation (percentage points)",
        "",
        "```",
        effects.round(3).to_string(index=False),
        "```",
        "",
        "## Pairwise excess changes (joint effect minus sum of single-group changes)",
        "",
        "```",
        interactions.round(3).to_string(index=False),
        "```",
        "",
        "A positive excess FPR indicates the joint perturbation raised false alarms",
        "more than the sum of the two separate perturbation effects.",
        "Negative excess FPR shows subadditivity. Signs must not be confused",
        "with causality, statistical significance or robustness to real-world shifts.",
        "",
        "## Interpretation limitations",
        "",
    ]
    lines.extend("- " + warning for warning in study["notes"])
    lines.extend([
        "- The fixed score cutoff of 0.5 and the synthetic transformation design can affect conclusions.",
        "- Multiple group pairs, seeds, and models are evaluated; do not select only flattering results.",
        "- Repeated validation splits share many training events and therefore do not form independent samples.",
        "- Requires external data, stronger uncertainty analysis and literature comparison before novelty claims.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/failure_fingerprints.json"))
    parser.add_argument("--output", type=Path, default=Path("results/FAILURE_FINGERPRINTS_REPORT.md"))
    args = parser.parse_args()
    study = json.loads(args.input.read_text(encoding="utf-8"))
    effects, interactions = summarize(study)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(study, effects, interactions), encoding="utf-8")
    print(f"Published {len(effects)} model/condition summaries, {len(interactions)} pair summaries")


if __name__ == "__main__":
    main()
