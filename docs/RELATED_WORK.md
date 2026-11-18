# Research comparison and novelty assessment

_Last reviewed: 8 November 2026._

The purpose of comparison is to identify **gaps**, not to borrow unsupported performance claims.

| Reference project | Evidence-backed practice adopted | How this project differs |
| --- | --- | --- |
| [ADBench (NeurIPS 2022)](https://github.com/Minqi824/ADBench) | Fixed datasets, multiple baseline models, controlled corruptions, comprehensive tables and reproduction guidance | Our domain is offline NIDS reliability and excess *false-alarm interaction* by predefined feature groups, not a general anomaly-detection leaderboard |
| [Adversarial Robustness Toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Separating experiments, reusable modules, examples, tests and clear limits | Our synthetic group permutations are **not** adversarial attacks or certified robustness |
| [MLPerf reference implementations](https://github.com/mlcommons/training) | Explicit run configurations, data instructions, performance logging and benchmark rules | Our scope is scientific behavior and failure analysis, not system speed competition |
| [UNSW-NB15 dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | Named source, documented split, reproducible dataset provenance | Our results cover historical offline data and do not prove effectiveness on contemporary networks |

## Literature to verify before a submission

- Moustafa, N., & Slay, J. (2015). *UNSW-NB15: A comprehensive data set for network intrusion detection systems*. MilCIS. DOI: [10.1109/MilCIS.2015.7348942](https://doi.org/10.1109/MilCIS.2015.7348942).
- Han, S., Hu, X., Huang, H., Jiang, M., & Zhao, Y. (2022). *ADBench: Anomaly Detection Benchmark*. NeurIPS. [Project](https://github.com/Minqi824/ADBench).
- Review the body of literature on conditional/group permutation importance, functional ANOVA interaction effects, NIDS domain shift, threshold transfer and testbed-feature shortcuts. These broad approaches are **not new inventions** of this project.

## What is and is not established

- **Established in our data:** RF Protocol + Context excess false-positive rate was positive for all three reported training validation seeds, with mean +1.796 percentage points.
- **Not established:** a new algorithm, novelty priority, causal contribution of TTL features, external reproducibility, robustness on live traffic, or significance across independent populations.
- **Testable next step:** compare the Protocol + Context result with and without TTL-related fields, then repeat with independent perturbation seeds and external data where features are harmonized.

This is a targeted review, not a systematic literature survey. A publication needs documented search strings, screening dates, exclusion criteria, and checks against recent peer-reviewed research.


## Closest methodological precedents — review 18 November 2026

The **core conditional-permutation idea already exists** in broader ML interpretability and newer NIDS work. The work is therefore a *possible empirical NIDS reliability contribution*, NOT a fundamentally new feature-importance algorithm.

1. **Molnar et al. / conditional subgroup permutation (Data Mining and Knowledge Discovery, 2024)**: model-agnostic feature importance with dependent features, showing how unconditional permutation can distort interpretation when feature values are correlated. [Publication PDF](https://storage.googleapis.com/lacuna-pdfs-lunar-airport-385023/pdfs/9a/ac/9aac1c94d23d6f9728ec86b11383b15aad42e06c718b7f156ea15b8b4dd95846.pdf). Bibliographic details require verification against the journal metadata before formal APA use.
2. **Reliability auditing of explanations for machine-learning-based intrusion detection systems (2026)**: compares explanation and permutation diagnostics in an NIDS setting. [Springer](https://link.springer.com/article/10.1007/s11416-026-00664-7).
3. **Confusion-Aware Explainable Alert Triage for Network Intrusion Detection (2026)**: investigates group-level feature relevance and attack-class-specific prediction problems in UNSW-NB15. [Applied Sciences](https://www.mdpi.com/2076-3417/16/21/10746).
4. **A Three-Axis Stress Test of LLM vs Classical ML for Network Intrusion Detection under Distribution Shift and Adversarial Evasion (2026)**: explores external transfer, evaluation shifts and misleading aggregate NIDS metrics. [arXiv preprint](https://arxiv.org/abs/2609.13511), not equivalent to a peer-reviewed publication.
5. **scikit-learn permutation feature importance documentation** describes ordinary global permutations and their limitations. [Documentation](https://scikit-learn.org/stable/modules/permutation_importance).

### Specific gap we are testing

Our post-hoc training-only analysis finds that **whether the donor block is allowed to come from a different attack/benign class** changes Random Forest's apparent Protocol+Context excess FPR (+1.660 vs −0.277 percentage points; difference +1.937 pp), while Logistic Regression shows little analogous difference (+0.307 vs +0.289 pp). These are observed in three non-independent grouped splits.

The question for a future confirmatory study is *how much of apparent NIDS feature-group interaction can be explained by model-dependent, donor-policy-induced out-of-distribution artifacts*, conditional on source network and physical feature consistency. This is not an assertion of unique precedence: conditional feature importance and interactions have extensive prior literature.

**Publication gate:** systematic literature search, clear inclusion criteria, new external data, independent repetitions, class and session dependence handling, and mechanism controls. Avoid calling this a world-first method.
