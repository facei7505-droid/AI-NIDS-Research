# Reproducibility guide

**Last updated: 19 November 2026.** All reported values must correspond to real executed code, a pinned input dataset, and a tracked CSV/JSON artifact. Most follow-up studies are **exploratory** and should not be mistaken for independent confirmation.

## 1. Environment and tests

Requires Python 3.11.

```bash
git clone https://github.com/facei7505-droid/AI-NIDS-Research.git
cd AI-NIDS-Research
python -m venv .venv
# Linux/macOS:
# source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q src tests
```

Exact recorded environment snapshots are stored in `results/environment-freeze.txt` and `results/environment-failure-fingerprints.txt`. The version ranges in `requirements.txt` may resolve differently over time; for byte-for-byte replication, use a recorded environment snapshot with Python 3.11.

## 2. Dataset provenance

```bash
python src/download_data.py
```

This retrieves the released UNSW-NB15 designated CSV split formats from a **third-party public mirror**, verifying pinned SHA-256 checksums. The mirror is not controlled by UNSW; checksum consistency proves byte identity to the project's pinned reference, not original data authority.

| File | Rows | SHA-256 |
|---|---:|---|
| `data/UNSW_NB15_training-set.csv` | 175,341 | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| `data/UNSW_NB15_testing-set.csv` | 82,332 | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |

Original data documentation: https://research.unsw.edu.au/projects/unsw-nb15-dataset . The original CSVs are not committed to this repository.

## 3. Recreate historical benchmarks (the official test was previously inspected)

```bash
python src/data_audit.py --train data/UNSW_NB15_training-set.csv --test data/UNSW_NB15_testing-set.csv
python src/run_experiments.py --cv --output results
python src/alert_budget_study.py --max-fpr 0.05
python src/analyze_alert_budget.py
```

Re-running these commands repeats **historical exploratory evaluations**. It does not create a fresh unseen test set. The alert-budget threshold was specified after viewing original test results; no prospective confirmation is claimed.

## 4. Recreate training-only group-interaction and donor controls

```bash
python src/failure_fingerprints.py
python src/report_failure_fingerprints.py
python src/ttl_decomposition.py
python src/ttl_retraining_ablation.py
python src/report_ttl_retraining.py
python src/class_mixing_control.py
python src/analyze_class_mixing.py
python src/permutation_seed_replication.py
python src/observable_donor_control.py
python src/report_observable_donor.py
python src/train_fitted_donor_control.py
python src/compare_matching_boundaries.py
```

Some computations may be slow on a local PC. The training-only group-held-out split seeds and donor-seed settings are defined in the individual scripts and documented in `docs/RESEARCH_DESIGN.md`. The same-class donor policy uses labels **for an offline diagnostic only**, never a deployable classifier.

## 5. Check published evidence before citing a number

```bash
python -m pytest -q
```

In particular, `tests/test_published_evidence.py`, `tests/test_observable_donor_evidence.py`, and `tests/test_donor_quantile_published_evidence.py` validate that published metrics correspond to archived raw experimental records.

Archived input and output references:

- `results/metrics_FULL_BENCHMARK.csv` — official baseline, 3 models
- `results/data_audit.json` — screening audit for fingerprint overlap
- `results/alert_budget_study.json` — nominal 5% validation-FPR exploratory transfer
- `results/failure_fingerprints.json` — original group-permutation sensitivity
- `results/permutation_seed_replication.json` — 60 executed donor-policy conditions
- `results/observable_donor_control.json` — 54 executed three-way donor conditions
- `results/train_fitted_donor_control.json` — 54 executed conditions with training-fitted bins
- `results/donor_quantile_comparison.json` — 54 matched old-vs-frozen quantile contrasts
- `paper/MANUSCRIPT_DRAFT.md` — unrevised-for-peer-review working manuscript

All reports and figures must be generated from executed artifacts; do not edit metrics by hand to make a figure look better.

## 6. Independent origin datasets: NOT yet executed

The UQ standardized NetFlow-v2 source/target proposal is in `docs/NETFLOW_V2_EXTERNAL_PLAN.md`. Two large real external CSVs would have to be acquired legitimately and verified before any dataset transfer claim. The current audit tool only checks basic schema/labels/provenance:

```bash
python src/audit_netflow_v2_schema.py --source data/external/NF-UNSW-NB15-v2.csv --external data/external/NF-CSE-CIC-IDS2018-v2.csv
```

Do **not** run this command unless both files were actually obtained under those paths. It does not train a model. The external data are not included, and **no independent NetFlow-v2 evaluation result exists** in this repository.

## 7. Scientific interpretation limits

Repeated random folds/perturbations are not independently sampled network environments. Synthetic feature swaps can violate flow constraints, donor policies were partly selected after seeing preliminary outcomes, and official test labels have already been inspected. Neither reproducibility nor a passing CI badge proves scientific originality, real-world accuracy or peer review.

See [QUALITY_GATES.md](QUALITY_GATES.md) and [the working paper](../paper/MANUSCRIPT_DRAFT.md) for remaining requirements.
