# AI-NIDS Research

**Status: baseline benchmark executed and published; follow-up originality study exploratory and not yet validated.** Full UNSW-NB15 binary baseline results and reproducibility metadata are available under `results/`. Historical NSL-KDD pilot results are not independently reproduced.

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

The already executed, verified-input baseline results are committed in `results/`. Fresh reproduction requires the pinned CSV files and the commands below. Metrics include confusion counts, scores, timings and SHA-256 hashes.

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

## Executed benchmark, novelty work and manuscript

- [Real baseline results](results/metrics_FULL_BENCHMARK.csv) — 175,341 training and 82,332 held-out test records. Random Forest baseline F1 **0.8902**, Recall **0.9885**, FPR **0.2847** (10,535 benign false alarms). This is **not** a deployment-ready alarm rate.
- [Data audit](results/data_audit.json) — 8,541 test records match a training predictor fingerprint (~10.37%); fingerprint coincidences are not verified identical source events.
- [Measured F1 figure](results/figures/f1.svg), [Recall figure](results/figures/recall.svg), [FPR figure](results/figures/false_positive_rate.svg).
- [Evidence-grounded manuscript draft](paper/MANUSCRIPT_DRAFT.md) — research article in progress, not peer reviewed.
- [Novelty and validation plan](NOVELTY_AND_VALIDATION_PLAN.md) — explicit hypotheses and caveats.
- [Exploratory alert-budget study code](src/alert_budget_study.py) and [automated workflow](.github/workflows/alert-budget-study.yml).

The alert-budget workflow is designed to publish `results/alert_budget_study.json` and `results/ALERT_BUDGET_REPORT.md` **only after successful execution and validation**. If these files are absent, results are pending or the run failed — no threshold-transfer conclusion is claimed. The official test dataset had been inspected before the follow-up study was designed; therefore that analysis is **exploratory** and cannot establish original confirmatory evidence on its own.

## AI assistance and student ownership

Much of the software and draft text was AI-assisted. Scientific authorship must accurately reflect the investigator's personal contributions, independent verification and ability to explain the study. A high school research project should not present automated output as a student-discovered result without independent validation.


## Executed exploratory false-alarm follow-up (2026-11-06)

The [executed threshold study](results/alert_budget_study.json) and its [descriptive statistical report](results/ALERT_BUDGET_ANALYSIS.md) are now available. Selection targeted a **5% false-positive rate on training-only held-out validation**. It **did not transfer** to the official test set:

| Model | Default test FPR | Constrained test FPR | Constrained test recall |
|---|---:|---:|---:|
| Logistic Regression | 39.14% | 11.41% | 86.71% |
| Random Forest | 28.62% | 14.54% | 95.32% |

For Random Forest, this removed 5,210 false alarms but produced 1,598 more missed attacks than the default threshold in the same study. On the non-overlap test subset, constrained FPR remained 14.15% for Random Forest and 10.66% for Logistic Regression.

**Status:** These are real executed historical benchmark measurements, but follow-up design occurred after baseline test inspection. Consequently findings are exploratory, not independently validated novel science. See the [updated research manuscript](paper/MANUSCRIPT_DRAFT.md).

Reproduce the descriptive statistics after running the threshold study:

```bash
python src/analyze_alert_budget.py --input results/alert_budget_study.json
```


## Failure Fingerprints: training-only feature-group interaction experiment

New exploratory analysis designed to investigate potential **non-additive increases in false alarms** when two groups of traffic features change together. This is a hypothesis, **not a confirmed discovery**.

- [Predefined protocol](FAILURE_FINGERPRINTS_PROTOCOL.md) — hypotheses, seeds (13, 29, 47), four groups, all six pairs, limits and falsification.
- [Experiment code](src/failure_fingerprints.py) — only the official 175,341-row **training CSV** is used; the official test CSV is never loaded.
- [Research reporting](src/report_failure_fingerprints.py) — reports all group effects and pair interactions; no selective best-case reporting.
- [Tests](tests/test_failure_fingerprints.py) and [GitHub Actions workflow](.github/workflows/failure-fingerprints.yml) for automatic execution.

After successful execution, outputs will be `results/failure_fingerprints.json` and `results/FAILURE_FINGERPRINTS_REPORT.md`. Their absence means **results not yet confirmed**.

```bash
python src/failure_fingerprints.py --train data/UNSW_NB15_training-set.csv
python src/report_failure_fingerprints.py
```

These perturbations can create unrealistic traffic-feature combinations and are not evidence of deployment robustness or a globally new discovery. An untouched external benchmark and comparison with feature-interaction literature are required.
