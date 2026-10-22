import os
import json
import hashlib
import pytest
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix
)

from backend.app.core.config import settings

def test_sts_reproducibility_audit():
    """Verify that STS Clinical Decision Tree reproduces held-out test metrics exactly."""
    data_path = os.path.join(settings.DATA_DIR, "sts_cleaned.csv")
    meta_path = os.path.join(settings.ARTIFACTS_DIR, "sts_model_metadata.json")
    model_path = os.path.join(settings.ARTIFACTS_DIR, "sts_decision_tree_v1.joblib")

    assert os.path.exists(data_path)
    assert os.path.exists(meta_path)
    assert os.path.exists(model_path)

    df = pd.read_csv(data_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    pipeline = joblib.load(model_path)
    features = meta["features"]["numeric"] + meta["features"]["categorical"]
    
    from sklearn.model_selection import train_test_split
    X = df[features]
    y = df["target"]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    assert len(X_test) == meta["dataset"]["test_samples"]
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    assert round(acc, 4) == round(meta["metrics"]["accuracy"], 4)
    assert round(bal_acc, 4) == round(meta["metrics"]["balanced_accuracy"], 4)
    assert round(macro_f1, 4) == round(meta["metrics"]["macro_f1"], 4)
    assert round(weighted_f1, 4) == round(meta["metrics"]["weighted_f1"], 4)

def test_uci_reproducibility_audit():
    """Verify that UCI Benchmark Decision Tree reproduces held-out test metrics exactly."""
    train_path = os.path.join(settings.DATA_DIR, "uci_train.csv")
    test_path = os.path.join(settings.DATA_DIR, "uci_test.csv")
    meta_path = os.path.join(settings.ARTIFACTS_DIR, "uci_model_metadata.json")
    model_path = os.path.join(settings.ARTIFACTS_DIR, "uci_decision_tree_v1.joblib")

    assert os.path.exists(train_path)
    assert os.path.exists(test_path)
    assert os.path.exists(meta_path)
    assert os.path.exists(model_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    pipeline = joblib.load(model_path)
    test_df = pd.read_csv(test_path)

    numeric_features = meta["features"]["numeric"]
    boolean_features = meta["features"]["boolean"]
    categorical_features = meta["features"]["categorical"]
    feature_columns = numeric_features + boolean_features + categorical_features
    valid_classes = meta["classes"]

    test_filtered = test_df[test_df["target"].isin(valid_classes)].copy()
    for col in numeric_features:
        test_filtered[col] = pd.to_numeric(test_filtered[col].replace("?", np.nan), errors="coerce")
    for col in boolean_features:
        test_filtered[col] = test_filtered[col].replace("?", "f").map({"t": 1, "f": 0}).fillna(0)
    test_filtered["sex"] = test_filtered["sex"].replace("?", "F")

    X_test = test_filtered[feature_columns]
    y_test = test_filtered["target"]

    assert len(X_test) == meta["dataset"]["test_samples"]
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    assert round(acc, 4) == round(meta["metrics"]["accuracy"], 4)
    assert round(bal_acc, 4) == round(meta["metrics"]["balanced_accuracy"], 4)
    assert round(macro_f1, 4) == round(meta["metrics"]["macro_f1"], 4)
    assert round(weighted_f1, 3) == round(meta["metrics"]["weighted_f1"], 3)
