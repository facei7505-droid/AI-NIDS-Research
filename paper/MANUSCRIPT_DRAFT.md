# Reproducibility, False Alarms and Validation Shift in Lightweight Network Intrusion Detection

**Manuscript draft v0.1 — 6 November 2026. Not peer reviewed, not submitted, and not a claim of novel discovery.**

## Abstract

Network intrusion detection models are often compared by aggregate classification scores, which may conceal high false-alarm rates and evaluation instability. We implement a transparent offline benchmark of majority-class classification, logistic regression (LR), and random forest (RF) on the prescribed UNSW-NB15 splits (175,341 training, 82,332 test records). Processing is fit on the training records only, and saved experiment metadata include file hashes, software versions, per-model confusion counts, and prediction timing. On the held-out test, RF attained F1=0.8902, recall=0.9885, precision=0.8096, and false-positive rate (FPR)=0.2847, while LR attained F1=0.8492 and FPR=0.3895. An exact-predictor-fingerprint screening flagged 8,541 (10.37%) test records as matching training predictors, and training-only cross-validation produced substantially higher F1 than the official test. These results motivate additional **exploratory** analyses of false-alarm-bounded thresholds and the role of cross-split overlap. A new group-held-out validation study is implemented, but its outcomes are **not included in this draft**. This article reports measured baseline findings and describes open uncertainties rather than claiming practical deployment readiness or novel detector performance.

## 1. Background and research gap

A network intrusion detection system (NIDS) seeks to identify traffic associated with potentially harmful activity. Because most machine-learning NIDS studies report global metrics, it is important to inspect class prevalence, false alarms, sensitivity, and the evaluation split. UNSW-NB15, introduced by Moustafa and Slay (2015), includes deliberately configured normal and attack flows. The designated split enables comparable offline evaluation, although it represents an older controlled dataset, not today's live network environments.

Recent work by Berhili, Chaieb and Benabdellah (2026) discusses how evaluation choices can inflate NIDS scores, highlighting why an attractive random-split metric cannot replace a held-out official-test estimate. Our contribution candidate is a carefully audited comparison of how a validation-only false-alarm budget transfers to both the official test distribution and a separate subset of records without identical training fingerprints. Threshold methods and overlap screening are not intrinsically novel; further literature review and new evidence are necessary to establish any original insight.

## 2. Research questions

RQ1. What tradeoffs do LR, RF, and a majority-class negative control exhibit on the designated UNSW-NB15 binary test split?

RQ2. How different are the training-only cross-validation and official held-out scores, and is cross-split feature-vector overlap present?

RQ3 (pending analysis). Does a threshold chosen on grouped validation with an upper confidence constraint on the benign false-positive rate satisfy its nominal 5% alarm budget on the official test and non-overlap subset?

RQ4 (pending analysis). Does the same policy retain useful recall under synthetic feature corruption? Synthetic corruption cannot establish resilience to real malicious adaptation.

## 3. Methods

### Dataset and provenance

Official-designated CSV splits contain 175,341 training and 82,332 test rows. Files were retrieved from a publicly hosted mirror; the original dataset is credited to UNSW. The benchmark records SHA-256 hashes:

- Train: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`
- Test: `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`

Mirror provenance must be distinguished from obtaining files directly from UNSW. Hash verification demonstrates byte identity to pinned files, not the mirror's scientific authority.

### Predictors and leakage control

The released pipeline excludes `id`, target `label` and attack category `attack_cat` and selected address/timestamp identifiers. Numeric fields receive median imputation and standard scaling; categorical fields receive imputation and one-hot encoding with unknown-category handling. All preprocessing steps are nested in scikit-learn pipelines fitted on training data only. RF uses 100 estimators, minimum leaf size 2 and a fixed random seed; LR uses maximum 1,000 iterations and fixed seed. Models were not tuned against the official test to create the reported baseline.

### Comparison protocol

All models were evaluated on the official 82,332-row test split. Positive class = network attack. Confusion counts are recorded alongside F1, precision, recall, average precision (ranking metric), balanced accuracy, false-positive and false-negative rates. Three-fold stratified cross-validation was conducted only on the official training records. Prediction timing is environment-specific, and does not represent network packet-by-packet throughput.

### Data overlap audit

A screening audit hashes 42 predictor values for each row; 8,541 test rows matched at least one training fingerprint. This is not definitive proof of identical underlying network events, and the fingerprint is not cryptographic. The official split is never silently altered. Any unmatched-subset evaluation will be clearly distinguished as a sensitivity analysis.

## 4. Executed baseline results

| Model | F1 | Precision | Recall | FPR | Average precision | False positives | False negatives |
|---|---:|---:|---:|---:|---:|---:|---:|
| Majority Dummy | 0.7102 | 0.5506 | 1.0000 | 1.0000 | 0.5506 | 37,000 | 0 |
| Logistic Regression | 0.8492 | 0.7536 | 0.9726 | 0.3895 | 0.9661 | 14,412 | 1,243 |
| Random Forest | 0.8902 | 0.8096 | 0.9885 | 0.2847 | 0.9870 | 10,535 | 522 |

RF offered the highest measured F1 and recall in this implementation but incorrectly flagged 10,535 benign test rows, demonstrating that high recall alone is not evidence of an operationally acceptable alerting system. The deliberately weak dummy classifier predicts attacks for every row, yielding recall of 1.0 while triggering a false alarm for every benign sample.

Training-only three-fold mean F1 was approximately 0.9539 for LR and 0.9692 for RF, compared with official-test scores of 0.8492 and 0.8902. Such gaps may reflect distribution differences, class composition or other aspects of the benchmark and cannot be causally attributed to any one explanation on the current evidence.

An audit flagged 74,301 repeated training predictor fingerprints, 28,386 repeated test fingerprints, and 229 training predictor groups with conflicting labels. These are *audit counts*, not independently confirmed duplicate events, and are a priority for follow-up verification.

## 5. Research integrity and limitations

1. This is an offline benchmark on historical UNSW-NB15. No claimed field deployment, zero-day protection, or production readiness is justified.
2. Training-only cross-validation and the designated test use different data regimes; further experiments are needed to explain the gap.
3. The overlap fingerprint depends on type normalization and hashing and can miss semantically equivalent records or conflate collisions.
4. False-positive control requires training/validation-based threshold selection, independent testing, and explicit reporting of recall loss.
5. A one-sided Wilson bound on validation false-positive proportion relies on assumptions that may fail under network distribution shift.
6. One run and single train/test split cannot capture uncertainty across new networks and periods.
7. The previously viewed official test results mean any newly designed follow-up on this test is exploratory, not confirmatory.
8. The research software and paper development were substantially AI-assisted; the student must independently run, inspect, understand and accurately disclose these contributions.

## 6. Prospective next experiments

The companion script `src/alert_budget_study.py` will select a threshold using grouped training-held-out validation without seeing official test labels, then measure the resulting FPR and recall on the complete official test and non-overlap subset. Threshold infeasibility will be reported as a valid result. Planned extensions include repeated validation seeds, uncertainty intervals, calibrated comparisons, external dataset evaluation, and feature-shift experiments at frozen thresholds. These are proposals, not completed measurements in this draft.

## 7. Conclusion

The executed baseline indicates that discrimination quality and the false-positive burden can paint very different pictures of the same NIDS model. Substantial separation between cross-validation and official-test performance, plus an overlap screening finding, motivate careful evaluation-policy research. We have **not established** a novel method or a generalizable detection improvement. The next scientific step is to complete and independently review confirmatory experiments, not to optimize a score for appearances.

## References

1. Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems. *MilCIS*. https://doi.org/10.1109/MilCIS.2015.7348942
2. Moustafa, N., & Slay, J. (2016). The evaluation of network anomaly detection systems: Statistical analysis of the UNSW-NB15 data set and the comparison with the KDD99 data set. *Information Security Journal: A Global Perspective, 25*(1–3), 18–31. https://doi.org/10.1080/19393555.2015.1125974
3. Berhili, M., Chaieb, O., & Benabdellah, M. (2026). How evaluation protocol choices inflate intrusion detection accuracy: A three-dataset systematic study. *Computers & Security*. https://doi.org/10.1016/j.cose.2026.105218
4. University of New South Wales (UNSW). UNSW-NB15 dataset. https://research.unsw.edu.au/projects/unsw-nb15-dataset

### Reproduction entry points

- `src/download_data.py` — pinned split files
- `src/data_audit.py` — overlap screening
- `src/run_experiments.py` — full baseline and train-only CV
- `src/run_robustness.py` — synthetic sensitivity tests
- `src/alert_budget_study.py` — exploratory alert-budget investigation
- `results/` — executed baseline artifact exports (see workflow history)


## 8. Follow-up: false-alarm-budget transfer (executed exploratory analysis)

This section documents an **exploratory follow-up**, developed after the official test performance of the baseline models had already been viewed. It is therefore not an independent pre-registered hypothesis test or proof of scientific novelty.

A separate group-held-out split of the original training data used 139,989 records to fit the models and 35,352 for validation. Duplicate predictor fingerprints were kept in the same validation group to reduce direct training/validation contamination. Model-specific thresholds were selected to target a **5% benign false-positive rate** on validation, with a one-sided Wilson upper-bound constraint. The frozen thresholds were then evaluated on the original 82,332-row official test set and its 73,791-row subset without matching training predictor fingerprints.

| Model | Policy | Official-test FPR | Official-test recall | Official-test F1 |
|---|---|---:|---:|---:|
| Logistic Regression | Default probability threshold 0.5 | 39.14% | 97.30% | 84.89% |
| Logistic Regression | Validation-constrained threshold 0.79660 | 11.41% | 86.71% | 88.47% |
| Random Forest | Default probability threshold 0.5 | 28.62% | 98.84% | 88.97% |
| Random Forest | Validation-constrained threshold 0.68444 | 14.54% | 95.32% | 92.01% |

The new validation-split models differ from those trained on the complete 175,341-row original training set; therefore their default-threshold baseline metrics are not numerically identical to Section 4.

For the constrained Random Forest, **5,210 fewer benign records were falsely flagged**, at a cost of **1,598 additional missed attacks** relative to the default threshold on the same test set. Logistic Regression avoided **10,261 false alarms**, but missed **4,799 additional attacks**.

Despite nominal validation false-positive rates of approximately **4.66%** for both learned models and an upper validation confidence bound under 5%, the measured official-test FPR reached **11.41%** for LR and **14.54%** for RF. These results fail the targeted 5% operational budget.

On the train-fingerprint non-overlap subset, constrained FPR was **10.66%** for LR and **14.15%** for RF. The subset therefore did not restore the nominal budget. Because overlap exclusion changes the composition of the sample, it is inappropriate to infer that duplicate contamination causes the discrepancy.

Descriptive two-sided 95% Wilson intervals for constrained official-test FPR were approximately **11.09–11.74%** for LR and **14.18–14.90%** for RF. These simple row-level intervals rely on independence assumptions and do not account for clustered network flows, selection after seeing baseline results, or shifts between datasets.

### Interpretation

The experiment provides evidence that a threshold selected to meet a false-alarm constraint on training-held-out validation **did not transfer that constraint** to the historical official test distribution. This observation supports further research into shifts in class-conditional score distributions and validation design. It does not establish a globally new technique, nor does it prove that distribution shift is the only explanation.

Before a stronger causal explanation or originality claim, we need multiple independent validation splits, source-level verification of overlap fingerprints, threshold calibration comparisons, an untouched external test dataset, and uncertainty estimates accounting for flow dependence.

**Evidence:** `results/alert_budget_study.json`, `results/alert_budget_analysis.json`, `results/ALERT_BUDGET_ANALYSIS.md`. The experimental pipeline and report-generation code are in `src/alert_budget_study.py` and `src/analyze_alert_budget.py`.

### Updated research conclusion

The strongest supported finding to date is a *negative transfer result*: a conservatively selected validation FPR budget of 5% was not preserved on the designated test split, even after separating test rows without identical training predictor fingerprints. The measured improvement in false alarms came with a quantifiable increase in missed attacks. Because the data and question are not fully independent, external confirmation is essential.
