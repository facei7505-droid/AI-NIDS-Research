# Reproducibility

_Last updated: 8 November 2026._

## Requirements

Python 3.11, `pip`, and the dependencies in `requirements.txt`. Existing saved environment versions are under `results/environment-freeze.txt` and `results/environment-failure-fingerprints.txt`.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python src/download_data.py
```

The data downloader uses a **third-party mirror**, not a server controlled by UNSW. It verifies pinned SHA-256 checksums before accepting CSVs. The pinned hashes establish identity relative to the archived reference files; they do not independently prove the mirror's authority. See the official [UNSW dataset description](https://research.unsw.edu.au/projects/unsw-nb15-dataset) for provenance and data-use terms.

Training CSV: 175,341 rows; SHA-256 `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`.

Test CSV: 82,332 rows; SHA-256 `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`.

## Reproduce the published stages

```bash
python src/data_audit.py --train data/UNSW_NB15_training-set.csv --test data/UNSW_NB15_testing-set.csv
python src/run_experiments.py --cv --output results
python src/run_robustness.py --output results/robustness.json
python src/alert_budget_study.py --max-fpr 0.05
python src/analyze_alert_budget.py
python src/failure_fingerprints.py
python src/report_failure_fingerprints.py
python src/ttl_decomposition.py
```

**Warning:** Do not use the official test split for new hypothesis tuning or threshold selection. The alert-budget follow-up reused an already inspected test split and is explicitly exploratory.

## Reproduction checks

1. Verify file hashes, row counts, schema and positive-class convention.
2. Run tests before and after changes.
3. Verify confusion totals and calculate FPR as `FP / (FP+TN)` (benign is negative).
4. Preserve the exact benchmark split for comparison; do not silently discard overlapping rows.
5. Report seeds, software, CPU/machine environment, complete model parameters and failure cases.
6. Record what was observed **before** generating any new hypothesis.
7. Keep independently tested results separate from exploratory results.
8. Compare related methods under matched computation and splits; do not quote incomparable leaderboard scores.

## Evidence sources

- `results/metrics_FULL_BENCHMARK.csv` — original LR/RF/dummy experiment
- `results/data_audit.json` — cross-split fingerprint audit
- `results/alert_budget_study.json` — exploratory 5% FPR transfer
- `results/failure_fingerprints.json` — training-only group interactions
- `results/ttl_decomposition.json` — published post-hoc training-only evidence (60 perturbation conditions)
- `paper/MANUSCRIPT_DRAFT.md` — working manuscript, not peer reviewed

Results are stored as plain JSON/CSV and should not be regenerated into claims by manually changing numeric values.
