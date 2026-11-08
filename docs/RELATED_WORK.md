# Research comparison and novelty assessment

_Last reviewed: 6 November 2026._

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
