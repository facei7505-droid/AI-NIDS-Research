# Research status and evidence policy

Date: 2026-11-06

## Completed in this GitHub repository

- A scikit-learn training/evaluation program with train-only preprocessing.
- Validation for binary labels, feature schema, and expected split sizes.
- Logistic Regression and Random Forest baselines.
- F1, precision, recall, balanced accuracy, confusion counts, FPR/FNR and prediction latency.
- Optional 3-fold stratified cross-validation **on training samples only**.
- SHA-256 recording of supplied CSV files.
- A small synthetic-data unit test suite and GitHub Actions configuration.

## Not completed

- The full UNSW-NB15 training and evaluation run.
- Independent confirmation of dataset hashes/provenance.
- Any statistically supported claim that one model generalizes better.
- Distribution-shift experiments, category-wise evaluation, confidence intervals.
- A final paper with results from the released pipeline.
- Migration of the earlier NSL-KDD pilot PDF, PPTX, plots, and original local Git history.

## Methodological warnings

The pipeline does not automatically remove cross-split duplicate predictor rows. Inspect and document them, and analyze the impact on estimates before publication. Avoid repeated selection against the designated test set. The timings are machine-dependent. The fixed train/test benchmark is historical; it does not certify deployed network monitoring quality.

## AI contribution

Research planning, baseline code, tests, and documentation were AI-assisted. Researchers must independently validate the outputs, run and interpret the experiments, and accurately disclose assistance in any academic submission.

## Minimum bar for a final scientific report

1. Log source URL, download date, file hashes, full environment and hardware.
2. Reproduce all stated metrics from raw inputs using published code.
3. Inspect data overlap, class imbalance and category-wise failure cases.
4. Use training-only validation and provide uncertainty estimates.
5. Discuss leakage, distribution shift, external validity and limitations without exaggeration.

**Do not claim the project is complete, 10/10, or accepted by a university.**
