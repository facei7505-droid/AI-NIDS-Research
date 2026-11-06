"""Run a synthetic feature-corruption study on offline UNSW-NB15.

Scores are produced only from real execution on local supplied CSV files.
This stress test does NOT simulate zero-day or adversarial network attacks.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline

from run_experiments import OFFICIAL_ROWS, load_dataset, models, prepare, sha256
from robustness import corrupt_features

DEFAULT_SEVERITIES = (0.0, 0.1, 0.25, 0.5)
MODES = ("missingness", "numeric_noise", "novel_categories")


def evaluate(y_true, predictions, positive_scores):
    tn, fp, fn, tp = (int(x) for x in confusion_matrix(y_true, predictions, labels=[0, 1]).ravel())
    return {
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "fpr": float(fp / (fp + tn)) if fp + tn else None,
        "average_precision": float(average_precision_score(y_true, positive_scores)),
        "tn": tn, "fp": fp, "fn": fn, "tp": tp,
    }


def experiment(train, test, *, severities=DEFAULT_SEVERITIES, seed=42):
    """Return stress-test results without mutating data or training on test rows."""
    if train.label.nunique() != 2 or test.label.nunique() != 2:
        raise ValueError("Both training and test splits must contain classes 0 and 1")
    if not severities or any(not np.isfinite(x) or x < 0 or x > 1 for x in severities):
        raise ValueError("Severities must be nonempty finite values between zero and one")
    x_train, x_test, prep, features = prepare(train, test)
    y_train, y_test = train.label.to_numpy(), test.label.to_numpy()
    modes = ["clean"] + list(MODES)
    rows = []
    for name, estimator in models().items():
        model = Pipeline([("preprocess", clone(prep)), ("model", clone(estimator))])
        model.fit(x_train, y_train)
        for mode in modes:
            for severity in ((0.0,) if mode == "clean" else severities):
                if mode == "clean":
                    x_eval = x_test
                else:
                    try:
                        x_eval = corrupt_features(x_train, x_test, severity=severity, mode=mode, seed=seed)
                    except ValueError as exc:
                        if "No numeric features" in str(exc) or "No categorical features" in str(exc):
                            continue
                        raise
                pred = model.predict(x_eval)
                if hasattr(model, "predict_proba"):
                    scores = model.predict_proba(x_eval)[:, 1]
                else:
                    scores = model.decision_function(x_eval)
                rows.append({"model": name, "mode": mode, "severity": float(severity),
                             **evaluate(y_test, pred, scores)})
    return rows, features


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/UNSW_NB15_training-set.csv"))
    parser.add_argument("--test", type=Path, default=Path("data/UNSW_NB15_testing-set.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/robustness.json"))
    parser.add_argument("--exploratory", action="store_true", help="Allow nonofficial splits; report as exploratory")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    train, test = load_dataset(args.train), load_dataset(args.test)
    if not args.exploratory and (len(train) != OFFICIAL_ROWS["train"] or len(test) != OFFICIAL_ROWS["test"]):
        parser.error("Unexpected official-split row count. Use --exploratory for alternative data.")
    rows, features = experiment(train, test, seed=args.seed)
    record = {
        "status": "EXPLORATORY (nonofficial split)" if args.exploratory else "OFFICIAL_SPLIT_SYNTHETIC_STRESS_TEST",
        "disclaimer": "Synthetic feature corruption is not evidence of resistance to real attacks or data drift.",
        "seed": args.seed,
        "train_sha256": sha256(args.train), "test_sha256": sha256(args.test),
        "train_rows": len(train), "test_rows": len(test),
        "features": features, "severities": DEFAULT_SEVERITIES,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} model/scenario results to {args.output}")


if __name__ == "__main__":
    main()
