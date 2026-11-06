# Failure Fingerprints: training-only exploratory results

**No official test data were used in this experiment.** The same
official training dataset is repeatedly split, so seeds are not
independent populations. Results do not establish novel scientific discovery.

- Input SHA-256: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`
- Grouped validation seeds: `[13, 29, 47]`
- Perturbed-row probability: `0.25`

## Mean changes relative to clean validation (percentage points)

```
              model        condition  mean_fpr_increase_pp  sd_fpr_increase_pp  mean_recall_loss_pp  sd_recall_loss_pp  repeats
Logistic Regression            clean                 0.000               0.000                0.000              0.000        3
Logistic Regression          context                -0.116               0.469                1.811              0.177        3
Logistic Regression         protocol                 6.402               0.136                6.468              0.283        3
Logistic Regression protocol+context                 6.596               0.202                8.153              0.226        3
Logistic Regression           timing                 0.268               0.018               -0.073              0.044        3
Logistic Regression   timing+context                 0.160               0.421                1.694              0.119        3
Logistic Regression  timing+protocol                 6.625               0.158                6.429              0.310        3
Logistic Regression    timing+volume                -0.502               0.046                3.443              0.152        3
Logistic Regression           volume                -0.887               0.102                3.620              0.176        3
Logistic Regression   volume+context                -0.514               0.490                5.325              0.084        3
Logistic Regression  volume+protocol                 6.385               0.159                9.667              0.227        3
      Random Forest            clean                 0.000               0.000                0.000              0.000        3
      Random Forest          context                 2.061               0.198               -0.252              0.098        3
      Random Forest         protocol                 3.996               1.276                5.013              0.556        3
      Random Forest protocol+context                 7.854               1.357                5.179              0.671        3
      Random Forest           timing                 0.833               0.361                0.010              0.081        3
      Random Forest   timing+context                 2.569               0.265                0.184              0.163        3
      Random Forest  timing+protocol                 5.913               1.014                5.129              0.405        3
      Random Forest    timing+volume                 2.795               0.329                0.112              0.480        3
      Random Forest           volume                 2.223               0.489               -0.120              0.421        3
      Random Forest   volume+context                 4.269               0.480               -0.188              0.515        3
      Random Forest  volume+protocol                 7.336               1.673                5.215              0.473        3
```

## Pairwise excess changes (joint effect minus sum of single-group changes)

```
              model             pair  mean_excess_fpr_pp  sd_excess_fpr_pp  mean_excess_recall_loss_pp  repeats
Logistic Regression protocol+context               0.309             0.253                      -0.126        3
Logistic Regression   timing+context               0.009             0.059                      -0.044        3
Logistic Regression  timing+protocol              -0.045             0.009                       0.035        3
Logistic Regression    timing+volume               0.117             0.047                      -0.104        3
Logistic Regression   volume+context               0.490             0.090                      -0.107        3
Logistic Regression  volume+protocol               0.870             0.176                      -0.421        3
      Random Forest protocol+context               1.796             0.099                       0.418        3
      Random Forest   timing+context              -0.325             0.193                       0.427        3
      Random Forest  timing+protocol               1.083             0.082                       0.107        3
      Random Forest    timing+volume              -0.261             0.215                       0.223        3
      Random Forest   volume+context              -0.015             0.208                       0.184        3
      Random Forest  volume+protocol               1.117             0.173                       0.323        3
```

A positive excess FPR indicates the joint perturbation raised false alarms
more than the sum of the two separate perturbation effects.
Negative excess FPR shows subadditivity. Signs must not be confused
with causality, statistical significance or robustness to real-world shifts.

## Interpretation limitations

- Only the official training CSV is used, never the official test CSV.
- Validation groups are separated by predictor fingerprints; not temporal or independent-network separation.
- A joint shuffle preserves within-group values, but can create physically impossible cross-group feature combinations.
- Changes in performance are sensitivity diagnostics, not causal feature attribution.
- Paired-group interaction is delta(A+B)-delta(A)-delta(B), using clean validation metric as reference.
- A replication or novelty claim requires external untouched data and literature comparison.
- The fixed score cutoff of 0.5 and the synthetic transformation design can affect conclusions.
- Multiple group pairs, seeds, and models are evaluated; do not select only flattering results.
- Repeated validation splits share many training events and therefore do not form independent samples.
- Requires external data, stronger uncertainty analysis and literature comparison before novelty claims.
