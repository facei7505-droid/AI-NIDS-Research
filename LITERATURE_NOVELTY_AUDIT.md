# Novelty audit — Failure Fingerprints (6 Nov 2026)

**Status:** targeted preliminary literature audit; NOT a systematic review or proof of first-in-world priority. Searches should be repeated with formal inclusion/exclusion criteria, citation chaining, and scholarly indexes before publication.

## What already exists

| Prior work | Relevance | What we must NOT claim |
|---|---|---|
| Abdelaziz et al., *Enhancing Network Threat Detection with Random Forest-Based NIDS and Permutation Feature Importance*, Journal of Network and Systems Management (published Oct 2024). https://doi.org/10.1007/s10922-024-09874-0 | Permutation analysis of NIDS features is not novel. | That introducing permutation importance to network intrusion detection is new. |
| *Formally Verifying Robustness and Generalisation of Network Intrusion Detection Models*, ACM SAC 2025. https://doi.org/10.1145/3672608.3707927 | Natural perturbations, generalisation and robustness have been studied. | That studying feature perturbations in NIDS is new. |
| Gabriška et al., *Random Forest-Based Network Intrusion Detection with Feature Selection and Class Balancing on UNSW-NB15 Traffic*, Information (2026), 17(9), 836. https://doi.org/10.3390/info17090836 | Attack-specific RF, feature selection and false-alarm tradeoffs already investigated. | That RF ablation and false alarms on UNSW-NB15 are unexplored. |
| *Robustness-Aware Machine Learning for Network Intrusion Detection under Feature and Distribution Variations Using UNSW-NB15*, IJSMR (2025). https://doi.org/10.37502/IJSMR.2025.81218 | Feature perturbation, reduction, and distribution shifts on UNSW-NB15 exist. | That UNSW-NB15 perturbation robustness is a fresh research branch. |
| Ologunde, *Reading the Testbed: How Three TTL Features Make Network Intrusion Detection on UNSW-NB15 Look Solved*, ResearchGate preprint (Aug 2026). https://doi.org/10.13140/RG.2.2.21500.30087 | A particularly relevant *non-peer-reviewed* claim about TTL feature shortcut and group ablation. Must replicate independently and distinguish features. | That discovering TTL-related testbed confounding or group ablation is inherently our first discovery. |

These citations provide background/context, **not** a complete novelty determination. Verify individual bibliographic metadata against the publisher and check newer papers, preprints, and methods in adjacent areas (model interpretation, functional ANOVA, interaction importance, conditional permutation importance).

## Current unique question candidate

For a fixed feature-group partition (timing, volume, protocol, context), evaluate **non-additive false-positive-rate interaction** under jointly permuted feature blocks, with matched group-level randomness and duplicate-group training/validation split. Study whether effect sign and magnitude persist under changes of random split, perturbation severity, perturbation mechanism, model family and external datasets.

Crucially, combinations of existing methods do not automatically constitute novelty; publish the question as **research candidate** rather than an original algorithm.

## Existing observation (training-only results, exploratory)

The executed three-seed study found that Random Forest protocol+context excess FPR was positive in all three group-held-out splits, with a mean increase of about **1.80 percentage points** (individual values about 1.77, 1.91, 1.71). This is a preliminary model sensitivity signal, **not independent replication**. Three overlapping training resamples cannot establish significance or deployment consequences.

## Important confounders

1. The `protocol` group includes TTL-associated attributes (`sttl`, `dttl`) and `context` includes `ct_state_ttl`. Their interaction may be driven by preexisting testbed shortcuts. Future analysis should separate these explicitly, especially in light of the 2026 TTL preprint.
2. Swapping group values across arbitrary rows may violate physical consistency of network flows. Conclusions must be limited to synthetic sensitivity.
3. Four groups were manually defined; alternative groupings can change interactions. Group partition is a researcher choice, not discovered ground truth.
4. Split-seed stability is not independent-dataset stability. Multiple tested pairs also invite selection bias.
5. No untouched independent dataset is available in our current evidence set.

## Falsifiable next steps

- Study **dose response** on the training split with perturbation fractions 0.10, 0.25 and 0.50, use prespecified independent corruption seeds, and report all conditions.
- Break the highest observed interaction into TTL-related and non-TTL fields to test whether that shortcut alone explains the effect.
- Compare against the alternative null control of independent marginal column shuffling and, where possible, physical-validity-constrained perturbations.
- On a completely untouched external corpus, harmonize feature definitions, repeat split/hyperparameter controls and compare to published group interaction methods.
- Maintain versioned source searches and distinguish first hypothesis registration from post-hoc selection of a leading pair.

## Research ownership

The current software, literature scan and manuscript are AI-assisted. A human investigator must check the citations, independently replicate analyses, question assumptions, and disclose tool use appropriately. Neither a 9–10 rating nor a scientific discovery can be promised before evidence and independent review.
