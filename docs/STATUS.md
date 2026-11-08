# Research status and release gates

_Status as reviewed 6 November 2026 (Asia/Almaty). Dates refer to documented project commits and are not publication dates._

| Area | Status | Evidence |
| --- | --- | --- |
| UNSW-NB15 baseline | Measured | `results/metrics_FULL_BENCHMARK.csv`; RF F1 0.8902, recall 0.9885, FPR 0.2847 |
| Dataset overlap audit | Measured screening | `results/data_audit.json`; 8,541 test predictor fingerprints match training |
| Validation FPR budget | Measured, exploratory | `results/alert_budget_study.json`; 5% validation goal missed on official test (RF 14.54% FPR) |
| Failure Fingerprints | Measured, training-only exploratory | `results/failure_fingerprints.json`; RF Protocol+Context +1.796 pp mean excess FPR |
| TTL contribution | Code and workflow committed | `src/ttl_decomposition.py`; require validated results artifact |
| Independent external validation | Not done | Protocol and untouched external dataset needed |
| Paper | Draft | `paper/MANUSCRIPT_DRAFT.md`; not peer reviewed |
| Originality | Candidate hypothesis | No validated first-in-world claim |

## Release checklist for a research-quality version

- [x] Open source code and explicit experimental commands
- [x] Real hash-identified baseline outcomes
- [x] Negative control and train-only preprocessing
- [x] Train/test overlap diagnostic
- [x] Exploratory outcome limitations documented
- [x] Training-only group-level interaction study
- [ ] Independent replication on untouched external data
- [ ] Reliable grouped/cluster-aware uncertainty estimates
- [ ] Methodological review and systematic literature comparison
- [ ] Independent human verification of all results
- [ ] Final article, figures, cited sources and AI disclosure approved by investigator

This checklist is not a score. Do not equate repository polish with scientific novelty.
