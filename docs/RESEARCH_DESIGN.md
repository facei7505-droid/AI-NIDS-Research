# Research design and evidence boundaries

_Last updated: 8 November 2026 (Asia/Almaty)._

## Central question

**When does feature-group interaction amplify false alarms in lightweight network intrusion detection, and do apparent interactions survive shortcut-feature controls and independent evaluation?**

This is a falsifiable *research question*, not a claim to have discovered a novel algorithm.

## Experimental phases

| Phase | Data boundary | Evidence status | Endpoint |
| --- | --- | --- | --- |
| A. LR, RF and majority-class baselines | Official UNSW-NB15 train/test | Executed | Binary F1, recall, false-positive rate, average precision |
| B. Duplication and label disagreement audit | Official train/test | Executed (fingerprint screening only) | Overlap counts and contradictory feature groups |
| C. 5% false-alarm-budget validation | Group-held-out training validation; official test reused | Executed **exploratory** | Frozen-threshold FPR/recall, including unmatched test subgroup |
| D. Failure Fingerprints | **Only official training split**; group-held-out folds | Executed exploratory | Single-group and pairwise excess FPR/recall loss |
| E. TTL shortcut decomposition | **Only official training split** | Executed, post-hoc exploratory | 60 perturbation conditions; compare TTL-only vs TTL-excluded Protocol/Context effects |
| F. Independent replication | Untouched external data | **Not performed** | Confirmation of transferability and scientific novelty |

## Frozen feature-group protocol (Failure Fingerprints)

- Groups: Timing, Volume, Protocol, Context. Definitions are in `src/failure_fingerprints.py`.
- Split seeds: `13, 29, 47`, 80/20 group-held-out training/validation; record matching on predictor fingerprints is used to create groups.
- LR and RF; negative-control dummy is intentionally omitted from feature sensitivity.
- A random 25% of validation rows are perturbed by *jointly permuting* feature values within each predefined group. This preserves the permuted block's internal co-occurrence but **not** physical consistency across groups.
- Test all four single groups and six group pairs, without omitting small or negative effects.
- Pair interaction is `FPR(A+B) - FPR(A) - FPR(B) + FPR(clean)`, reported in percentage points; repeat for recall loss.
- Repeat split seeds are **not independent datasets**. Do not interpret low standard deviations as proof of real-world generalization.

## Post-hoc TTL decomposition

After observing RF Protocol + Context excess FPR, we identified a plausible dataset-specific confounder: `sttl`, `dttl`, `ct_state_ttl`. The study contrasts TTL-only, Protocol without TTL, Context without TTL, both cores jointly, and both complete blocks. This follow-up was designed **after seeing the leading pair** and must never be described as prospective confirmation.

## Threats to validity

1. UNSW-NB15 contains fingerprint overlap and contradictory labels across predictor-identical records; these counts require source-level confirmation.
2. Group-permuted features may violate causal/physical network constraints.
3. Multiple comparisons across groups, models, corruption mechanisms and seeds invite selective reporting.
4. The official test split was inspected before the 5% false-alarm study; that study is exploratory.
5. Row-level uncertainty assumes independent flows and ignores network/session correlation.
6. Models do not demonstrate zero-day detection, contemporary traffic performance or deployment readiness.
7. External, untouched network data must be obtained and an evaluation protocol frozen before labels are inspected.

## Authorship and integrity

Code and writing are substantially AI-assisted. The human investigator must personally verify figures, rerun the experiments, check bibliography details, defend the choices and disclose assistance. Unverified claims of first-in-world novelty, peer review, real-world protection or guaranteed admissions must not appear in the manuscript.

## Falsification: class-mixing permutation control (18 November 2026)

The initial Failure Fingerprints permutation study drew replacement feature blocks from arbitrary validation rows. This can **mix attack-labelled and normal-labelled traffic**, possibly making group interaction estimates reflect out-of-distribution synthetic combinations rather than a stable model failure.

A later exploratory diagnostic, `src/class_mixing_control.py`, pairs two synthetic perturbation regimes:

1. **Global block shuffling** within each predefined Protocol/Context group (original style).
2. **Within-class block shuffling**, where donors for each validation row come from the *same ground-truth class*.

Both regimes use the same grouped fit/validation split indices (13, 29, 47), trained model, perturbation fraction (.25), and group-specific random mask rules. All clean/single/joint conditions are preserved. The official designated test set is **never loaded**.

**Predefined interpretation rules before looking at this experiment's outcome:**

- If positive excess FPR seen in global permutations becomes near zero or negative under within-class shuffling, this supports the **alternative explanation** that artificial class mixing contributes materially to the measured interaction. It does not prove its unique cause.
- If the sign and sizable effect persist in within-class shuffling, simple label mixing cannot completely explain the measured synthetic sensitivity, but neither causal attribution nor generalization has been demonstrated.
- If the effect changes sign across split seeds, report instability and refrain from promoting the interaction as an established mechanism.
- Do not choose only the most flattering model or subgroup. Include the full 3-seed × 2-model × 2-mode set.
- Using true labels to choose donors is valid **only as a retrospective offline diagnostic**. It is not an available operation at intrusion-detection inference time, and it would be target leakage if used in a deployed algorithm or predictor fitting.
- This experiment was conceived after inspecting the earlier Protocol+Context result, and is therefore **post-hoc exploratory**, not preregistered independent confirmation.

This diagnostic compares synthetic regimes; it is not physically constrained traffic simulation, validation on another network, or proof of first-in-world scientific novelty. The result remains pending until `results/class_mixing_control.json` is published from an executed and validated workflow.


## Three-way donor-policy falsification control — 18 November 2026

**Exploratory extension selected after inspecting earlier class-mixing results.** Hypothesis: the excess Protocol+Context FPR estimated with unrestricted feature-block shuffling will be greater than estimates when donors are selected from similar observed traffic, and the effect may differ by model family.

### Defined experiment

- Data: only original pinned 175,341-row UNSW-NB15 **training CSV**, no official test labels.
- Group-held-out fit/validation split seeds: 13, 29, 47.
- Model families: Logistic Regression and Random Forest.
- Separate donor-permutation seeds: 101, 211, 307.
- Predefined perturbation fraction: 25% of validation rows, preserving within-group column blocks.
- Groups: Protocol and Context as previously specified.
- **Global donors:** all selected rows are candidate sources.
- **Observable-stratified donors:** use only the unperturbed numeric predictors `dur` and `sbytes`, separated into up to three quantile bins per feature. No class labels are used for stratification. This is a *transductive evaluation diagnostic*, not a production-trained donor sampler.
- **Same-class oracle donors:** use known labels to choose sources, strictly as an offline diagnostic; this policy would leak targets if used at inference.
- Outcomes: excess FPR interaction defined as `100*(FPR_joint-FPR_protocol-FPR_context+FPR_clean)`, together with clean/joint FPR and recall, group-specific exchange rates and split/seed provenance.
- Planned factorial records: 3 split seeds × 3 donor seeds × 2 model families × 3 donor policies = **54**.

### Interpret all outcomes, not selected examples

- A global > observable-stratified contrast is consistent with unrestricted donor shuffling generating stronger synthetic artifacts, **not proof of causation**.
- A difference between observable-stratified and oracle control may reflect remaining class-dependent information not captured by the two matching attributes; it also may reflect variable exchange rates or sparse strata.
- If differences disappear or reverse, report the failure as evidence against the proposed interpretation rather than hiding it.
- The true deployment operating point or real network-shift response cannot be established from any of these synthetic controls.
- Different donor strata may have different swap counts; comparisons must report `joint_group_exchange_rate` and, ideally, include a matched effective-exchange-rate sensitivity check.
- Repeat all results on a previously untouched external corpus before claiming generalizable NIDS failure modes. Prior research on conditional permutation already exists; this is not a claim to invent conditional feature importance.

Evidence is considered executed only when `results/observable_donor_control.json` is produced by a successful workflow and its provenance and full design are checked. AI-assisted design and coding must be disclosed.
