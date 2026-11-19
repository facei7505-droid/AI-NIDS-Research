# When False-Alarm Interaction Estimates Depend on the Perturbation Protocol: An Exploratory Study of Network Intrusion Detection

**Working paper · version 0.2 · updated 19 November 2026**  
**Status:** Unpublished, not peer reviewed. Software, experiments, and manuscript are substantially AI-assisted; the human investigator must verify authorship, computations, citations, and conclusions before submission.

## Abstract

This study examines whether apparent feature-group interactions in machine-learning network intrusion detection systems (NIDS) depend on *how synthetic perturbation donors are selected*. We first benchmark a majority-class predictor, logistic regression (LR), and random forest (RF) on the historical UNSW-NB15 designated binary train/test splits (175,341/82,332 records). RF obtains test F1 of 0.8902 and recall of 0.9885, but generates 10,535 false alarms (FPR 0.2847). A subsequent validation-derived 5% false-alarm policy fails to transfer to the official test: the constrained RF test FPR is 14.54%. These analyses motivate an exploratory training-only investigation of feature-group permutation artifacts. For Protocol and Context feature blocks, unrestricted donor shuffling yields an RF mean excess FPR interaction of **+1.591 pp** versus **−0.205 pp** when donors are selected within the known class (three group-held-out splits, five donor seeds, 60 evaluated conditions). A later class-blind matching experiment using observed duration and source bytes lowers RF interaction from **+1.610 pp** under global shuffling to **+0.959 pp** under observable matching (54 conditions), with nearly identical actual exchange fractions. A further 54-condition follow-up freezes quantile bin boundaries using training records only and observes RF **+0.958734 pp**, indicating limited sensitivity to whether these particular boundaries were learned from validation data. The experiments concern **synthetic evaluation artifacts**, not a novel deployed detector. All follow-ups are post-hoc, use the same historical source corpus and require independent, semantically harmonized network-origin replication.

**Keywords:** network intrusion detection; false alarms; feature interaction; conditional permutation; benchmark shift; reproducibility.

## 1. Introduction and research questions

NIDS benchmarks often reward recall and F1 while obscuring false alarms and vulnerability to evaluation-design choices. Moreover, unconstrained feature permutations can break predictor relationships and create flow records that would not occur on a real network. We therefore ask:

**RQ1.** What baseline performance and false-alarm burden do simple supervised models demonstrate on the official UNSW-NB15 split?

**RQ2.** Does a threshold selected to meet a 5% FPR constraint on grouped training-only validation preserve that constraint on the designated test distribution?

**RQ3.** For predefined Protocol and Context feature blocks, does changing the donor-selection policy change the measured *non-additive FPR interaction*? Is this contrast model-dependent?

**RQ4.** Does observable class-blind donor grouping based on unperturbed flow duration and source bytes reduce that measured interaction? Does fitting grouping boundaries on training records (rather than held-out validation features) substantially change the result?

This is an empirical reliability question, **not** a claim to invent conditional permutation or to discover a universally new network phenomenon.

## 2. Data, provenance and models

The first benchmark uses the official-designated UNSW-NB15 split CSV formats containing 175,341 train and 82,332 test rows. The research downloader retrieves a public mirror with explicit SHA-256 verification:

| Input | Records | SHA-256 |
| --- | ---: | --- |
| UNSW-NB15 designated training CSV | 175,341 | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| UNSW-NB15 designated testing CSV | 82,332 | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |

Hash agreement identifies pinned mirror files; **it does not independently authenticate the mirror or demonstrate data collection by this project**. Positive label 1 represents an attack; FPR = FP/(FP+TN), with benign label 0.

Numeric imputation, scaling where used, and categorical encoding are fitted only on each corresponding model-training fold. LR and RF are compared against a majority-class dummy predictor. RF uses 100 estimators and minimum leaf size 2, with random seed 42; full parameter details are in `src/run_experiments.py`.

For subsequent synthetic perturbation studies, records originate exclusively from the pinned **training CSV**, partitioned with `GroupShuffleSplit` by predictor fingerprint to reduce exact cross-fold predictor overlap. Reported validation-seed repetitions share most of the same records; **they are not independent network populations**.

## 3. Experimental design

### 3.1 Baseline and alert-budget studies

The baseline evaluates full-training LR/RF/dummy models on the designated test. In a later *exploratory* threshold study, LR and RF train on 139,989 records, choose thresholds on 35,352 grouped validation records to satisfy a one-sided Wilson upper bound for a nominal 5% benign FPR, then evaluate on the previously inspected official test split. Hence the result is a post-hoc stress test, not pristine confirmatory inference.

### 3.2 Feature-group interaction metric

We assign existing UNSW predictors to Timing, Volume, Protocol and Context groups (`src/failure_fingerprints.py`). For synthetic selected-row donor permutation, feature values in a predefined group are permuted **together**, preserving within-group co-occurrence but not necessarily consistency across groups. The primary contrast for two feature groups A and B is:

```text
Excess interaction FPR (percentage points) =
    100 × [ FPR(A+B) - FPR(A) - FPR(B) + FPR(clean) ].
```

The original four-group scan used three group-held-out split seeds (13, 29, 47) and a 25% perturbation rate. Its largest observed RF Protocol+Context excess FPR was +1.796 pp on average, which motivated subsequent **post-hoc** falsification controls.

### 3.3 Falsifying unrestricted donor selection

The first control compares unrestricted global block permutation to a **same-class oracle** donor policy. In the oracle policy, the true benign/attack label is used solely to match donor pools during *offline evaluation*. It is **not available for an unlabeled production IDS**. Both policies use the same fitted estimator, grouped train/validation splits, Protocol/Context feature lists and perturbation fraction. Three validation seeds and five separate donor seeds yield 60 model × split × seed × donor-policy outcomes.

### 3.4 Label-blind matching and leakage-reduction control

A later 54-condition study includes a third policy matching donors by quantile bins of unperturbed observed duration (`dur`) and source bytes (`sbytes`). This version computes bins on validation covariates and is therefore **transductive**, although it does not use class labels. It records actual exchanged-row proportions separately from selection masks.

A further 54-condition experiment fits numeric medians and quantile boundaries **on the fitting fold only**, freezes them and applies them unchanged to validation. This controls for a specific form of evaluation-distribution adaptation. The design uses the same three grouped split seeds, three donor seeds, two model families and three donor policies.

### 3.5 Statistical interpretation

Reported averages and repeated-seed comparisons are descriptive. The splits overlap heavily, network flows may be correlated, and feature-group/donor policies were chosen after earlier results were inspected. Treating 9 or 15 permuted conditions as independent population samples would be invalid. We do not claim formal significance, a causal mechanism or novelty priority.

## 4. Results

### 4.1 Official designated test benchmark

| Model | F1 | Recall | Precision | FPR | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Majority Dummy | 0.7102 | 1.0000 | 0.5506 | 1.0000 | 37,000 | 0 |
| Logistic Regression | 0.8492 | 0.9726 | 0.7536 | 0.3895 | 14,412 | 1,243 |
| Random Forest | **0.8902** | **0.9885** | **0.8096** | **0.2847** | 10,535 | 522 |

Source: `results/metrics_FULL_BENCHMARK.csv`. Three-fold training-only CV produced higher F1 values (LR about 0.9539, RF about 0.9692); this gap is not causally explained by the current analysis. Predictor-fingerprint screening flagged **8,541** test rows (10.37%) as matching training predictor fingerprints; these are not proof of identical real network events. Details: `results/data_audit.json`.

### 4.2 Alert-budget transfer

| Validation-trained model | Test FPR, threshold 0.5 | Test FPR, validation-constrained | Constrained recall |
|---|---:|---:|---:|
| Logistic Regression | 39.14% | **11.41%** | 86.71% |
| Random Forest | 28.62% | **14.54%** | 95.32% |

Source: `results/alert_budget_study.json`. For RF, the constrained threshold prevents 5,210 false alarms but adds 1,598 missed attacks on the same designated test compared with the threshold-0.5 control. Validation met the nominal ~5% criterion, but the official test did not. The test data had been viewed during earlier baseline analysis; no prospective confirmation is implied.

### 4.3 Perturbation donor-policy replication

| Model | Global donor excess FPR | Same-class oracle excess FPR | Paired difference | Positive paired differences |
|---|---:|---:|---:|---:|
| Random Forest | **+1.591 pp** | **−0.205 pp** | **+1.796 pp** | 15/15 |
| Logistic Regression | +0.290 pp | +0.285 pp | +0.005 pp | 6/15 |

Source: `results/permutation_seed_replication.json`; 60 conditions across three overlapping grouped validation splits and five permutation seeds. The contrast appears model-specific under these conditions. **It does not show a first-in-world interaction.**

### 4.4 Three-way donor-policy comparison

| Model | Global donors | Observable class-blind strata | Same-class oracle |
|---|---:|---:|---:|
| Random Forest | **+1.610 pp** | **+0.959 pp** | −0.219 pp |
| Logistic Regression | +0.337 pp | +0.221 pp | +0.309 pp |

Entries are mean *excess FPR interaction* in percentage points; data: `results/observable_donor_control.json` (54 conditions). RF global vs observable decreases by **0.651 pp**. Joint-condition Protocol and Context exchange fractions remain close to 25% across policies, reducing the plausibility of a simple exchange-count explanation but not ruling out distortion-severity confounding.

### 4.5 Frozen quantile boundaries

With the same model/split/seed/policy cells, observable-matching RF excess FPR was **+0.958702 pp** when bin limits were learned from validation and **+0.958734 pp** when learned strictly on fitting data. LR changed from **+0.221477 pp** to **+0.213412 pp**. Sources: `results/train_fitted_donor_control.json` and `results/donor_quantile_comparison.json` (54 paired conditions).

The near-zero RF contrast suggests this particular bin-learning choice had little impact *in the historical training corpus*. Frozen boundaries are methodologically cleaner; they do not alone establish cross-dataset generalization.

### 4.6 TTL shortcut sensitivity

The earlier training-only TTL perturbation experiment measured mean RF increases in FPR of **+6.24 pp** for TTL-only feature changes and **+7.93 pp** for combined complete Protocol+Context group changes. A separate retraining-without-TTL experiment is stored in `results/ttl_retraining_ablation.json`. These experiments altered different factors; results cannot be combined to infer that TTL is the unique cause of the original interaction. Full caveats and numerical comparisons: `docs/INTERACTION_REPLICATION_CHALLENGE.md`.

## 5. Discussion and relationship to prior work

The central observed result is **instability in the measured synthetic feature-interaction diagnostic** when donor policies differ. The Random Forest interaction shows a large unrestricted-versus-class-oracle contrast, while LR's is small. Observable, label-blind donor matching sits between these two policies for RF. Thus, conclusions about which feature groups jointly produce excess false alarms may depend on **evaluation design**, not solely on the learned model.

Conditional permutation and dependence-aware feature importance have already been studied. NIDS evaluation bias, domain shift and common-feature NetFlow dataset families are established areas. This project's possible contribution is a *specific quantitative audit and falsification protocol* for false-alarm interaction estimates, **not** the invention of conditional feature permutation or a novel NIDS classifier.

The strongest next test is an independent-origin, standardized feature-space comparison: UQ's NetFlow v2 source family and an external-origin CIC-derived domain. This has **not** been executed. See `docs/NETFLOW_V2_EXTERNAL_PLAN.md` and `src/audit_netflow_v2_schema.py` for the provenance and schema gate. Mapping raw UNSW Protocol/Context fields directly into CICFlowMeter records would not be valid.

## 6. Limitations and research integrity

1. All current model experiments derive from a **single historical network benchmark**; independent network-origin replication is missing.
2. Synthetic donor-block permutations may create impossible joint network-flow values; no live network or realistic traffic generator was evaluated.
3. Validation-split seeds are correlated, and no session-clustered uncertainty model has been completed.
4. Protocol+Context and the donor-policy follow-ups are **post-hoc**, selected after seeing preliminary outcomes. Multiple comparison selection bias remains.
5. Same-class oracle donors use true labels in diagnostic donor selection and cannot be deployed at inference.
6. The original threshold-transfer follow-up reused an already inspected official test split.
7. Cross-split fingerprint matches do not prove identical underlying events; collisions and canonicalization effects remain possible.
8. The research is **substantially AI-assisted**; independent investigator verification and disclosure are required. No peer review, world-first priority or practical protection is claimed.

## 7. Reproducibility and data availability

The public repository includes preprocessing, model definitions, hash-verified file-download logic, all archived numeric results and automated unit/evidence-integrity tests. Primary artifacts are ordinary CSV/JSON; test infrastructure is GitHub Actions. Study commands and detailed data/provenance boundaries are in `docs/REPRODUCIBILITY.md`.

The actual source CSVs are not redistributed by this repository. Public source information is linked below. **A no-license repository cannot be assumed to grant reuse permission**; the investigator must choose an explicit code license before public redistribution or reuse claims.

## 8. Conclusion

We found a **model-dependent sensitivity of measured false-alarm feature-group interactions to the donor-selection policy** within a historical NIDS benchmark. The finding survived repeated synthetic perturbation seeds, and a label-blind observable matching control partly reduced the RF interaction without meaningfully reducing the number of exchanged rows. A training-fitted matching variant produced similar findings. These outcomes constitute **exploratory methodological evidence**, not an original validated algorithm, a causal explanation of real attacks, or a claim that we have reached scientific novelty 9/10. Confirmation requires held-out external-origin data, a frozen harmonized feature protocol, stronger inference and independent review.

## References

1. Moustafa, N., & Slay, J. (2015). *UNSW-NB15: A comprehensive data set for network intrusion detection systems.* MilCIS. https://doi.org/10.1109/MilCIS.2015.7348942
2. Moustafa, N., & Slay, J. (2016). *The evaluation of network anomaly detection systems: Statistical analysis of the UNSW-NB15 data set and the comparison with the KDD99 data set.* Information Security Journal. https://doi.org/10.1080/19393555.2015.1125974
3. Berhili, M., Chaieb, O., & Benabdellah, M. (2026 online). *How evaluation protocol choices inflate intrusion detection accuracy: A three-dataset systematic study.* Computers & Security. https://doi.org/10.1016/j.cose.2026.105218
4. Han, S., Hu, X., Huang, H., Jiang, M., & Zhao, Y. (2022). *ADBench: Anomaly Detection Benchmark.* NeurIPS, Datasets and Benchmarks. https://proceedings.neurips.cc/paper_files/paper/2022/hash/cf93972b116ca5268827d575f2cc226b-Abstract-Datasets_and_Benchmarks.html
5. Sarhan, M., Layeghy, S., & Portmann, M. (2022). *Towards a Standard Feature Set for Network Intrusion Detection System Datasets.* Mobile Networks and Applications. https://doi.org/10.1007/s11036-021-01843-0
6. University of Queensland Cyber Research Centre. *Machine Learning-Based NIDS Datasets* (NetFlow v2, common feature format). https://www.cyber.uq.edu.au/project/machine-learning-based-nids-datasets
7. University of New South Wales. *UNSW-NB15 dataset.* https://research.unsw.edu.au/projects/unsw-nb15-dataset

**Citation audit needed before submission:** the bibliography is intentionally short and does not replace a systematic literature search covering conditional importance, feature interactions, NIDS session dependence and drift.
