"""Pre-training data audit for an offline intrusion-detection benchmark.

Checks exact feature-vector overlap without exposing, altering, or removing test
records. The hash uses deterministic row serialization after column ordering.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

EXCLUDED = frozenset({"id", "label", "attack_cat", "srcip", "dstip", "stime", "ltime", "timestamp"})


def row_hashes(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Stable across split order; normalizes missing values before hashing."""
    if not columns:
        raise ValueError("No predictor columns to audit")
    clean = frame.loc[:, columns].copy()
    # Serialize rows with a length-independent typed schema using pandas hashing.
    # Categorical text and numeric columns must have matching dtypes across splits.
    clean = clean.fillna("__MISSING__").astype("string")
    return pd.util.hash_pandas_object(clean, index=False).reset_index(drop=True)


def audit_splits(training: pd.DataFrame, testing: pd.DataFrame) -> dict:
    for part, frame in (("train", training), ("test", testing)):
        if "label" not in frame.columns:
            raise ValueError(f"{part} requires a label column")
        if frame.columns.duplicated().any():
            raise ValueError(f"{part} contains duplicate column names")
    features = sorted(set(training.columns) - EXCLUDED)
    if not features or set(features) != set(testing.columns) - EXCLUDED:
        raise ValueError("Train/test predictor schemas differ")
    train_hash = row_hashes(training, features)
    test_hash = row_hashes(testing, features)
    train_set = set(train_hash.tolist())
    shared = test_hash.isin(train_set)
    duplicate_train = int(train_hash.duplicated().sum())
    duplicate_test = int(test_hash.duplicated().sum())

    labels = pd.DataFrame({"key": train_hash, "label": training.label.reset_index(drop=True)})
    disagreement = int((labels.groupby("key").label.nunique() > 1).sum())
    test_labels = pd.DataFrame({"key": test_hash, "label": testing.label.reset_index(drop=True)})
    cross = pd.concat([labels, test_labels], ignore_index=True)
    contradictory_cross = int((cross.groupby("key").label.nunique() > 1).sum())

    return {
        "train_rows": int(len(training)),
        "test_rows": int(len(testing)),
        "predictor_columns": len(features),
        "duplicate_train_rows": duplicate_train,
        "duplicate_test_rows": duplicate_test,
        "test_rows_matching_training_predictors": int(shared.sum()),
        "test_overlap_fraction": float(shared.mean()) if len(testing) else None,
        "conflicting_duplicate_feature_groups_train": disagreement,
        "conflicting_feature_groups_pooled": contradictory_cross,
        "warning": (
            "Non-cryptographic row fingerprints are for diagnostic screening, "
            "not proof of identical records. Verify suspicious matches from source data. "
            "Do not remove overlapping records without documenting benchmark modifications."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/data_audit.json"))
    args = parser.parse_args()
    train = pd.read_csv(args.train, low_memory=False)
    test = pd.read_csv(args.test, low_memory=False)
    train.columns = train.columns.str.strip().str.lower()
    test.columns = test.columns.str.strip().str.lower()
    result = audit_splits(train, test)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
