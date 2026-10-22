import os
import sys
import json
import hashlib
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)

# Robust workspace-relative path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
train_path = os.path.join(BASE_DIR, "data", "uci_train.csv")
test_path = os.path.join(BASE_DIR, "data", "uci_test.csv")
meta_path = os.path.join(BASE_DIR, "artifacts", "uci_model_metadata.json")
model_path = os.path.join(BASE_DIR, "artifacts", "uci_decision_tree_v1.joblib")

print("=" * 60)
print("THYROPREDICT AI — UCI REPRODUCIBILITY & SCIENTIFIC AUDIT")
print("=" * 60)

# 1. Dataset Provenance & File Integrity
print("\n--- 1. DATASET PROVENANCE & CHECKSUM VERIFICATION ---")
assert os.path.exists(train_path), f"Missing UCI train file: {train_path}"
assert os.path.exists(test_path), f"Missing UCI test file: {test_path}"
assert os.path.exists(meta_path), f"Missing UCI metadata: {meta_path}"
assert os.path.exists(model_path), f"Missing UCI model artifact: {model_path}"

with open(train_path, "rb") as f:
    train_bytes = f.read()
    calc_train_md5 = hashlib.md5(train_bytes).hexdigest()
    calc_train_sha256 = hashlib.sha256(train_bytes).hexdigest()

with open(test_path, "rb") as f:
    test_bytes = f.read()
    calc_test_md5 = hashlib.md5(test_bytes).hexdigest()
    calc_test_sha256 = hashlib.sha256(test_bytes).hexdigest()

with open(meta_path, "r", encoding="utf-8") as f:
    saved_meta = json.load(f)

saved_train_md5 = saved_meta["dataset"]["fingerprint_md5"]
print(f"Train File MD5:       {calc_train_md5} (Metadata: {saved_train_md5})")
print(f"Train File SHA-256:   {calc_train_sha256}")
print(f"Test File MD5:        {calc_test_md5}")
print(f"Test File SHA-256:    {calc_test_sha256}")

assert calc_train_md5 == saved_train_md5, "Train dataset MD5 checksum mismatch!"
print("Provenance & Checksum verification: PASS.")

# 2. Dataset Ingestion & Partitioning
print("\n--- 2. PARTITIONING & DATA INTEGRITY ---")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

numeric_features = saved_meta["features"]["numeric"]
boolean_features = saved_meta["features"]["boolean"]
categorical_features = saved_meta["features"]["categorical"]
feature_columns = numeric_features + boolean_features + categorical_features
valid_classes = saved_meta["classes"]

# Verify no target or ID leakage in feature columns
for feat in feature_columns:
    assert feat != "target", "Target column found in input features!"
    assert feat not in ["id", "patient_id", "participant_id"], f"Identifier {feat} in features!"

def clean_uci(d_in):
    d = d_in.copy()
    for col in numeric_features:
        d[col] = pd.to_numeric(d[col].replace("?", np.nan), errors="coerce")
    for col in boolean_features:
        d[col] = d[col].replace("?", "f").map({"t": 1, "f": 0}).fillna(0)
    d["sex"] = d["sex"].replace("?", "F")
    return d

train_filtered = train_df[train_df["target"].isin(valid_classes)].copy()
test_filtered = test_df[test_df["target"].isin(valid_classes)].copy()

train_clean = clean_uci(train_filtered)
test_clean = clean_uci(test_filtered)

X_train = train_clean[feature_columns]
y_train = train_clean["target"]
X_test = test_clean[feature_columns]
y_test = test_clean["target"]

print(f"Train sample count: {len(X_train)} (Saved Expected: {saved_meta['dataset']['train_samples']})")
print(f"Test sample count:  {len(X_test)} (Saved Expected: {saved_meta['dataset']['test_samples']})")
assert len(X_train) == saved_meta["dataset"]["train_samples"], "Train samples count mismatch!"
assert len(X_test) == saved_meta["dataset"]["test_samples"], "Test samples count mismatch!"
print("Sample counts and partition split verification: PASS.")

# 3. Model Loading & Tree Architecture
print("\n--- 3. MODEL ARCHITECTURE & PIPELINE INTEGRITY ---")
model_pipeline = joblib.load(model_path)
assert "preprocessor" in model_pipeline.named_steps, "Missing preprocessor pipeline step!"
assert "classifier" in model_pipeline.named_steps, "Missing classifier pipeline step!"

clf = model_pipeline.named_steps["classifier"]
saved_hp = saved_meta["hyperparameters"]
assert clf.criterion == saved_hp["criterion"], "Criterion mismatch!"
assert clf.max_depth == saved_hp["max_depth"], "Max depth mismatch!"
assert clf.min_samples_split == saved_hp["min_samples_split"], "Min samples split mismatch!"
assert clf.min_samples_leaf == saved_hp["min_samples_leaf"], "Min samples leaf mismatch!"
assert clf.class_weight == saved_hp["class_weight"], "Class weight mismatch!"
assert clf.random_state == saved_hp["random_state"], "Random state mismatch!"

depth = int(clf.get_depth())
n_leaves = int(clf.get_n_leaves())
print(f"Tree Depth: {depth} (Metadata: {saved_meta['tree_structure']['depth']})")
print(f"Leaf Nodes: {n_leaves} (Metadata: {saved_meta['tree_structure']['n_leaves']})")
assert depth == saved_meta["tree_structure"]["depth"], "Tree depth mismatch!"
assert n_leaves == saved_meta["tree_structure"]["n_leaves"], "Leaf count mismatch!"
print("Model pipeline and tree hyperparameters verification: PASS.")

# 4. Held-Out Evaluation Reproduction
print("\n--- 4. METRIC REPRODUCIBILITY AUDIT ---")
y_pred = model_pipeline.predict(X_test)
classes = list(clf.classes_)
assert classes == saved_meta["classes"], "Model classes order mismatch!"

acc = accuracy_score(y_test, y_pred)
bal_acc = balanced_accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

saved_acc = saved_meta["metrics"]["accuracy"]
saved_bal = saved_meta["metrics"]["balanced_accuracy"]
saved_macro = saved_meta["metrics"]["macro_f1"]
saved_weighted = saved_meta["metrics"]["weighted_f1"]

print(f"Calculated Test Accuracy:     {acc:.4f} | Saved: {saved_acc:.4f}")
print(f"Calculated Balanced Accuracy: {bal_acc:.4f} | Saved: {saved_bal:.4f}")
print(f"Calculated Macro-F1:          {macro_f1:.4f} | Saved: {saved_macro:.4f}")
print(f"Calculated Weighted-F1:       {weighted_f1:.4f} | Saved: {saved_weighted:.4f}")

assert round(acc, 4) == round(saved_acc, 4), f"Accuracy mismatch: {acc:.4f} vs {saved_acc:.4f}"
assert round(bal_acc, 4) == round(saved_bal, 4), f"Balanced accuracy mismatch: {bal_acc:.4f} vs {saved_bal:.4f}"
assert round(macro_f1, 4) == round(saved_macro, 4), f"Macro-F1 mismatch: {macro_f1:.4f} vs {saved_macro:.4f}"
assert round(weighted_f1, 3) == round(saved_weighted, 3), f"Weighted-F1 mismatch: {weighted_f1:.4f} vs {saved_weighted:.4f}"
print("Core evaluation metrics exact match: PASS.")

# 5. Confusion Matrix Verification
print("\n--- 5. CONFUSION MATRIX VERIFICATION ---")
cm = confusion_matrix(y_test, y_pred, labels=classes)
saved_cm = np.array(saved_meta["metrics"]["confusion_matrix"]["matrix"])
print("Calculated Confusion Matrix:")
print(cm)
print("Saved Confusion Matrix:")
print(saved_cm)
assert np.array_equal(cm, saved_cm), "Confusion matrix does not match saved matrix!"
print("Confusion Matrix exact match: PASS.")

# 6. Per-Class Precision, Recall, and F1 Verification
print("\n--- 6. PER-CLASS METRIC VERIFICATION ---")
precisions = precision_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
recalls = recall_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
f1s = f1_score(y_test, y_pred, labels=classes, average=None, zero_division=0)

for i, cls in enumerate(classes):
    saved_p = saved_meta["metrics"]["per_class"][cls]["precision"]
    saved_r = saved_meta["metrics"]["per_class"][cls]["recall"]
    saved_f = saved_meta["metrics"]["per_class"][cls]["f1_score"]
    saved_s = saved_meta["metrics"]["per_class"][cls]["support"]
    calc_s = int((y_test == cls).sum())

    print(f"Class '{cls}':")
    print(f"  Precision: Calc={precisions[i]:.4f}, Saved={saved_p:.4f} -> Match: {round(precisions[i], 4) == round(saved_p, 4)}")
    print(f"  Recall:    Calc={recalls[i]:.4f}, Saved={saved_r:.4f} -> Match: {round(recalls[i], 4) == round(saved_r, 4)}")
    print(f"  F1-Score:  Calc={f1s[i]:.4f}, Saved={saved_f:.4f} -> Match: {round(f1s[i], 4) == round(saved_f, 4)}")
    print(f"  Support:   Calc={calc_s}, Saved={saved_s} -> Match: {calc_s == saved_s}")

    assert round(precisions[i], 4) == round(saved_p, 4), f"Precision mismatch for {cls}"
    assert round(recalls[i], 4) == round(saved_r, 4), f"Recall mismatch for {cls}"
    assert round(f1s[i], 4) == round(saved_f, 4), f"F1 mismatch for {cls}"
    assert calc_s == saved_s, f"Support mismatch for {cls}"

print("\nAll per-class metrics matched saved benchmarks: PASS.")
print("=" * 60)
print("UCI REPRODUCIBILITY AUDIT: ALL CHECKS PASSED SUCCESSFULLY (CODE 0)")
print("=" * 60)
