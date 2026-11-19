# Research status and release gates

_Status as reviewed 19 November 2026 (Asia/Almaty). Dates refer to documented project commits and are not publication dates._

| Area | Status | Evidence |
| --- | --- | --- |
| UNSW-NB15 baseline | Measured | `results/metrics_FULL_BENCHMARK.csv`; RF F1 0.8902, recall 0.9885, FPR 0.2847 |
| Dataset overlap audit | Measured screening | `results/data_audit.json`; 8,541 test predictor fingerprints match training |
| Validation FPR budget | Measured, exploratory | `results/alert_budget_study.json`; 5% validation goal missed on official test (RF 14.54% FPR) |
| Failure Fingerprints | Measured, training-only exploratory | `results/failure_fingerprints.json`; RF Protocol+Context +1.796 pp mean excess FPR |
| TTL contribution | Measured, post-hoc exploratory | `results/ttl_decomposition.json`; 60 perturbation conditions |
| Matched TTL retraining ablation | Code and CI configured (result not yet verified) | `src/ttl_retraining_ablation.py`, `.github/workflows/ttl-retraining-ablation.yml` |
| Donor-policy falsification | Executed, exploratory | `results/class_mixing_control.json`; RF mean +1.660 global versus -0.277 within-class excess FPR |
| Permutation-seed replication | Code, tests and workflow committed; results pending | `src/permutation_seed_replication.py`; 60 planned conditions |
| Observable donor matching | Executed, exploratory | `results/observable_donor_control.json` (54 conditions) and `results/OBSERVABLE_DONOR_REPORT.md` |
| Independent external validation | Not done | `docs/EXTERNAL_VALIDATION_PROTOCOL.md` defines candidate independent corpora and mapping gates |
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

## Repository curation — 18 November 2026

- Rebuilt `README.md` around confirmed measurements and transparent limitations.
- Consolidated active methodology under `docs/`. Older protocol snapshots and benchmarking notes are preserved under `docs/archive/` (Git history retained); the root-level duplicates were removed.
- Added archived-evidence consistency tests and a retrained TTL ablation design. The new ablation's scientific conclusion remains pending successful experiment execution.
- Quality target 9.5/10 is aspirational. It requires independent dataset replication and reviewer scrutiny; no numeric grade is certified by these commits.

## Novelty falsification progress — 18 November 2026

- **Executed:** 60-condition repeated donor-policy experiment from `results/permutation_seed_replication.json`. For RF, mean global minus same-class excess-FPR interaction is +1.796 pp (15/15 matched comparisons positive); LR difference +0.005 pp (6/15 positive). All trials use UNSW-NB15 original *training* split.
- **Documented:** raw study and derived table at `results/PERMUTATION_SEED_REPLICATION_REPORT.md`; manuscript updated.
- **Implemented, not yet confirmed as executed:** Observable-stratified donor control uses class-blind matching on unperturbed `dur` and `sbytes`; code, unit tests, separate CI and complete output checks committed. No numeric results should be inferred until `results/observable_donor_control.json` exists.
- **Still missing for originality 9/10:** matched comparison to published conditional permutation methods, physically plausible traffic controls, untouched external dataset, and independent human replication.

## Research status, 19 November 2026

- Executed 54-condition class-blind observable-stratified donor control, saved raw JSON and derived report with reproducibility tests. RF mean excess FPR: global +1.610 pp, observable +0.959 pp, class-oracle −0.219 pp. This is synthetic training-only sensitivity, **not external validation**.
- [External validation protocol](EXTERNAL_VALIDATION_PROTOCOL.md) specifies official potential CIC corpora, provenance requirements and strict semantic feature-mapping gates. No independent dataset has yet been downloaded or tested.
- Missing gates: independent dataset with predefined legitimate shared groups, physical-consistency controls, formal literature review and statistical independence/cluster-aware uncertainty analysis. **9/10 novelty is not established.**
