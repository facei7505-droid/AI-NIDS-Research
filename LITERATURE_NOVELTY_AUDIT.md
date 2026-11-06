# Literature and novelty audit — Failure Fingerprints

**Updated 2026-11-06. Preliminary evidence search, not a systematic review.**

## Verified relevant publications and context

| Source | Overlap with this project | Implication |
|---|---|---|
| Gabriška et al. (2026), *Random Forest-Based Network Intrusion Detection with Feature Selection and Class Balancing on UNSW-NB15 Traffic*, Information, 17(9), 836. https://doi.org/10.3390/info17090836 | RF, feature selection, false alarms and class balancing on UNSW-NB15. | We cannot claim to introduce RF feature study or confusion-matrix-driven false-alarm analysis. |
| *Reliability auditing of explanations for machine-learning-based intrusion detection systems* (2026), Journal of Computer Virology and Hacking Techniques. https://link.springer.com/article/10.1007/s11416-026-00664-7 | SHAP vs permutation importance on UNSW-NB15; model explanation stability. | Permutation as an explanation/evaluation method is established. |
| *An Explainable and Interpretable GNN Based on Temporal Time Series: An IDS Approach* (2026), Electronics, 15(17), 3764. https://www.mdpi.com/2079-9292/15/17/3764 | Notes that TTL-related UNSW-NB15 attributes may reflect testbed-specific shortcuts, not genuine transferable threat signals. | Our observed protocol/context effects might be driven by TTL-associated features; study them explicitly. |
| Shrestha (2026), *Machine Learning-Driven Network Anomaly Detection: An Empirical Study Using Isolation Forest and Random Forest on the UNSW-NB15 Benchmark*. https://ausjournal.com/index.php/j/article/view/92 | Reports high discriminative influence of TTL and flow-rate attributes. | TTL/flow-rate dependence is already known in related studies. |
| Mishra & Mishra (2026), *When Cost-Sensitive Thresholds Fail to Transfer: A Leakage-Controlled Evaluation of Network Intrusion Detection on UNSW-NB15*. https://www.jetir.org/view?paper=JETIR2610258 | Threshold/cost transfer failures studied on the same benchmark. | Earlier alert-budget transfer results cannot be treated as a novel topic in isolation. |

These sources have different methodological quality and are **not** equivalent independent replications. Bibliographic metadata should be rechecked at the publisher when preparing a submission. A systematic search should cover grouped/conditional permutation, functional ANOVA interactions, data-drift sensitivity, and multiple hypothesis correction.

## Measured preliminary result

The initial `results/failure_fingerprints.json` contains 66 training-only validation conditions and 36 pair-interaction records from 3 group-held-out split seeds.

For **Random Forest + Protocol/Context**, excess FPR interaction equals approximately **+1.773, +1.905, +1.711 percentage points** for split seeds 13, 29 and 47, with mean **+1.796 pp**. This means the combined synthetic permutation had more impact on FPR than the sum of the separately permuted groups under this experimental definition.

**This is not a first-in-world discovery or independently replicated result.** The three split seeds reuse the same training corpus and the group construction was researcher-defined.

## Next falsifiable analysis: TTL-shortcut decomposition

Protocol includes `sttl` and `dttl`, while Context includes `ct_state_ttl`. These variables have known UNSW-NB15 testbed relevance, so it would be scientifically misleading to infer the group interaction is a new network phenomenon without removing or isolating them.

The follow-up `src/ttl_decomposition.py` measures synthetic sensitivity using TTL-only, protocol without TTL, context without TTL, paired core groups and complete protocol/context groups, over 3 predefined validation seeds and 2 independent perturbation seeds. This follow-up was designed *after* observing the first protocol+context result; it is explicitly **post-hoc exploratory analysis**.

If protocol-core+context-core remains similar in magnitude after excluding TTL features, TTL shortcut alone cannot fully account for the observed interaction under this perturbation. If effect disappears, the shortcut hypothesis becomes more plausible. **Neither outcome proves causality** without more controls and external validation.

## Main limitations and standards

- Group permutations can violate feature constraints and represent unrealistic flows.
- Split-seed stability is not new-network generalization.
- The study has multiple tested group pairs and models, requiring transparency about selection and statistical uncertainty.
- A cross-dataset evaluation would require feature harmonization, fully untouched data and a written protocol before labels are opened.
- An original contribution requires a careful systematic comparison with prior literature and new reproducible results, not a novel-sounding title.
- Software and draft text have substantial AI assistance; the human student's independent contributions and methodological understanding must be accurately represented.

## Sources

Publisher and article landing pages linked in the table. Original baseline data and numerical outputs are tracked separately in `results/`, along with input hashes.
