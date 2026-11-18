# Executed five-seed donor-policy replication — exploratory

**Evidence source:** `results/permutation_seed_replication.json`, SHA-256-verified UNSW-NB15 official **training** split. Analysis date: 18 November 2026. The original official test split was not used in this experiment.

Three duplicate-group train/validation splits (seeds 13, 29, 47) and five permutation seeds (101, 211, 307, 401, 503) produced **60 conditions** across Logistic Regression, Random Forest and both donor selection policies.

## Results (excess false-positive interactions, percentage points)

| Model | Mean global donors | Mean same-class donors | Mean paired difference | Positive contrasts |
|---|---:|---:|---:|---:|
| Random Forest | +1.591 | -0.205 | +1.796 | 15/15 |
| Logistic Regression | +0.290 | +0.285 | +0.005 | 6/15 |

## Paired differences by validation split (mean over five permutations)

**Random Forest:** split 13: +1.712 pp; split 29: +1.985 pp; split 47: +1.693 pp.

**Logistic Regression:** split 13: +0.013 pp; split 29: -0.009 pp; split 47: +0.011 pp.

## Interpretation

For Random Forest, unrestricted feature-block donor sampling generated a consistently larger *synthetic* Protocol+Context excess false-positive-rate interaction than class-matched donor sampling across these conditions. The corresponding Logistic Regression contrast was small and inconsistent across permutation seeds.

**This is NOT a proof that the phenomenon is globally novel or generalizable.** Five permuted seeds on three overlapping training subsets are not independent datasets. Class-matched donors use true labels only as a retrospective diagnostic and cannot be used in a deployed IDS. Neither policy guarantees physically realistic traffic. The Protocol/Context pair was selected after earlier experiments, so these are **post-hoc exploratory** results.

Next: compare to a class-blind observable matching rule, account for different actual exchange rates, use conditional-group importance baselines and eventually an untouched independent corpus.
