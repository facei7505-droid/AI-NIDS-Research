# Failure Fingerprints: prospective analysis plan

**Status:** exploratory, added 2026-11-06, before inspecting the *Failure Fingerprints* outcome file. The UNSW-NB15 official test split and earlier threshold-transfer results have already been inspected for other research questions; this study is only training-split exploratory research.

## Distinct research question

When a set of network-flow features is permuted jointly across training-held-out validation records, do **pairs of feature groups** cause an excess rise in false-positive rate (FPR) or recall loss beyond the sum of the single-group changes? Are the signs stable across multiple predefined group-held-out splits?

This asks about **non-additive model sensitivity under a synthetic perturbation**, not a claim that no related work exists. It must be checked against prior grouped perturbation, feature interaction, robustness and NIDS literature.

## Predefined variables and controls

- **Source:** only `UNSW_NB15_training-set.csv`, pinned by SHA-256. No official test labels are imported.
- **Training/validation:** group-held-out 80/20 split using feature fingerprints, repeated with seeds 13, 29, 47.
- **Classifiers:** existing Logistic Regression and Random Forest with baseline default cutoff 0.5. Majority Dummy excluded from group interactions because it cannot react to feature permutations.
- **Groups:** timing, volume, protocol and context (literal feature lists in `src/failure_fingerprints.py`).
- **Single perturbations:** shuffle a random 25% of validation rows' feature values within each group. Rows are permuted together for all columns in a group.
- **Pairs:** all six combinations of two groups, each using the same group-specific shuffle and selection seed as in the corresponding single-group condition, holding the other group fixed.
- **Metrics:** benign FPR, attack recall and F1, recorded with all TP/TN/FP/FN counts.
- **Primary descriptive statistic:** excess joint FPR (percentage points): `[FPR(A+B)-FPR(clean)]-[FPR(A)-FPR(clean)]-[FPR(B)-FPR(clean)]`.
- **Secondary:** excess joint recall loss analogously. Negative and positive values are both reported.
- **Replication:** report all three split seeds separately plus mean and sample standard deviation. This is a split-sensitivity screen; repeated splits are NOT independent samples.

## Claims we will NOT make

- No model-proven deployment resilience, real network drift detection, or adversarial robustness.
- Permutations can create impossible combinations of fields; this is a synthetic diagnostic, not faithful traffic generation.
- Group effects do not prove causality or uniquely identify the underlying features responsible.
- A statistically significant novelty claim is impossible from three overlapping splits without external dataset replication.
- Negative interactions are as important as positive interactions, and no pairs will be removed for flattering presentation.
- The existing official test set may only be used for clearly labeled exploratory extensions and cannot provide pristine confirmation.

## Falsifiable follow-up

If large positive excess-FPR interactions recur for the same groups across splits, evaluate them using different perturbation mechanisms and a completely untouched external network dataset. If they disappear or reverse, report that synthetic feature-group interactions are unstable under the chosen experimental setup.

The scientific contribution must be based on **replicable evidence and comparative literature**, not the algorithm's name or ambitious title.

## Reproduce

```bash
python src/download_data.py
python -m pytest -q
python src/failure_fingerprints.py --train data/UNSW_NB15_training-set.csv --output results/failure_fingerprints.json
python src/report_failure_fingerprints.py --input results/failure_fingerprints.json
```

Artifacts from actual execution are expected in `results/` after workflow success. Do not interpret missing files as zero effects.
