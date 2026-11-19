# Frozen versus validation-fitted donor quantiles

**Executed post-hoc paired comparison**, using stored measurements only.

Input training SHA-256: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`. Matched cells: **54**.

| Model | Policy | Validation-fit interaction (pp) | Train-fit interaction (pp) | Change (pp) |
|---|---|---:|---:|---:|
| Logistic Regression | global | +0.337 | +0.337 | +0.000 |
| Logistic Regression | observable_strata | +0.221 | +0.213 | -0.008 |
| Logistic Regression | same_class_oracle | +0.309 | +0.309 | +0.000 |
| Random Forest | global | +1.610 | +1.610 | +0.000 |
| Random Forest | observable_strata | +0.959 | +0.959 | +0.000 |
| Random Forest | same_class_oracle | -0.219 | -0.219 | +0.000 |

## Interpretation

Only the construction of observable matching bins changes between these paired sets of model/policy/seed conditions. Large changes would indicate unwanted transductive sensitivity. Near-zero differences indicate that this **particular** binning choice did not substantially alter the historic training-only result.

## Limitations

- A training-fitted quantile rule avoids learning bin boundaries from held-out validation covariates, although donors still come from the validation batch.
- These synthetic permutations do not establish causal network behavior.
- All experimental folds are correlated because they reuse one historical dataset.
- Same-class donor selection is a label-oracle retrospective diagnostic only.
- The Protocol/Context comparison was selected after other exploratory findings.

No independent dataset was tested, and no novelty priority is claimed.
