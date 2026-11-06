# Executed false-alarm-budget transfer analysis

**Exploratory, not preregistered independent confirmation.** Derived from hash-identified executed `results/alert_budget_study.json`. This study is post-hoc relative to the previously inspected designated test set.

Target validation FPR: **5.00%**. Official held-out test size: **82,332**, non-overlap test rows **73,791**.

| Model | Subset | Default FPR | Constrained FPR | FPR budget overshoot | Constrained Recall | Recall cost | False alarms avoided | Extra missed attacks |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Majority Dummy | official_test | 100.00% | 0.00% | -5.00 pp | 0.00% | 100.00 pp | 37,000 | 45,332 |
| Majority Dummy | nonoverlap_test | 100.00% | 0.00% | -5.00 pp | 0.00% | 100.00 pp | 35,528 | 38,263 |
| Logistic Regression | official_test | 39.14% | 11.41% | +6.41 pp | 86.71% | 10.59 pp | 10,261 | 4,799 |
| Logistic Regression | nonoverlap_test | 39.35% | 10.66% | +5.66 pp | 84.30% | 12.52 pp | 10,196 | 4,792 |
| Random Forest | official_test | 28.62% | 14.54% | +9.54 pp | 95.32% | 3.53 pp | 5,210 | 1,598 |
| Random Forest | nonoverlap_test | 28.39% | 14.15% | +9.15 pp | 94.50% | 4.16 pp | 5,060 | 1,593 |

## 95% Wilson intervals for test FPR

- Majority Dummy, official_test: 0.00%, interval [0.00%, 0.01%], benign n=37,000.
- Majority Dummy, nonoverlap_test: 0.00%, interval [0.00%, 0.01%], benign n=35,528.
- Logistic Regression, official_test: 11.41%, interval [11.09%, 11.74%], benign n=37,000.
- Logistic Regression, nonoverlap_test: 10.66%, interval [10.34%, 10.98%], benign n=35,528.
- Random Forest, official_test: 14.54%, interval [14.18%, 14.90%], benign n=37,000.
- Random Forest, nonoverlap_test: 14.15%, interval [13.79%, 14.52%], benign n=35,528.

## Scientific interpretation

- The validation-selected 5% alarm budget **failed to transfer** to the designated test for both learned models. Do not claim it met the target.
- Tighter thresholds trade fewer false alarms for more missed attacks; the exact observed costs are shown above.
- Non-overlap results are a sensitivity analysis, not an independent randomly collected external validation set.
- Intervals assume independent test rows and ignore dependence and prior test inspection. They are descriptive, **not** confirmatory evidence of an original method.
- No real-network deployment, new-attack robustness or globally novel finding is established here.

Source: `results/alert_budget_study.json`. Analysis implementation: `src/analyze_alert_budget.py`.
