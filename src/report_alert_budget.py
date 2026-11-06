"""Generate a factual, reproducible Markdown research note from executed JSON.

No fixed scores, conclusions, or flattering performance claims are embedded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def format_pct(n):
    return "N/A" if n is None else f"{100*n:.2f}%"


def render(result: dict) -> str:
    lines = [
        "# False-alarm-budget transfer: executed exploratory analysis",
        "",
        "**Exploratory:** the original UNSW-NB15 designated test split was inspected before",
        "this experiment was designed. These data do not support a preregistered",
        "confirmatory claim or proof of novelty.",
        "",
        f"- FPR budget targeted on grouped training validation: **{format_pct(result['fpr_budget'])}**",
        f"- Training-fit records: **{result['fit_rows']:,}**",
        f"- Training-validation records: **{result['validation_rows']:,}**",
        f"- Official test records: **{result['test_rows']:,}**",
        f"- Test rows matching training predictor fingerprints: **{result['overlap_rows']:,}**",
        f"- Unmatched test rows: **{result['nonoverlap_rows']:,}**",
        f"- Training input SHA-256: `{result['train_sha256']}`",
        f"- Test input SHA-256: `{result['test_sha256']}`",
        "",
        "## Frozen evaluation results",
        "",
        "| Model | Cutoff policy | Validation FPR upper | Test FPR | Test recall | Test F1 | Non-overlap FPR | Non-overlap recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in result["results"]:
        p = item["policy"]
        name = item["model"]
        if item["status"] != "evaluated":
            lines.append(f"| {name} | {p} (infeasible) | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        val = item["validation"]
        official = item["official_test"]
        distinct = item["nonoverlap_test"]
        bound = format_pct(val["validation_fpr_upper"]) if val is not None else "N/A"
        lines.append(f"| {name} | {p} | {bound} | "
                     f"{format_pct(official['fpr'])} | {format_pct(official['recall'])} | "
                     f"{format_pct(official['f1'])} | {format_pct(distinct['fpr'])} | "
                     f"{format_pct(distinct['recall'])} |")
    lines += [
        "",
        "## Interpretation guide",
        "",
        "- A validation budget is not a guaranteed upper bound on test FPR; directly inspect measured differences.",
        "- Observe absolute changes in recall, not just reductions in FPR.",
        "- The unmatched subset can differ systematically from the complete test distribution; it is not an independent random sample.",
        "- A majority-class classifier is a negative control, not a useful operational detector.",
        "- The study does not establish effectiveness on live networks, novel attack types, or independent external datasets.",
        "",
        "## Constraints and limitations",
        "",
    ]
    lines.extend("- " + str(c) for c in result["caveats"])
    lines.extend(["", "**Scientific novelty has not been established.** Review published literature and validate on an untouched external dataset before claiming an original contribution.", ""])
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/alert_budget_study.json"))
    p.add_argument("--output", type=Path, default=Path("results/ALERT_BUDGET_REPORT.md"))
    args = p.parse_args()
    study = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(study), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
