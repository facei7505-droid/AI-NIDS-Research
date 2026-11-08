# AI-NIDS Research

**Failure Fingerprints: Investigating False-Alarm Instability in Lightweight Network Intrusion Detection**

[![CI](https://github.com/facei7505-droid/AI-NIDS-Research/actions/workflows/tests.yml/badge.svg)](https://github.com/facei7505-droid/AI-NIDS-Research/actions/workflows/tests.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Research status](https://img.shields.io/badge/research-exploratory-64748b)

> **Research status — 8 November 2026:** Historical UNSW-NB15 baseline, false-alarm transfer, feature-group interaction, and TTL sensitivity experiments have **executed**. Scientific originality and external generalization are **not established**. No claim of peer review, novel detector architecture, real-time protection or independent external validation is made.

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

**Project documentation:** [Study protocol](docs/RESEARCH_DESIGN.md) · [Related work](docs/RELATED_WORK.md) · [Reproducibility](docs/REPRODUCIBILITY.md) · [Evidence status](docs/STATUS.md) · [Working paper](paper/MANUSCRIPT_DRAFT.md).

_Last repository documentation review: **8 November 2026**._
