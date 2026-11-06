# Executed benchmark (see artifacts)

## Binary classification
```
              model  train_rows  test_rows  precision   recall       f1  average_precision  balanced_accuracy  false_positive_rate  false_negative_rate  inference_ms_per_1000  fit_seconds    tn    fp   fn    tp
     Majority Dummy      175341      82332   0.550600 1.000000 0.710177           0.550600           0.500000             1.000000             0.000000               1.925059     0.826012     0 37000    0 45332
Logistic Regression      175341      82332   0.753645 0.972580 0.849229           0.966105           0.791533             0.389514             0.027420               2.151837     4.346724 22588 14412 1243 44089
      Random Forest      175341      82332   0.809649 0.988485 0.890174           0.987018           0.851878             0.284730             0.011515              10.595273   109.222080 26465 10535  522 44810
```

Stress-test rows: 39
Synthetic stress tests cannot verify performance on new real attacks.
See data_audit.json for cross-split overlap and conflicting-label warnings.
