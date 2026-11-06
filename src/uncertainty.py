"""Statistical utilities for binary offline classification research.

Only evaluate predictions from frozen, held-out models. All bootstrapping here
resamples test rows; it does not account for dataset or training instability.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score


def binary_metrics(y_true, y_pred) -> dict:
    truth = np.asarray(y_true)
    pred = np.asarray(y_pred)
    if truth.ndim != 1 or pred.ndim != 1 or truth.shape != pred.shape or not len(truth):
        raise ValueError("Expected matching non-empty one-dimensional vectors")
    if not np.isin(truth, [0, 1]).all() or not np.isin(pred, [0, 1]).all():
        raise ValueError("Binary 0/1 labels required")
    tn, fp, fn, tp = map(int, confusion_matrix(truth, pred, labels=[0, 1]).ravel())
    return {
        "tn": tn, "fp": fp, "fn": fn, "tp": tp,
        "f1": float(f1_score(truth, pred, zero_division=0)),
        "precision": float(precision_score(truth, pred, zero_division=0)),
        "recall": float(recall_score(truth, pred, zero_division=0)),
        "fpr": fp / (fp + tn) if fp + tn else None,
    }


def paired_bootstrap_difference(y_true, predictions_a, predictions_b, metric="f1",
                                n_resamples=2000, seed=42, confidence=0.95):
    """Estimate difference (A - B) on same held-out observations.

    Percentile CI; row-level empirical resampling is inappropriate for
    temporally dependent traffic traces without suitable block resampling.
    """
    truth = np.asarray(y_true)
    a = np.asarray(predictions_a)
    b = np.asarray(predictions_b)
    if any(x.ndim != 1 or len(x) != len(truth) for x in (truth, a, b)) or not len(truth):
        raise ValueError("Labels/predictions must have matching non-empty lengths")
    if metric not in {"f1", "recall", "precision"}:
        raise ValueError("Metric must be f1, recall, or precision")
    if not isinstance(n_resamples, int) or n_resamples < 100:
        raise ValueError("At least 100 bootstrap resamples are required")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must lie strictly between 0 and 1")
    baseline = binary_metrics(truth, a)[metric] - binary_metrics(truth, b)[metric]
    rng = np.random.default_rng(seed)
    samples = np.empty(n_resamples, dtype=float)
    for index in range(n_resamples):
        row_ids = rng.integers(0, len(truth), len(truth))
        scores_a = binary_metrics(truth[row_ids], a[row_ids])
        scores_b = binary_metrics(truth[row_ids], b[row_ids])
        samples[index] = scores_a[metric] - scores_b[metric]
    alpha = (1 - confidence) / 2
    return {
        "metric": metric,
        "estimate_a_minus_b": float(baseline),
        "ci_low": float(np.quantile(samples, alpha)),
        "ci_high": float(np.quantile(samples, 1 - alpha)),
        "confidence": confidence,
        "bootstrap_samples": n_resamples,
        "seed": seed,
        "caution": "Test-row uncertainty only; dependence/shift/training variability not captured.",
    }
