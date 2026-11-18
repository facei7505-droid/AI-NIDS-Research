# Research contribution candidate: alarm-budget transfer under overlap and feature shift

**STATUS: prospective/exploratory; no novel scientific result established.**

## Scientific motivation

The existing UNSW-NB15 baseline produces a high attack recall for Random Forest (0.9885) but a false-positive rate of 0.2847 on the designated test set. A model can be an excellent anomaly ranker and still be operationally unsuitable at its default probability cutoff. The measured audit additionally flags 8,541 test feature vectors matching training feature vectors, so the apparent reliability must be investigated separately for unmatched records.

## Research questions

- RQ-A: When a threshold is chosen **using only training-held-out validation** to target a 5% false-alarm budget, does the measured official-test FPR satisfy this budget?
- RQ-B: Does the same policy satisfy this budget on the **non-overlapping subset of the official test split**?
- RQ-C: Does the decision change under synthetic missingness/noise/new-category stress?
- RQ-D: What recall is sacrificed when controlling false alarms? Is the tradeoff practically useful?

These questions extend a benchmark analysis, but thresholding, deduplication, and confidence bounds are all established techniques. **Originality must be argued through a literature comparison and independently verified findings**, not presumed from combining these methods.

## Registered implementation

`src/alert_budget_study.py` provides a group-held-out split of training data, where duplicate predictor rows are assigned to the same group. It trains each baseline on the grouped fitting subset. Threshold selection is conducted on the held-out validation group using an upper one-sided Wilson confidence bound for the benign false-positive proportion and aims for max FPR of 0.05.

The selected decision rule is evaluated separately on: (1) all official test rows; and (2) test rows without matching training predictor fingerprints. The original benchmark remains unchanged.

**Critical qualification:** Original UNSW-NB15 official test results were inspected before this protocol was written, making these additional tests **exploratory, not confirmatory preregistered results**. Confirmatory publication requires a new, untouched external dataset and protocol finalization before running it.

## Null hypotheses, expected contributions, and failure outcomes

- H0-A: Validation-constrained FPR does not transfer to the official test distribution within tolerance.
- H0-B: Excluding overlap does not materially change the estimated false alarm burden.
- H0-C: Synthetic corruption does not materially affect the thresholded system's recall or FPR.

A positive **or negative** experimental finding is useful when supported by transparent method, uncertainty analysis, repeat trials and external validation. A failure to satisfy the threshold budget must be explicitly reported.

## Research limitations

- UNSW-NB15 is historical and its splits differ in feature and class distributions.
- Matching a 64-bit pandas row fingerprint is a screening mechanism; investigate collisions and data-type normalization before asserting exact overlap.
- `GroupShuffleSplit` does not guarantee stratification, chronological separation or grouping by originating network/session.
- The Wilson bound quantifies simple binomial proportion uncertainty under i.i.d. assumptions; it cannot guarantee false-alarm transfer under covariate shift.
- The threshold selected at a single random seed is not enough for robust conclusions. Repeat validation splits and quantify policy variability.
- A 5% target may be unattainable without sacrificing most attack recall. This would be a scientifically meaningful negative result.
- Artificial feature corruption is a sensitivity test, **not** adversarial robustness and not proof against zero-day attacks.
- All follow-up comparisons using previously seen test data must be marked exploratory.

## Literature diligence

A complete novelty assessment needs searches in Google Scholar, Semantic Scholar and bibliographic indexes covering NIDS calibration, cost-sensitive learning, false-alarm-constrained ROC optimization, data contamination, and train-test distribution shift. Compare against strongest published methods with equivalent data, split, features, decision budgets and compute costs. Cite and discuss prior work honestly.

## Reporting and ownership

Publish all model settings, hash-verified inputs, group-split seed, selected thresholds, confidence-bound values, both test-subset sample sizes, confusion counts and software environment. Include AI-generated code disclosure and independent student replication. **Do not write a novelty claim, 9/10 score, or final conclusion before evidence exists.**
