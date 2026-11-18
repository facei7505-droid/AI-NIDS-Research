# Research status (updated 2026-11-06)

## Completed, verifiable in repository

- Full official-designated UNSW-NB15 baseline experiment on 175,341 training and 82,332 test records. Saved `results/metrics_FULL_BENCHMARK.csv`, hash-identified inputs, `results/metadata_FULL_BENCHMARK.json`, `results/train_cv_FULL_BENCHMARK.csv`, synthetic robustness output and environmental package versions.
- LR, RF and majority Dummy comparisons. **RF: F1=0.8902, recall=0.9885, FPR=0.2847** (10,535 false positives). These are measured OFFLINE benchmark values, not operational effectiveness claims.
- Train/test feature fingerprint screening flagged 8,541 test rows matched to training (10.37%), requiring further source-level investigation.
- Baseline SVG charts generated from archived metrics, and a draft manuscript under `paper/MANUSCRIPT_DRAFT.md`.
- Group-held-out threshold study implementation, tests, preregistration-style research plan and automatic workflow are committed.

## Unfinished / uncertain

- **No independently established scientific novelty.** Threshold tuning and overlap-aware screening are established methods; the combined hypothesis remains to be tested and compared against literature.
- Alert-budget study outputs will only count as executed evidence when `results/alert_budget_study.json` and the corresponding workflow record exist and are reviewed. The follow-up is **exploratory**, because the official test outcomes were already inspected.
- Need validation of source-level duplicate/overlap fingerprints and the characteristics of conflicting labels.
- Need repeated validation splits, realistic uncertainty estimates, cost/recall trade-off, independent external benchmark, and a reviewed comparison against published methods.
- Need independent human replication of every figure and metric, full authorship and AI-assistance disclosure, and external review.

## Ethical scientific reporting

This repository and draft were substantially AI-assisted. A student should personally reproduce and interpret the work, document their research decisions and represent all assistance accurately. No university admission, award, research originality or peer-review outcome is guaranteed.
