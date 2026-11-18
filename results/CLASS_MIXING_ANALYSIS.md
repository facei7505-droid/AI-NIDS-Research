# Executed class-mixing falsification analysis

**Exploratory, official UNSW-NB15 training split only.** All rows derived from [the versioned experiment JSON](class_mixing_control.json), not invented.

| Model | Global excess FPR | Within-class excess FPR | Paired global − within-class | Same sign across splits? |
|---|---:|---:|---:|---|
| Logistic Regression | +0.307 pp | +0.289 pp | +0.018 pp | No |
| Random Forest | +1.660 pp | -0.277 pp | +1.937 pp | Yes |

## All paired differences

- **Logistic Regression:** seed 13: +0.027 pp; seed 29: +0.090 pp; seed 47: -0.063 pp.
- **Random Forest:** seed 13: +2.151 pp; seed 29: +1.950 pp; seed 47: +1.711 pp.

## Interpretation

Global permutations sample both attack and benign rows as donors; within-class permutations use true class labels **only for an offline diagnostic**. The differences suggest the feature interaction estimate is **sensitive to donor-selection policy**, not that a new intrusion mechanism was discovered. Because the prior experiment first motivated the chosen Protocol/Context pair, this is post-hoc rather than independent confirmation.

## Limitations

- Ground-truth class labels define the within-class permutation donor pool. This is an offline diagnostic, not an inference-time operation.
- The mean paired difference is not a formal inferential effect estimate across independent networks.
- The sample contains just three overlapping training-held-out splits; no independent dataset replication.
- Global permutation mixes labels and can generate physically inconsistent joint feature values.
- The Protocol+Context pairing was chosen after inspecting earlier effects: all findings are post-hoc exploratory.
- A shift in nonadditive excess FPR is not proof that class mixing is the unique cause of differences.

**Next:** replicate with multiple independent permutation seeds, matching group definitions, a physical-validity-constrained null, and untouched external data.
