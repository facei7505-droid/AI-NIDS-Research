"""Controlled, label-preserving feature corruption for OFFLINE stress tests.

These perturbations are synthetic; they are not network attacks and cannot
demonstrate real-world resistance to adversaries or new threat families.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def corrupt_features(x_train: pd.DataFrame, x_test: pd.DataFrame, *,
                     severity: float, mode: str, seed: int = 42) -> pd.DataFrame:
    """Return a NEW test dataframe. Train data are used only for scale estimates.

    Supported modes:
    - numeric_noise: add Gaussian noise proportional to training std on
      randomly selected numeric cells; no attempt to preserve physical units.
    - missingness: replace a fraction of all feature cells by NaN.
    - novel_categories: replace selected categorical cells by an unseen token.

    Results are meaningful as measurement-corruption sensitivity analyses only.
    """
    if list(x_train.columns) != list(x_test.columns):
        raise ValueError("Train and test feature columns/order must match")
    if not 0 <= severity <= 1 or not np.isfinite(severity):
        raise ValueError("Severity must be between 0 and 1")
    if mode not in {"numeric_noise", "missingness", "novel_categories"}:
        raise ValueError("Unknown corruption mode")
    rng = np.random.default_rng(seed)
    shifted = x_test.copy(deep=True)
    if severity == 0:
        return shifted

    numeric = list(x_train.select_dtypes(include="number").columns)
    categories = [c for c in x_train if c not in numeric]
    if mode == "numeric_noise":
        if not numeric:
            raise ValueError("No numeric features")
        for column in numeric:
            std = float(pd.to_numeric(x_train[column], errors="coerce").std())
            if not np.isfinite(std) or std == 0:
                continue
            mask = rng.random(len(shifted)) < severity
            noise = rng.normal(0, std * severity, len(shifted))
            shifted.loc[mask, column] = shifted.loc[mask, column].astype(float) + noise[mask]
    elif mode == "missingness":
        for column in shifted:
            mask = rng.random(len(shifted)) < severity
            shifted.loc[mask, column] = np.nan
    else:
        if not categories:
            raise ValueError("No categorical features")
        # Sentinel differs from all known training/test categorical values.
        sentinel = "__UNSEEN_SENSITIVITY_TEST__"
        for column in categories:
            existing = set(x_train[column].dropna().astype(str)) | set(x_test[column].dropna().astype(str))
            if sentinel in existing:
                raise ValueError("Novel category sentinel already occurs in data")
            mask = rng.random(len(shifted)) < severity
            shifted.loc[mask, column] = sentinel
    return shifted
