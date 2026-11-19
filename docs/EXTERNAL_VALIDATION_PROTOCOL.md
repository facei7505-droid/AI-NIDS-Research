# Untouched external validation protocol: CIC-IDS2017 / CSE-CIC-IDS2018

**Protocol drafted 19 November 2026, before any external dataset result is included in this repository.**
Status: **DESIGN ONLY — NO EXTERNAL EXPERIMENT COMPLETED OR CLAIMED.**

## Source and provenance

1. **CIC-IDS2017** primary source: Canadian Institute for Cybersecurity, University of New Brunswick: https://www.unb.ca/cic/datasets/ids-2017.html . The official release includes labeled network flows and machine-learning CSV files generated with CICFlowMeter.
2. **CSE-CIC-IDS2018** official description: https://www.unb.ca/cic/datasets/ids-2018.html ; official public cloud registry: https://registry.opendata.aws/cse-cic-ids2018/ . Release includes flow records extracted using CICFlowMeter-V3.
3. Access original source or verifiable official distribution. Record file name, URL, retrieval UTC time, SHA-256, row counts, field names, software and license terms. **No external input has been downloaded, hashed, or evaluated by this protocol.**

## Why source and target are not directly interchangeable

UNSW-NB15 was extracted with a different flow representation from CICFlowMeter datasets. UNSW's **Protocol group** includes `sttl`, `dttl`, `stcpb`, `dtcpb`, `service` and `state`; its **Context group** includes `ct_state_ttl` and windowed connection-count attributes (`ct_*`). These do not generally have identical definitions or one-to-one corresponding CIC-IDS2017 machine-learning CSV columns.

**Do not** map `ct_state_ttl` to arbitrary CIC counters, silently fill absent group columns with zero, apply unrelated feature importances, or label different feature groups as a direct replication of the original Protocol+Context interaction.

## Required design before touching external target labels

- **Pre-register one testable, cross-dataset hypothesis:** donor selection policy changes measured nonadditive FPR interactions under synthetic perturbations, and magnitude differs by classifier. This must be tested on a *semantically harmonized* pair of feature groups available in each dataset.
- Establish the **same conceptual groups in both datasets** using only genuinely matching flow characteristics. Candidate shared fields *for manual unit and definition verification*, not yet an approved map:
  - Duration: UNSW `dur` (seconds) vs CIC `Flow Duration` (typically microseconds; verify source documentation and units).
  - Packet counts: UNSW `spkts` / `dpkts` vs CIC `Total Fwd Packets` / `Total Backward Packets`; verify source/destination orientation and semantics.
  - Volume: UNSW `sbytes` / `dbytes` vs CIC `Total Length of Fwd Packets` / `Total Length of Bwd Packets`; verify header, payload, and direction accounting.
  - Rates: UNSW `rate` vs CIC `Flow Packets/s`; verify calculation and exclusion rules before use.
- If fewer than two non-overlapping conceptually comparable feature groups remain, **declare the intended cross-dataset interaction untestable**. Do not quietly switch the hypothesis post-hoc.
- Define binary labels BENIGN=0 vs all attacks=1 with documented multi-label mapping and missing/unknown cases. Avoid data leakage from label-bearing columns or filenames.
- Preserve CIC day/session/file boundaries. Split by acquisition day, source network, or independent environment where metadata permit. **Do not use random record splits as a substitute for time-separated or network-separated confirmation.**
- Select model settings and perturbation fraction on **UNSW training data only**. All feature scaling must be fitted only on the applicable model's training partition.
- Apply only **class-blind donor policies** in the primary prospective comparison. The label-oracle policy is a retrospective upper-bound diagnostic, not the main deployable comparator.
- Report class prevalences, FPR, recall, false positives, false negatives, pair interaction, donor exchange fraction, and runtime for every test condition, including failures.
- Provide a numerical uncertainty model accounting for correlated flows/sessions; rows are not independent Bernoulli samples.
- Stop and explicitly report incompatibility, unexpected feature units, incomplete provenance or attack-label ambiguity rather than coercing the results.

## Primary and negative outcomes

The primary statistic is paired **global donor minus observable-matched donor** excess FPR interaction for the chosen *shared* conceptual groups (same model, split, fraction, and random mask). Report model-specific outcomes and sign consistency across independent units (days/networks), not only multiple permutations on one day.

A positive difference that survives the new dataset supports a claim about **methodological sensitivity of measured NIDS feature interactions across datasets**. A zero, negative or inconsistent difference **refutes external transfer** under that design. The within-class oracle is permitted solely to investigate potential mechanisms after the primary claim is evaluated.

This is **not** a novel conditional permutation algorithm. Prior literature on conditional permutation, feature dependencies, benchmark bias and NIDS data leakage must be matched against the study. A single additional synthetic dataset does not prove real-world deployment protection.

## Integrity gates

1. Register all final group definitions, units, feature conversion formulas, label mapping and independent holdout unit before opening external target labels.
2. Hash all input files and archive a *read-only protocol version* with a commit SHA.
3. Capture tests for absent columns, invalid numeric values, inconsistent labels, data overlap and chronological leakage.
4. Freeze the training and perturbation code and baseline comparisons.
5. Evaluate once on external test data; publish **all outcomes** without threshold selection on that test.
6. Cite official dataset documentation and reveal substantial AI assistance.

If these gates cannot be met, preserve current project originality as an exploratory finding rather than claiming a 9/10 scientific contribution.
