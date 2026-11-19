# Observable-donor three-policy control — executed results

**Historical UNSW-NB15 training-only experiment; exploratory, not independently validated.**

Train file SHA-256: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`

| Model | Donor policy | Excess FPR (pp) | Joint FPR | Joint recall | Protocol exchanged | Context exchanged |
|---|---|---:|---:|---:|---:|---:|
| Logistic Regression | global | 0.337 | 24.53% | 90.55% | 25.04% | 24.88% |
| Logistic Regression | observable_strata | 0.221 | 23.95% | 93.28% | 25.02% | 24.86% |
| Logistic Regression | same_class_oracle | 0.309 | 15.02% | 96.87% | 25.04% | 24.88% |
| Random Forest | global | 1.610 | 17.70% | 92.50% | 25.04% | 24.88% |
| Random Forest | observable_strata | 0.959 | 15.96% | 96.48% | 25.02% | 24.86% |
| Random Forest | same_class_oracle | -0.219 | 11.33% | 96.95% | 25.04% | 24.88% |

## Paired contrasts by split

| Model | Split | Global − observable (pp) | Observable − oracle (pp) |
|---|---:|---:|---:|
| Logistic Regression | 13 | 0.126 | -0.060 |
| Logistic Regression | 29 | 0.181 | -0.153 |
| Logistic Regression | 47 | 0.039 | -0.048 |
| Random Forest | 13 | 0.462 | 1.239 |
| Random Forest | 29 | 0.858 | 1.165 |
| Random Forest | 47 | 0.634 | 1.128 |

## Scientific qualifications

- All data are from the official historical training split; overlapping splits do not provide independent population replicates.
- Class-matched donor sampling uses true labels as an offline oracle control only, and must not be used as a deployed detector.
- Observable strata are computed on validation features (transductive); grouping on duration and bytes does not guarantee physically consistent flows.
- Exchange frequency is not an exhaustive measure of distributional perturbation severity.
- Protocol/Context pairing and these policy choices are exploratory follow-ups; independent precommitted external replication is still missing.

This is a donor-policy sensitivity diagnostic, not proof of a new algorithm, a causal network phenomenon, or external generalization.
