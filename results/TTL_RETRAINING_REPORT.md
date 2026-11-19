# Matched TTL retraining ablation — executed exploratory findings

**Post-hoc on the UNSW-NB15 training split only. Not an independent confirmation.**

Input training SHA-256: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`.
Split seeds: `[13, 29, 47]`, shared permutation seed: `751`.

| Model | Excess pair interaction: full minus no-TTL (mean pp) | Clean FPR: full minus no-TTL (mean pp) | Same effect sign all splits? |
|---|---:|---:|---|
| Logistic Regression | -0.181 | -0.948 | No |
| Random Forest | -0.319 | -0.048 | Yes |

## What the comparison establishes

Models were **retrained** using full or TTL-removed predictor sets on identical
group-held-out training/validation split indices. Positive interaction contrast
means the original full-feature model had a larger nonadditive pair effect than
the TTL-removed model under this synthetic experimental procedure.

## What it does not establish

- Excluding TTL features changes model fitting and is not a causal intervention on real traffic.
- These split seeds share the same source data and are not independent populations.
- The joint row permutations can generate physically unrealistic cross-feature combinations.
- This was designed after the relevant feature pair was identified; selection bias matters.
- No verified first-in-world novelty, external deployment quality or guarantee of low false alarms.

Use `results/ttl_retraining_ablation.json` for all individual model/split metrics and raw contrasts.
