import pandas as pd
import numpy as np
import joblib
import json
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)

print("=" * 60)
print("PHASE 2 & 3: SCIENTIFIC MODEL VALIDATION & OVERFITTING AUDIT")
print("=" * 60)

# --- 1. STS Clinical Model Audit ---
sts_pipeline = joblib.load("artifacts/sts_decision_tree_v1.joblib")
with open("artifacts/sts_model_metadata.json", "r") as f:
    sts_meta = json.load(f)

df_sts = pd.read_csv("data/sts_cleaned.csv")
X_sts = df_sts[sts_meta["features"]["numeric"] + sts_meta["features"]["categorical"]]
y_sts = df_sts["target"]

from sklearn.model_selection import train_test_split
X_train_sts, X_test_sts, y_train_sts, y_test_sts = train_test_split(
    X_sts, y_sts, test_size=0.20, random_state=42, stratify=y_sts
)

y_train_pred = sts_pipeline.predict(X_train_sts)
train_acc = accuracy_score(y_train_sts, y_train_pred)
train_f1 = f1_score(y_train_sts, y_train_pred, average="macro")

y_test_pred = sts_pipeline.predict(X_test_sts)
test_acc = accuracy_score(y_test_sts, y_test_pred)
test_bal_acc = balanced_accuracy_score(y_test_sts, y_test_pred)
test_f1 = f1_score(y_test_sts, y_test_pred, average="macro")

print("\n[STS CLINICAL MODEL AUDIT]")
print(f"Training Accuracy: {train_acc:.4f} | Training Macro F1: {train_f1:.4f}")
print(f"Test Accuracy:     {test_acc:.4f} | Test Macro F1:     {test_f1:.4f}")
print(f"Balanced Accuracy: {test_bal_acc:.4f}")
print(f"Overfitting Gap (Train - Test): {(train_acc - test_acc):.4f}")

cm_sts = confusion_matrix(y_test_sts, y_test_pred, labels=sts_pipeline.classes_)
print("\nSTS Confusion Matrix (Test Split N=54):")
print("Classes:", sts_pipeline.classes_)
print(cm_sts)

for i, cls in enumerate(sts_pipeline.classes_):
    tp = cm_sts[i, i]
    fn = cm_sts[i, :].sum() - tp
    fp = cm_sts[:, i].sum() - tp
    tn = cm_sts.sum() - (tp + fp + fn)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    print(f"  Class '{cls}': Sensitivity={sens:.4f}, Specificity={spec:.4f}, TN={tn}, FP={fp}, FN={fn}, TP={tp}")

# --- 2. UCI Benchmark Model Audit ---
uci_pipeline = joblib.load("artifacts/uci_decision_tree_v1.joblib")
with open("artifacts/uci_model_metadata.json", "r") as f:
    uci_meta = json.load(f)

train_uci = pd.read_csv("data/uci_train.csv")
test_uci = pd.read_csv("data/uci_test.csv")

numeric_features = ["age", "TSH", "T3", "TT4", "T4U", "FTI"]
boolean_features = [
    "on_thyroxine", "query_on_thyroxine", "on_antithyroid_medication",
    "sick", "pregnant", "thyroid_surgery", "I131_treatment",
    "query_hypothyroid", "query_hyperthyroid", "lithium", "goitre",
    "tumor", "hypopituitary", "psych"
]
categorical_features = ["sex"]
feature_columns = numeric_features + boolean_features + categorical_features

def clean_uci_df(df_in):
    d = df_in.copy()
    for col in numeric_features:
        d[col] = pd.to_numeric(d[col].replace("?", np.nan), errors="coerce")
    for col in boolean_features:
        d[col] = d[col].replace("?", "f").map({"t": 1, "f": 0}).fillna(0)
    d["sex"] = d["sex"].replace("?", "F")
    return d

train_clean = clean_uci_df(train_uci[train_uci["target"].isin(["negative", "compensated hypothyroid", "primary hypothyroid"])])
test_clean = clean_uci_df(test_uci[test_uci["target"].isin(["negative", "compensated hypothyroid", "primary hypothyroid"])])

X_train_uci = train_clean[feature_columns]
y_train_uci = train_clean["target"]
X_test_uci = test_clean[feature_columns]
y_test_uci = test_clean["target"]

y_train_pred_uci = uci_pipeline.predict(X_train_uci)
train_acc_uci = accuracy_score(y_train_uci, y_train_pred_uci)
train_f1_uci = f1_score(y_train_uci, y_train_pred_uci, average="macro")

y_test_pred_uci = uci_pipeline.predict(X_test_uci)
test_acc_uci = accuracy_score(y_test_uci, y_test_pred_uci)
test_bal_acc_uci = balanced_accuracy_score(y_test_uci, y_test_pred_uci)
test_f1_uci = f1_score(y_test_uci, y_test_pred_uci, average="macro")

print("\n[UCI BENCHMARK MODEL AUDIT]")
print(f"Training Accuracy: {train_acc_uci:.4f} | Training Macro F1: {train_f1_uci:.4f}")
print(f"Test Accuracy:     {test_acc_uci:.4f} | Test Macro F1:     {test_f1_uci:.4f}")
print(f"Balanced Accuracy: {test_bal_acc_uci:.4f}")
print(f"Overfitting Gap (Train - Test): {(train_acc_uci - test_acc_uci):.4f}")

cm_uci = confusion_matrix(y_test_uci, y_test_pred_uci, labels=uci_pipeline.classes_)
print("\nUCI Confusion Matrix (Test Split N=972):")
print("Classes:", uci_pipeline.classes_)
print(cm_uci)

for i, cls in enumerate(uci_pipeline.classes_):
    tp = cm_uci[i, i]
    fn = cm_uci[i, :].sum() - tp
    fp = cm_uci[:, i].sum() - tp
    tn = cm_uci.sum() - (tp + fp + fn)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    print(f"  Class '{cls}': Sensitivity={sens:.4f}, Specificity={spec:.4f}, TN={tn}, FP={fp}, FN={fn}, TP={tp}")

print("\nAudit Completed Successfully.")
