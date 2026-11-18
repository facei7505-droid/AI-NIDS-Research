# Reproducibility challenge: Failure Fingerprints interaction sign stability

**Evidence reviewed 18 November 2026. Exploratory interpretation, not a confirmatory novelty result.**

## Motivation

The original training-only Failure Fingerprints experiment reported a mean **+1.796 percentage point excess false-positive interaction** for Random Forest under jointly permuted Protocol and Context groups, across split seeds 13, 29 and 47. This represented *synthetic* perturbation sensitivity, not causal attribution.

The later matched TTL-retraining ablation reused those grouped split seeds but changed the feature-block permutation seed and explicitly compared independently retrained models **with versus without TTL-related fields**. The identical core Protocol/Context pair under the full model yielded **negative**, not positive, excess FPR interactions.

## Reproducible observations

| Analysis | RF excess pair FPR, seed 13 | seed 29 | seed 47 | Mean |
|---|---:|---:|---:|---:|
| Initial full Protocol + Context, permutation tied to split seeds | +1.773 pp | +1.905 pp | +1.711 pp | **+1.796 pp** |
| Retrained-ablation full features, Protocol core + Context core, perturb seed 751 | −0.324 pp | −0.190 pp | −0.262 pp | **−0.259 pp** |
| Retrained-ablation without TTL, Protocol core + Context core, perturb seed 751 | −0.054 pp | +0.289 pp | −0.054 pp | **+0.060 pp** |

**Important: these conditions are NOT directly equivalent.** The original Protocol/Context pair includes TTL-related features; the later Protocol *core* and Context *core* pair excludes TTL features from perturbations, even when the full model was trained with TTL. The experiment therefore changes the perturbed feature definitions **and** the permutation seed. It cannot attribute the difference solely to the random seed or to TTL removal. Future verification should hold the *same feature groups*, learned model, perturbation severity and donor policy fixed while varying only one factor.

The within-core, matched-comparison second experiment gives more interpretable contrasts:
- RF full model core interaction: mean −0.259 pp.
- RF retrained without TTL core interaction: mean +0.060 pp.
- Paired full-minus-no-TTL difference: mean **−0.319 pp** across the three reused split seeds.

The matched result is post-hoc, and three correlated split seeds do not establish independent population uncertainty.

## What the current evidence does and does not support

**Supports:** feature-perturbation conclusions can depend substantially on experimental design. Control experiments are necessary before treating large group interactions as stable mechanisms.

**Does not support:** claiming a new algorithm, first-in-world discovery, proof of TTL causality, physical network robustness, or a statistically significant general statement about network shifts.

## High-priority falsification controls

1. **Donor class mixing:** compare globally permuted feature blocks to label-conditioned within-class donor blocks, with identical split and group-specific mask rules. The within-class donor procedure uses true labels only in offline diagnostics, never model training or deployment. See `src/class_mixing_control.py`.
2. **Permutation-seed sensitivity:** repeat the *same complete Protocol+Context perturbation* for a range of independently fixed seeds; report every seed, not merely the best outcome.
3. **Factorial TTL attribution:** compare core-group perturbation across full and independently retrained no-TTL models while keeping fixed training split indices and perturbation masks.
4. **Physical constraints:** test perturbations preserving meaningful network-flow consistency instead of interpreting arbitrary cross-group swaps as realizable packets.
5. **External confirmation:** register the intended predictor mapping and metrics before accessing a new untouched corpus.

## Evidence files

- `results/failure_fingerprints.json` — original 66 training-only conditions and 36 interactions.
- `results/ttl_retraining_ablation.json` — executed 48-case paired full/no-TTL training-only ablation.
- `src/ttl_retraining_ablation.py` — experimental protocol and split pairing.
- `src/class_mixing_control.py` — class-matched donor design, created 18 November 2026; no quantitative claim until executed output appears.

## Integrity statement

This discussion was AI-assisted, and claims are limited to the exact values in published GitHub data. Differences between experiments cannot be assigned to individual causes without single-factor comparisons.

## Observed class-mixing control — 18 November 2026

The subsequent **executed training-only donor-policy comparison** (`results/class_mixing_control.json`) held the feature groups, models, split seeds and perturbation fraction fixed while comparing unrestricted donors versus same-class donors:

| Model | Global donor policy: mean excess FPR | Same-class donor policy: mean excess FPR | Paired difference |
|---|---:|---:|---:|
| Random Forest | +1.660 pp | −0.277 pp | **+1.937 pp** |
| Logistic Regression | +0.307 pp | +0.289 pp | **+0.018 pp** |

All numbers are **descriptive** means across grouped split seeds 13, 29 and 47. The shift was much larger for RF, while LR showed little change. This is a falsification-style observation about the *experimental permutation methodology*, not proof that cross-class mixing uniquely caused the result.

Reproducible evidence: `results/class_mixing_control.json`, `results/class_mixing_analysis.json`, and `results/CLASS_MIXING_ANALYSIS.md`.

### Further replication now specified

The post-hoc next phase is a full factorial **fixed-model, repeated-permutation-seed** experiment (`src/permutation_seed_replication.py`). It has 3 grouped split seeds × 5 independent permutation seeds × 2 models × 2 donor policies = 60 paired setting records. All outcomes must be reported, including seed-level reversals.

The new outcome is **pending** until the corresponding CI workflow publishes `results/permutation_seed_replication.json`. Even if all 5 perturbation seeds agree, this does not imply independent network population replication or a first-in-world discovery.
