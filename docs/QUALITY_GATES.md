# Quality gates and external research benchmarks

_Last assessed: **18 November 2026**. This is an internal checklist, not a university admission score or peer-review verdict._

## Research projects we use as methodological references

- **ADBench** ([repository](https://github.com/Minqi824/ADBench), NeurIPS 2022): encourages systematic fixed datasets, explicit baseline configurations, careful comparisons and reproducibility instead of cherry-picked model scores. We should retain all weak baselines, not only successful ones.
- **Adversarial Robustness Toolbox** ([repository](https://github.com/Trusted-AI/adversarial-robustness-toolbox)): mature modular testing and documented perturbation boundaries. Our synthetic feature-group permutations do not qualify as certified or adversarial robustness.
- **MLPerf** ([benchmark ecosystem](https://mlcommons.org/benchmarks/)): standardization, versioning, unambiguous metrics, logged execution conditions and comparable runs. Our project is an academic experiment, not an MLPerf-compliant submission.
- **UNSW-NB15** ([dataset provider](https://research.unsw.edu.au/projects/unsw-nb15-dataset)): known official-designated train/test split; high historical relevance but not a current deployment population.

No example above establishes that our method is novel; these are **quality practices** and must not be presented as comparative scientific outcome baselines.

## Required gates for a defensible 9–9.5/10 *internal* assessment

| Area | Concrete acceptance gate | Current status on 18 Nov 2026 |
|---|---|---|
| Valid inputs | Byte-pinned dataset provenance, exact split, full class metrics and confusion counts | **Completed** for UNSW-NB15 |
| Research design | Hypotheses fixed before outcome inspection; no tuning on held-out test | **Partial**; several current experiments explicitly post-hoc |
| Independent replication | At least one truly external, previously untouched corpus with harmonized features | **Missing** |
| Causal and alternative explanations | Matched retrained TTL ablation, alternative groupings, physically plausible shifts | **Partial**; retraining workflow published, results not yet verified |
| Statistical rigor | Dependence/cluster-aware uncertainty, multiple comparisons correction, repeated independent datasets | **Missing/partial**; Wilson intervals assume row independence |
| Strong matched baselines | Modern threshold/calibration and group-interaction comparisons, matched runtime/budget | **Partial**; majority, LR and RF supported |
| Reproducibility | Automated tests, environment freeze, checksums, data-split audit, all outcomes and failures published | **Mostly implemented**; complete current CI outcome still needs verification |
| Scientific argument | Clear review of closest methods and transparent limits of novelty | **Partial**; targeted overview but not a systematic review |
| Publication quality | Final internally reviewed manuscript with graphs, source citations, date, disclosures, replication instructions | **Draft** |
| Ownership | Student can reproduce work independently, defend choices and disclose substantial AI help | **Not externally assessed** |

**No project score should be forced to 9.5/10 simply because code, visuals or documentation improved.** The unsatisfied gates are scientific, not cosmetic.

## High-value next experiments

1. Execute the retrained full-vs-no-TTL study using paired training indices, keep the original 2026-11-18 design and report negative outcomes.
2. Compare grouped interactions with a documented alternative partition and an appropriate null control on *training validation only*.
3. Repeat on an untouched external dataset after registering the precise feature mapping, target definition and evaluation policy.
4. Use uncertainty methods appropriate for correlated sessions/traffic groups; explicitly handle multiple feature-group hypotheses.
5. Have the human investigator independently rerun at least one complete experiment and record hardware, dataset hashes, run time and decisions.

## How to report progress honestly

- **Executed:** provide commit, input hashes, machine-readable result, model definition, and test trace.
- **Pending:** code and workflow exist, but executed result is not yet confirmed.
- **Exploratory:** outcome or hypothesis is influenced by previously viewed labels and requires later untouched confirmation.
- **Unsupported:** do not claim first-in-world novelty, real-world protection, peer-review recognition or admission.
