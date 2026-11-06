"""Offline UNSW-NB15 benchmark. No measured results are bundled."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DROP = frozenset({"id", "label", "attack_cat", "srcip", "dstip", "stime", "ltime", "timestamp"})
OFFICIAL_ROWS = {"train": 175341, "test": 82332}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input CSV: {path}")
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip().str.lower()
    if df.columns.duplicated().any():
        raise ValueError("Duplicated column names after normalization")
    if "label" not in df:
        raise ValueError("Missing binary label")
    labels = pd.to_numeric(df["label"], errors="raise")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("Labels must be binary 0/1 without missing values")
    df["label"] = labels.astype(int)
    return df


def prepare(train: pd.DataFrame, test: pd.DataFrame):
    train_cols = set(train.columns) - DROP
    test_cols = set(test.columns) - DROP
    if train_cols != test_cols or not train_cols:
        raise ValueError("Training/test features disagree or are empty")
    columns = sorted(train_cols)
    x_train, x_test = train[columns].copy(), test[columns].copy()
    numeric, categorical = [], []
    for col in columns:
        is_numeric = pd.api.types.is_numeric_dtype(x_train[col])
        if is_numeric != pd.api.types.is_numeric_dtype(x_test[col]):
            raise ValueError(f"Inconsistent feature dtype: {col}")
        if is_numeric:
            numeric.append(col)
            for frame in (x_train, x_test):
                frame[col] = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        else:
            categorical.append(col)
            for frame in (x_train, x_test):
                frame[col] = frame[col].astype("string").fillna("missing").astype(str)
    steps = []
    if numeric:
        steps.append(("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric))
    if categorical:
        steps.append(("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical))
    return x_train, x_test, ColumnTransformer(steps), columns


def models():
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, min_samples_leaf=2, random_state=42, n_jobs=1),
    }


def measure(name, estimator, transformer, x_train, y_train, x_test, y_test):
    pipeline = Pipeline([("preprocess", clone(transformer)), ("model", clone(estimator))])
    start = time.perf_counter()
    pipeline.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    pipeline.predict(x_test.iloc[:min(len(x_test), 100)])  # warm-up
    elapsed = []
    for _ in range(5):
        start = time.perf_counter()
        predictions = pipeline.predict(x_test)
        elapsed.append(time.perf_counter() - start)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y_test, predictions, labels=[0, 1]).ravel())
    return {
        "model": name, "train_rows": int(len(x_train)), "test_rows": int(len(x_test)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "false_negative_rate": fn / (fn + tp) if fn + tp else None,
        "inference_ms_per_1000": float(np.median(elapsed) * 1_000_000 / len(x_test)),
        "fit_seconds": fit_seconds, "tn": tn, "fp": fp, "fn": fn, "tp": tp,
    }


def run(args):
    train, test = load_dataset(args.train), load_dataset(args.test)
    if not args.exploratory and (len(train) != OFFICIAL_ROWS["train"] or len(test) != OFFICIAL_ROWS["test"]):
        raise ValueError("Unexpected official-split row count; use --exploratory for alternative data")
    if args.exploratory:
        train = train.groupby("label", group_keys=False).sample(frac=min(1, 15000 / len(train)), random_state=42)
        test = test.groupby("label", group_keys=False).sample(frac=min(1, 8000 / len(test)), random_state=42)
    if train["label"].nunique() != 2 or test["label"].nunique() != 2:
        raise ValueError("Both classes must be represented in each split")
    x_train, x_test, transformer, columns = prepare(train, test)
    y_train = train["label"].to_numpy()
    y_test = test["label"].to_numpy()

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    results = [measure(n, m, transformer, x_train, y_train, x_test, y_test) for n, m in models().items()]
    mode = "EXPLORATORY" if args.exploratory else "FULL_BENCHMARK"
    pd.DataFrame(results).to_csv(out / f"metrics_{mode}.csv", index=False)

    if args.cv:
        folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        cv_rows = []
        for name, estimator in models().items():
            pipe = Pipeline([("preprocess", clone(transformer)), ("model", clone(estimator))])
            scores = cross_validate(pipe, x_train, y_train, cv=folds, scoring={"f1": "f1", "recall": "recall"}, n_jobs=1)
            for fold in range(3):
                cv_rows.append({"model": name, "fold": fold + 1,
                                "train_cv_f1": float(scores["test_f1"][fold]),
                                "train_cv_recall": float(scores["test_recall"][fold])})
        pd.DataFrame(cv_rows).to_csv(out / f"train_cv_{mode}.csv", index=False)

    metadata = {
        "status": "executed locally, not independently verified",
        "mode": mode, "seed": 42,
        "training_file": str(args.train), "test_file": str(args.test),
        "train_sha256": sha256(args.train), "test_sha256": sha256(args.test),
        "train_rows": int(len(train)), "test_rows": int(len(test)),
        "features": columns, "cv_on_training_only": bool(args.cv),
        "python_platform": platform.platform(),
        "warning": "Do not treat historical offline benchmarks as contemporary network deployment evidence.",
    }
    (out / f"metadata_{mode}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"metrics": results, "metadata": metadata}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=ROOT / "data/UNSW_NB15_training-set.csv")
    parser.add_argument("--test", type=Path, default=ROOT / "data/UNSW_NB15_testing-set.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--exploratory", action="store_true", help="Sample subset; never use for final result claims")
    parser.add_argument("--cv", action="store_true", help="Stratified three-fold CV on training records ONLY")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
