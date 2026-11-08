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
