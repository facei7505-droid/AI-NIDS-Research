# AI-NIDS Research

**Failure Fingerprints: Investigating False-Alarm Instability in Lightweight Network Intrusion Detection**

[![CI](https://github.com/facei7505-droid/AI-NIDS-Research/actions/workflows/tests.yml/badge.svg)](https://github.com/facei7505-droid/AI-NIDS-Research/actions/workflows/tests.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Research status](https://img.shields.io/badge/research-exploratory-64748b)

> **Research status — 18 November 2026:** Historical UNSW-NB15 baseline, false-alarm transfer, feature-group interaction, and TTL sensitivity experiments have **executed**. Scientific originality and external generalization are **not established**. No claim of peer review, novel detector architecture, real-time protection or independent external validation is made.

## Research question

**Which combinations of network-traffic features create non-additive false alarms, and how much of their apparent influence could come from benchmark-specific TTL shortcuts?**

We study a model's *failure modes*, not merely its accuracy. The current reproducible setup uses official-designated UNSW-NB15 train/test CSV splits with hash-verified provenance, training-only preprocessing, transparent model configurations, saved confusion counts, source code, CI tests and machine-readable evidence.

## Measured results

### 1 · Official designated test benchmark

| Model | F1 | Attack recall | False positive rate (FPR) |
| --- | ---: | ---: | ---: |
| Majority Dummy | 0.7102 | 100.00% | 100.00% |
| Logistic Regression | 0.8492 | 97.26% | 38.95% |
| Random Forest | **0.8902** | **98.85%** | **28.47%** |

**Source:** [Executed benchmark CSV](results/metrics_FULL_BENCHMARK.csv) · [Metadata, hashes and environment](results/metadata_FULL_BENCHMARK.json) · [Dataset audit](results/data_audit.json).

High recall is **not** proof of an effective operational intrusion detector: RF falsely flagged **10,535** benign test records. The fingerprint audit flagged **8,541** test predictor rows matching training fingerprints (10.37%). Such matches require careful verification; they are **not proof** of identical network events.

### 2 · Validation-selected 5% false-alarm limit

A threshold selected using grouped **training-only validation** did **not** preserve the target FPR on the official test:

| Model | Test FPR, default | Test FPR, constrained | Constrained recall |
| --- | ---: | ---: | ---: |
| Logistic Regression | 39.14% | 11.41% | 86.71% |
| Random Forest | 28.62% | **14.54%** | **95.32%** |

The constrained RF made **5,210 fewer false alarms** but missed **1,598 additional attacks** relative to the default cutoff in the *same* validation-trained study. This was designed after seeing the initial official-test results: **post-hoc exploratory evidence, not independent confirmation**.

**Evidence:** [Experiment JSON](results/alert_budget_study.json) · [Analysis and limitations](results/ALERT_BUDGET_ANALYSIS.md).

### 3 · Failure Fingerprints: group interactions

We perturb predefined feature groups (**timing**, **volume**, **protocol**, **context**) on grouped validation splits of the **training CSV only**. Across three split seeds, the Random Forest **Protocol + Context** pair showed an average **+1.796 percentage points** of *excess false-positive interaction* (individual values approximately +1.773, +1.905, +1.711 pp). This is a synthetic sensitivity measure, **not evidence of a novel attack mechanism or causal feature attribution**.

**Evidence:** [Complete 66-condition study](results/failure_fingerprints.json) · [36 interaction records and summaries](results/FAILURE_FINGERPRINTS_REPORT.md).

### 4 · TTL-shortcut sensitivity (post-hoc)

The later training-only TTL study produced **60 conditions** (3 split seeds × 2 permutation seeds × 2 models × 5 conditions). For RF, the mean **FPR increase relative to clean validation** was:

| Synthetic feature perturbation | Mean increase in RF FPR |
| --- | ---: |
| TTL attributes only | **+6.24 pp** |
| Protocol without TTL | +1.53 pp |
| Context without TTL | +2.01 pp |
| Protocol core + Context core | +3.28 pp |
| Full Protocol + Context | +7.93 pp |

These are **perturbation effects**, not excess interactions, and must not be compared as though they were the same statistic as the +1.796 pp above. The observed contrast motivates shortcut analysis but **does not establish that TTL caused the original interaction**.

**Evidence:** [Executed TTL sensitivity JSON](results/ttl_decomposition.json) · [Code](src/ttl_decomposition.py).

## Research structure

```text
AI-NIDS-Research/
├── README.md                   # Research overview and verified results
├── docs/
│   ├── RESEARCH_DESIGN.md      # Method, hypotheses, data boundaries
│   ├── RELATED_WORK.md         # Comparable research and novelty limits
│   ├── REPRODUCIBILITY.md      # Installation, data integrity, commands
│   └── STATUS.md               # Evidence gates and remaining work
├── paper/
│   └── MANUSCRIPT_DRAFT.md     # Draft article; not peer reviewed
├── src/                        # Training, diagnostics and reporting
├── tests/                      # Synthetic-data unit tests
├── results/                    # Executed, hash-identified evidence
└── .github/workflows/          # CI and research execution workflows
```

## Quick start

Requires **Python 3.11**:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python src/download_data.py
python src/run_experiments.py --cv --output results
python src/failure_fingerprints.py --train data/UNSW_NB15_training-set.csv
python src/report_failure_fingerprints.py
```

The downloader fetches *public mirror copies* of the official-designated split CSV files, checking pinned SHA-256 hashes before use. **Dataset origin:** [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset). Dataset bytes are not tracked in Git.

See [full reproducibility instructions](docs/REPRODUCIBILITY.md) for Windows, exact commands, provenance limitations and experiment-specific caveats.

## Research integrity and limitations

- The historical UNSW-NB15 benchmark is **not** a substitute for live network deployment or fresh external validation.
- Artificial corruption/permutation may create physically impossible feature combinations.
- Split seeds on one dataset are correlated and not independent external replication.
- Official test results were seen before several follow-up hypotheses, so those analyses are exploratory.
- TTL and cross-split fingerprint effects need deeper attribution and source-level validation.
- Academic novelty must be established through a systematic literature review, matched baselines and independent reproducibility; it **cannot** be guaranteed by the title or repository presentation.
- This codebase and manuscript were substantially AI-assisted. Any student authorship claim must identify the investigator's own work and disclose assistance accurately.

**Quality review:** [Measured scientific quality gates](docs/QUALITY_GATES.md) · [Archived prior research plans](docs/archive/RESEARCH_PROTOCOL_2026-11-06.md).\n\n**Project documentation:** [Study protocol](docs/RESEARCH_DESIGN.md) · [Related work](docs/RELATED_WORK.md) · [Reproducibility](docs/REPRODUCIBILITY.md) · [Evidence status](docs/STATUS.md) · [Working paper](paper/MANUSCRIPT_DRAFT.md).

_Last repository documentation review: **19 November 2026**._

## Retrained TTL ablation — next controlled experiment

The earlier TTL test perturbed a model **already trained with TTL fields**. That cannot establish how a model trained *without* TTL behaves. To address this, we now compare a full-feature and a TTL-removed model, **retrained independently on identical training indices and assessed on the same held-out rows**.

- [Experiment](src/ttl_retraining_ablation.py) and [paired reporting code](src/report_ttl_retraining.py)
- [Unit tests](tests/test_ttl_retraining_ablation.py) and [report tests](tests/test_report_ttl_retraining.py)
- [Reproducible GitHub Actions run](.github/workflows/ttl-retraining-ablation.yml)

Once CI has successfully completed, `results/ttl_retraining_ablation.json` and `results/TTL_RETRAINING_REPORT.md` will contain measured comparisons. Until then **no result or scientific conclusion is claimed**. The new analysis was formulated after studying existing TTL interactions; it is exploratory and must be independently replicated.

## Interaction replication challenge — 18 November 2026

The initial RF Protocol + Context experiment showed +1.796 pp mean excess FPR, but the later **core-group** matched TTL retraining study did not reproduce the same positive sign (full-model core-group mean **−0.259 pp**, retrained no-TTL mean **+0.060 pp**). **These are not equivalent experiments:** group membership and permutation seed differed, so the discrepancy cannot yet be attributed to one cause.

We now prioritize *falsification*, not claiming novelty from the first positive-looking result:

- [Exactly what changed between studies](docs/INTERACTION_REPLICATION_CHALLENGE.md)
- [Executed full-vs-no-TTL retraining data](results/ttl_retraining_ablation.json)
- [Class mixing falsification code](src/class_mixing_control.py), [tests](tests/test_class_mixing_control.py) and [workflow](.github/workflows/class-mixing-control.yml)

The class-mixing study contrasts global feature-group donor shuffling with same-class donor shuffling. The latter uses **ground-truth labels only as an offline diagnostic**, and must never be presented as a deployable IDS method. New results should not be claimed until `results/class_mixing_control.json` is actually generated and checked.

## Donor-policy falsification — executed exploratory finding

[Executed global vs same-class donor study](results/class_mixing_control.json) found the Protocol+Context excess FPR interaction for Random Forest was **+1.660 pp** using global donor shuffles and **−0.277 pp** using within-class donor shuffles (mean paired difference **+1.937 pp**, 3 non-independent grouped splits). Logistic Regression changed far less (+0.307 vs +0.289 pp). The same-class comparison uses true class labels **only for offline diagnostics** and is not deployable.

Interpretation: the interaction finding is sensitive to how synthetic donor blocks are selected. This does **not** establish causation, independent replication, or a new algorithm. See the [quantitative report](results/CLASS_MIXING_ANALYSIS.md), [replication challenge](docs/INTERACTION_REPLICATION_CHALLENGE.md), and [closest prior work](docs/RELATED_WORK.md).

[Repeated random-permutation factorial experiment](src/permutation_seed_replication.py) and [CI workflow](.github/workflows/permutation-seed-replication.yml) are committed to test 60 combinations across three grouped splits, five perturbation seeds, two models and two donor policies. Treat the experiment as **pending until** `results/permutation_seed_replication.json` is published from verified execution.

## Replicated donor policy comparison — November 2026

The executed [60-condition perturbation-seed study](results/permutation_seed_replication.json) used three grouped training/validation splits, five independent perturbation seeds, and two ML models. It compared unrestricted donor sampling with within-ground-truth-class donors while freezing group definitions and training splits.

| Model | Global excess FPR | Within-class excess FPR | Paired mean difference | Positive paired comparisons |
|---|---:|---:|---:|---:|
| Random Forest | +1.591 pp | −0.205 pp | **+1.796 pp** | 15/15 |
| Logistic Regression | +0.290 pp | +0.285 pp | +0.005 pp | 6/15 |

Read the [full verified-data summary](results/PERMUTATION_SEED_REPLICATION_REPORT.md). These 15 comparisons are **not 15 independent studies**. They reuse the same training corpus. Ground-truth labels are used only to *diagnose* donor-policy artifacts, not to train or operate a deployed detection model.

**Next falsification step:** [Observable Donor Control](src/observable_donor_control.py) matches potential donors using only unperturbed numeric features `dur` and `sbytes`, without ground-truth class labels. [Tests](tests/test_observable_donor_control.py) and [CI](.github/workflows/observable-donor-control.yml) are committed. Its findings must not be reported before `results/observable_donor_control.json` is published from an executed successful run. This is transductive evaluation stratification, not physically validated or production-ready matching.

## Observable donor matching: 54 executed conditions (19 November 2026)

The [executed 3-policy donor study](results/observable_donor_control.json) and [reproducible scientific analysis](results/OBSERVABLE_DONOR_REPORT.md) compare unrestricted global donor shuffling, two-feature observable-stratified matching (class-blind), and within-class matching (an offline label-oracle control only).

| Model | Global excess FPR | Observable-stratified excess FPR | Same-class oracle excess FPR |
|---|---:|---:|---:|
| Random Forest | +1.610 pp | **+0.959 pp** | −0.219 pp |
| Logistic Regression | +0.337 pp | +0.221 pp | +0.309 pp |

The values come from 3 grouped validation splits × 3 donor seeds × 2 models × 3 policies (**54 conditions**), using the official UNSW-NB15 **training** data only. For RF, the observed contrast global minus observable is **+0.651 pp**; measured exchange rates are close to 25% for Protocol and Context under each policy. This identifies an empirical **methodological sensitivity**, not a new detector architecture or independent confirmation of a previously unknown mechanism.

- [Executed analysis JSON](results/observable_donor_analysis.json)
- [Analysis generator](src/report_observable_donor.py) and [integrity tests](tests/test_observable_donor_evidence.py)
- [External validation protocol](docs/EXTERNAL_VALIDATION_PROTOCOL.md) — CIC-IDS2017 / CSE-CIC-IDS2018 are **candidates only**. Source/target feature mappings have not been verified and no independent cross-dataset result is claimed.

The study is exploratory: the feature pair and donor policies were developed after viewing related results, and class-blind observable matching is transductive, not physically guaranteed or production-grade.
