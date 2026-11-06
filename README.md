# AI-NIDS Research

**Status: Research software under validation.** Full UNSW-NB15 results have **not** been measured or published here. Historical NSL-KDD pilot results are not independently reproduced.

This repository studies defensive, offline network intrusion detection using Logistic Regression and Random Forest. The research objective is to compare model discrimination, false-alarm burden and prediction latency under transparent, repeatable evaluation conditions.

## Data

Download the two predefined split CSV files from [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) into:

- `data/UNSW_NB15_training-set.csv` (175,341 rows)
- `data/UNSW_NB15_testing-set.csv` (82,332 rows)

Original CSVs are **not** redistributed here. Verify the dataset origin and checksums. Keep the designated test set completely separate from training and hyperparameter selection.

## Quick start

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python src/run_experiments.py --cv
```

Results are generated only when the designated input files are present. They are stored in `results/` as CSV and JSON with confusion counts, scores, timings, and input SHA-256 hashes.

## Research integrity

- Preprocessing (median imputation, standardization, categorical one-hot encoding) is fitted on training data inside scikit-learn pipelines.
- Training-only stratified cross-validation is optional.
- Neither the test set nor its labels may influence preprocessing or model selection.
- Binary labels are validated and leakage-prone features (`id`, `attack_cat`, `label`) excluded.
- Results from quick subsets or archival pilots must not be presented as full test-set benchmarks.
- Historical benchmarks do not establish real-world effectiveness against new attacks.

## Roadmap

1. Run full UNSW-NB15 benchmark with verified source files.
2. Add repeated trials, confidence intervals, and category-wise error analysis.
3. Evaluate feature reduction, robustness to distribution shift and inference cost.
4. Produce a paper from *measured* results with appropriate citations and AI-assistance disclosure.

**Do not claim a 10/10 scientific evaluation until the experiments are independently reproduced.**


## Research-quality components

| Component | File | Purpose |
|---|---|---|
| Benchmark | [src/run_experiments.py](src/run_experiments.py) | Train-only preprocessing, LR/RF and majority dummy, F1/FPR/average precision |
| Data audit | [src/data_audit.py](src/data_audit.py) | Check duplicate and cross-split feature fingerprints, conflicting labels |
| Uncertainty | [src/uncertainty.py](src/uncertainty.py) | Paired bootstrap intervals for predictions made on the same held-out rows |
| Stress testing | [src/robustness.py](src/robustness.py) | Synthetic missingness, numeric noise, and unseen categorical values |
| Tests | [tests/](tests/) | Synthetic-data unit tests |
| Scientific protocol | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | Questions, hypotheses, controls, evidence limitations |

**Important:** the data audit and stress-test modules are research utilities, not yet integrated into the main benchmark execution command. No robustness results have been collected. Do not confuse added experiments with executed experiments.

### Audit original splits

```bash
python src/data_audit.py \
  --train data/UNSW_NB15_training-set.csv \
  --test data/UNSW_NB15_testing-set.csv
```

Read [RESEARCH_STATUS.md](RESEARCH_STATUS.md) for the evidence status and [EXPERIMENT_LOG_TEMPLATE.md](EXPERIMENT_LOG_TEMPLATE.md) to record run metadata.


### Run the synthetic robustness study

Once both official training/test CSVs are in `data/`, run:

```bash
python src/run_robustness.py \
  --train data/UNSW_NB15_training-set.csv \
  --test data/UNSW_NB15_testing-set.csv \
  --output results/robustness.json
```

The script fits each classifier **once on the unmodified training split** and evaluates it on the untouched test features and predetermined synthetic missingness, numerical-noise, and novel-category conditions. The output records CSV SHA-256 hashes, feature names, class-specific performance, corruption severity and environment. The clean-input evaluation is a reference point, not an independent repeated trial.

**Research warning:** Synthetic input corruption is only a stress test, not evidence of robustness to real-life network drift or malicious traffic. For alternative datasets or toy examples pass `--exploratory`; those runs must not be reported as official UNSW-NB15 results.

The integration was locally smoke-tested on a small fabricated dataset (3 tests passed; 39 scenario rows generated). These are **software verification results, not scientific model accuracy results**. Full-benchmark execution and GitHub CI confirmation remain pending.
