# Preregistered-style research protocol (draft; before full benchmark)

**Project title:** Reliable and Efficient Network Intrusion Detection Under Data Shift and Limited Computational Resources

**Status:** a prospective protocol, not completed research. Protocol revisions must be documented before reading the designated test labels.

## Research questions

- **RQ1 (baseline):** How do Logistic Regression (LR) and Random Forest (RF) compare on the official UNSW-NB15 test split in F1, recall, false-positive rate (FPR), PR-AUC, and inference cost?
- **RQ2 (resource efficiency):** Can fewer training-only-selected features deliver competitive sensitivity at lower inference latency and model memory?
- **RQ3 (robustness):** How do missing values, bounded numerical measurement noise, and previously unseen categorical levels influence model detection quality relative to clean inputs?

These are testable questions, **not claims of novel algorithms**. Separate data-shift work must acknowledge that label-preserving synthetic corruptions do not reproduce evolving real-world attacks.

## Hypotheses (prospective)

- H1: RF and LR differ in recall/FPR trade-off on the designated split. No direction is asserted before testing.
- H2: At least one training-only feature subset may reduce latency/model size without a large loss in recall; the margin must be declared before experiments (suggested: 0.02 absolute recall).
- H3: Both models will experience reduced recall under increasing measurement corruption, but the relative degradation is unknown.

## Data and contamination checks

Primary dataset: official UNSW-NB15 predefined training/test CSV files. Verify download origin, split shapes, SHA-256 hashes, column names, duplicated records, and cross-split exact overlap. Report overlap both with and without labels. **Never silently delete test records.** If overlap exists, report an additional clearly labelled *sensitivity analysis*, preserving the original official test benchmark.

Exclude: identifiers, target, attack category from binary-classification predictor set. Fit imputation, scaling, one-hot encoding, and any feature selection using **training rows only**.

## Evaluation protocol

1. Freeze code version, dependencies, seeds, selected columns and model settings.
2. Train baseline LR, RF and a **majority-class dummy control** on the official training split.
3. Perform model/threshold/feature selection on stratified train-only CV. Test data are never used for development.
4. Predict the designated official held-out test set **once for each frozen candidate**.
5. Record confusion counts and positive-class F1, recall, precision, FPR, balanced accuracy and PR-AUC (PR-AUC only where continuous model scores are available).
6. Record class prevalence and confusion-matrix-normalized rates; absolute percentage-point differences matter more than accuracy alone.
7. Quantify paired performance differences via bootstrap resampling of held-out **rows** with a fixed seed, 2,000 resamples and percentile intervals. This estimates test-sample uncertainty, **not** uncertainty from training-set/domain shift.
8. Repeat CPU inference measurements after warm-up with at least 10 runs; report median, IQR, computer specs, batch size, thread count, and memory.
9. For robustness experiments, define corruption levels and transformations using the training distribution, apply them only to evaluation inputs, and declare them **synthetic stress tests**, not zero-day detection.
10. For all follow-up investigations that see the test results, designate the analysis *exploratory* and use new external data for confirmatory claims.

## Required figures

- Dataset split and label prevalence.
- PR curves and confusion matrices for baselines.
- Recall vs FPR at preselected thresholds.
- Recall vs feature count; inference latency and model size vs feature count.
- Detection degradation vs prespecified corruption severity.
- Paired difference uncertainty intervals.

## Decision rules and limitations

No model is declared generally 'better' based on F1 alone. Compare detection trade-offs, uncertainty, resource constraints and robustness. If findings are not statistically or practically distinguishable, report **inconclusive**.

Do not extrapolate from historical offline UNSW-NB15 to live attacks or promise 'real-time protection'. Subject all methodological changes and paper figures to independent review.

## Student ownership and integrity

Student investigator should personally explain preprocessing choices, data splits, confusion matrix, threshold selection and failure cases, independently run experiments, and maintain an experiment notebook with dates and hashes. AI assistance must be transparently disclosed.

## Core sources

- Society for Science. Regeneron ISEF Grand Award Judging Criteria. https://www.societyforscience.org/isef/grand-award/criteria/
- Bouke & Abdullah (2023). Pattern leakage in ML-based IDS, *Expert Systems with Applications*. https://doi.org/10.1016/j.eswa.2023.120715
- Berhili, Chaieb & Benabdellah (2026). Evaluation protocol choices and IDS accuracy, *Computers & Security*. https://doi.org/10.1016/j.cose.2026.105218
- UNSW-NB15 official dataset. https://research.unsw.edu.au/projects/unsw-nb15-dataset
