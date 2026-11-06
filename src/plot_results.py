"""Generate reproducible SVG figures from measured benchmark output CSV.

No image assets or invented values are bundled. Figures are generated only
from named columns in the supplied executed metrics file.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from xml.sax.saxutils import escape

PALETTE = ("#0f766e", "#2563eb", "#64748b", "#d97706")


def svg_chart(data, value_column, title, *, scale=1.0):
    if not 0 < scale <= 100:
        raise ValueError("Invalid scaling factor")
    required = {"model", value_column}
    if not required.issubset(data.columns) or data.empty:
        raise ValueError(f"Metrics require columns {sorted(required)}")
    vals = pd.to_numeric(data[value_column], errors="raise")
    if vals.isna().any() or not vals.between(0, scale).all():
        raise ValueError("All values must be within expected chart scale")
    height = 105 + 56 * len(data)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{height}" viewBox="0 0 760 {height}" role="img" aria-label="{escape(title)}">',
        '<rect width="760" height="100%" fill="#ffffff"/>',
        f'<text x="30" y="39" font-size="19" fill="#111827" font-weight="bold">{escape(title)}</text>',
        '<text x="30" y="65" font-size="12" fill="#4b5563">Measured offline UNSW-NB15 official test results</text>',
    ]
    for i, (name, val) in enumerate(zip(data["model"], vals)):
        yy=86 + i*56
        x=238
        bar_width=420*float(val)/scale
        parts.extend([
            f'<text x="30" y="{yy+17}" font-size="13" fill="#111827">{escape(str(name))}</text>',
            f'<rect x="{x}" y="{yy}" width="420" height="24" rx="4" fill="#e5e7eb"/>',
            f'<rect x="{x}" y="{yy}" width="{bar_width:.1f}" height="24" rx="4" fill="{PALETTE[i%len(PALETTE)]}"/>',
            f'<text x="672" y="{yy+17}" font-size="13" fill="#111827">{100*float(val):.2f}%</text>',
        ])
    parts.append('</svg>')
    return "\n".join(parts)+"\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/metrics_FULL_BENCHMARK.csv"))
    p.add_argument("--output-dir",type=Path,default=Path("results/figures"))
    args=p.parse_args()
    df=pd.read_csv(args.input)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for metric,title in [("f1","F1 score"),("recall","Attack recall"),("false_positive_rate","False alarm rate")]:
        output=args.output_dir/(metric+".svg")
        output.write_text(svg_chart(df, metric, title),encoding="utf-8")
        print(output)


if __name__=="__main__":
    main()
