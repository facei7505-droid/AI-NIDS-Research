# False-alarm-budget transfer: executed exploratory analysis

**Exploratory:** the original UNSW-NB15 designated test split was inspected before
this experiment was designed. These data do not support a preregistered
confirmatory claim or proof of novelty.

- FPR budget targeted on grouped training validation: **5.00%**
- Training-fit records: **139,989**
- Training-validation records: **35,352**
- Official test records: **82,332**
- Test rows matching training predictor fingerprints: **8,541**
- Unmatched test rows: **73,791**
- Training input SHA-256: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`
- Test input SHA-256: `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`

## Frozen evaluation results

| Model | Cutoff policy | Validation FPR upper | Test FPR | Test recall | Test F1 | Non-overlap FPR | Non-overlap recall |
|---|---|---:|---:|---:|---:|---:|---:|
| Majority Dummy | default | N/A | 100.00% | 100.00% | 71.02% | 100.00% | 100.00% |
| Majority Dummy | validation_constrained | 0.02% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| Logistic Regression | default | N/A | 39.14% | 97.30% | 84.89% | 39.35% | 96.82% |
| Logistic Regression | validation_constrained | 4.99% | 11.41% | 86.71% | 88.47% | 10.66% | 84.30% |
| Random Forest | default | N/A | 28.62% | 98.84% | 88.97% | 28.39% | 98.66% |
| Random Forest | validation_constrained | 4.99% | 14.54% | 95.32% | 92.01% | 14.15% | 94.50% |

## Interpretation guide

- A validation budget is not a guaranteed upper bound on test FPR; directly inspect measured differences.
- Observe absolute changes in recall, not just reductions in FPR.
- The unmatched subset can differ systematically from the complete test distribution; it is not an independent random sample.
- A majority-class classifier is a negative control, not a useful operational detector.
- The study does not establish effectiveness on live networks, novel attack types, or independent external datasets.

## Constraints and limitations

- Fingerprint matching is not proof of semantic record identity.
- GroupShuffleSplit is not a time- or network-group shift.
- Official test performance is exploratory after previous test analyses.
- A validation FPR constraint is not guaranteed to transfer to shifted test data.
- Results are offline historical benchmark data, not live IDS proof.

**Scientific novelty has not been established.** Review published literature and validate on an untouched external dataset before claiming an original contribution.
