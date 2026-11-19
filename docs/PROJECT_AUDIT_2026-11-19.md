# Independent-style internal project audit — 19 November 2026

**Project:** AI-NIDS Research  
**Scope:** GitHub source, saved executed UNSW-NB15 evidence, research design, CI, the current working manuscript, documentation and verified publisher/reference information.  
**Assessment type:** internal critical review, **not** peer review, a university admissions rubric, independent empirical replication, or formal novelty certification.

## Scorecard (0–10, approximate)

| Criterion | Rating | Support / main qualification |
|---|---:|---|
| Topic relevance | **9.5** | NIDS reliability, synthetic evaluation artifacts and false-alert rates are important research problems |
| Research question clarity | **9.0** | Explicit falsifiable donor-policy/false-alarm interaction question; strong scope discipline |
| Scientific originality | **6.5** | Specific replicated-within-corpus empirical audit, but conditional permutation and evaluation bias already exist in the literature |
| Data quality & provenance | **8.5** | Real historical benchmark, pinned split checksums, mirror caveats, overlap audit; external-origin data absent |
| Experimental coverage | **8.5** | LR/RF/dummy, threshold control, corruption, TTL control, 60-condition donor-seed replication, 54-condition observable study, 54-condition frozen-strata study |
| Methodological rigor | **7.5** | Train-only preprocessing and group-held-out training folds; many choices post-hoc, synthetic swaps can violate valid traffic constraints |
| Statistical reliability | **6.5** | Descriptive paired results and saved confusion counts; no network/session-clustered independent confidence intervals or multiple-testing control |
| Code & modularity | **8.5** | Separate experiment/report/audit modules, Python CI, defensive leakage checks; research-specific scripts, not a production package |
| Reproducibility | **8.5** | Clear input SHA-256, saved CSV/JSON, environment snapshots, unit and result-integrity tests; environment versions not fully frozen as a single lockfile |
| Automated testing / CI | **8.0** | Main CI successful on several recent commits; TTL workflow YAML repaired and rerun in progress as of audit, so full suite status still needs confirmation |
| Scientific manuscript | **8.0** | Unified Abstract/Methods/Results/Discussion/Limitations, verified number links; unreviewed, limited related-work breadth and no independent confirmation |
| GitHub presentation | **9.0** | Concise results-first README with chart and run commands, CITATION.cff, CONTRIBUTING, CHANGELOG, data/rights/AI disclosures |
| Practical deployment | **5.0** | Offline historical flow benchmarks only; no verified live traffic, realistic deployment false-alarm budget or zero-day claim |
| Academic portfolio potential | **8.0** | Strong research-engineering component if the student independently reproduces and can defend methodology; not an admissions guarantee |

### Overall

**Indicative overall research project quality: ~8.1/10.** This is a **holistic judgment, not the arithmetic mean** of the scores: originality, statistical independence, and external validation weigh heavily for scientific publication. Engineering and repository presentation are stronger than the validity of global scientific conclusions.

**Scientific originality: 6.5/10**, provisional. It cannot be raised to 9 merely by adding more commits, text, plots or synthetic seeds.

## What was actually measured

1. **Official split baseline:** 175,341 training / 82,332 test records. Random Forest F1 0.8902; attack recall 0.9885; false positive rate 0.2847 (10,535 benign false alarms). Evidence: `results/metrics_FULL_BENCHMARK.csv`.
2. **Fingerprint overlap audit:** 8,541 test records had a training predictor fingerprint match (10.37%). These are non-cryptographic hash matches, not authenticated identical real events. Evidence: `results/data_audit.json`.
3. **Post-hoc 5% false-alarm threshold:** validation-derived bound did not transfer; LR test FPR 11.41%, RF test FPR 14.54% under constrained policy. Evidence: `results/alert_budget_study.json`.
4. **Post-hoc donor-policy perturbation:** Random Forest mean excess Protocol+Context interaction +1.591 pp global vs −0.205 pp within-class oracle, a +1.796 pp difference over 15 matched within-corpus settings. Logistic Regression analogous contrast +0.005 pp. Evidence: `results/permutation_seed_replication.json`.
5. **Observable donor matching:** Random Forest excess interaction +1.610 pp global vs +0.959 pp using class-blind quantile grouping of `dur` and `sbytes`, with comparable row-exchange fractions. Evidence: `results/observable_donor_control.json`.
6. **Frozen matching boundaries:** Random Forest excess interaction +0.958734 pp with training-fitted quantile bins compared with +0.958702 pp with validation-fitted bins. Evidence: `results/train_fitted_donor_control.json` and `results/donor_quantile_comparison.json`.

All donor studies use the **same historical underlying training corpus**, and the feature pair was chosen after earlier positive-looking results.

## Research integrity warnings

- The official test was seen before some follow-up hypotheses; these are clearly marked exploratory.
- Repeat seeds on an overlapping dataset are **not** independent replication.
- Conditional permutation already has prior literature; this project does **not** own that general idea.
- Within-class oracle donors use true labels for offline diagnostics only. Presenting this as a real-time algorithm would be target leakage.
- The external standardized NetFlow-v2 proposal is **design only**. Its public dataset counts are publisher metadata, not downloaded/project-executed results.
- The paper and code are AI-assisted; the student must verify results, produce original scientific understanding and disclose assistance.
- Public code has no explicit license yet. Do not imply automatic open-source reuse rights.

## What a legitimate 9+ research score would require

1. **External-origin test** on correctly harmonized UQ NetFlow-v2 inputs, with independently verifiable provenance and a frozen source/target protocol.
2. Comparisons against *published* conditional/group permutation methods under identical fitted models and perturbation budgets.
3. Independent group/session-aware uncertainty and correction for choosing a feature pair after prior inspection.
4. Controls showing results are not entirely caused by physically invalid synthetic flows or different distortion magnitudes.
5. An investigator-verified manuscript, checked bibliography and reproducibility record.

## Presentation / workflow next actions

- Check that the repaired TTL workflow completes successfully; do not describe its CI as green before success.
- Verify latest main CI after the editorial changes, and retain a stable full-reproduction checkpoint or tag once reviewed.
- The owner should choose a license before inviting code reuse and set repository description/topics under GitHub **About**. Repository-admin operations may not be available to this connector.
- Independent expert feedback should target the scientific question and controls, rather than requesting artificial score inflation.

## External methodological anchors

- ADBench (NeurIPS 2022): https://github.com/Minqi824/ADBench
- NeurIPS reproducibility checklist: https://neurips.cc/public/guides/PaperChecklist
- UQ standardized NetFlow datasets: https://www.cyber.uq.edu.au/project/machine-learning-based-nids-datasets
- UNSW-NB15 original data: https://research.unsw.edu.au/projects/unsw-nb15-dataset

**Review date:** 19 November 2026. Any score is contingent on the then-current GitHub evidence; it is not externally certified.
