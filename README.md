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
