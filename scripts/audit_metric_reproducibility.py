import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)

import os

# Robust workspace-relative path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "sts_cleaned.csv")
meta_path = os.path.join(BASE_DIR, "artifacts", "sts_model_metadata.json")
model_path = os.path.join(BASE_DIR, "artifacts", "sts_decision_tree_v1.joblib")

# 1. Load Data and Metadata
df = pd.read_csv(data_path)
with open(meta_path, "r", encoding="utf-8") as f:
    saved_meta = json.load(f)

model_pipeline = joblib.load(model_path)

features = saved_meta["features"]["numeric"] + saved_meta["features"]["categorical"]
target_col = "target"

# Check target-derived or post-diagnosis columns in features
print("--- 1. FEATURE INTEGRITY AUDIT ---")
print("Input features count:", len(features))
for feat in features:
    assert feat != "target", "Target is in features!"
    assert feat != "Unnamed: 20", "Raw diagnostic label column in features!"
    assert "diagnos" not in feat.lower(), f"Suspicious feature name: {feat}"
print("Feature check: No target or diagnostic label columns in input features. PASS.")

# 2. Check for duplicate rows
print("\n--- 2. DATASET DUPLICATES & INTEGRITY ---")
duplicates = df.duplicated(subset=features)
print(f"Total rows in dataset: {len(df)}")
print(f"Duplicate feature rows in dataset: {duplicates.sum()}")

# 3. Reproduce Split and Evaluation
X = df[features]
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train sample count: {len(X_train)} (Expected: {saved_meta['dataset']['train_samples']})")
print(f"Test sample count:  {len(X_test)} (Expected: {saved_meta['dataset']['test_samples']})")
assert len(X_train) == saved_meta['dataset']['train_samples'], "Train count mismatch!"
assert len(X_test) == saved_meta['dataset']['test_samples'], "Test count mismatch!"

# Check train/test overlap
train_indices = set(X_train.index)
test_indices = set(X_test.index)
overlap = train_indices.intersection(test_indices)
print(f"Train/Test index overlap: {len(overlap)} (Must be 0)")
assert len(overlap) == 0, "Data leakage! Overlapping train and test indices!"

# 4. Independent Predictions
y_pred = model_pipeline.predict(X_test)
classes = list(model_pipeline.named_steps["classifier"].classes_)

acc = accuracy_score(y_test, y_pred)
bal_acc = balanced_accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
cm = confusion_matrix(y_test, y_pred, labels=classes)

print("\n--- 3. METRIC REPRODUCIBILITY AUDIT ---")
print(f"Calculated Test Accuracy:     {acc:.4f} | Saved in Metadata: {saved_meta['metrics']['accuracy']:.4f}")
print(f"Calculated Balanced Accuracy: {bal_acc:.4f} | Saved in Metadata: {saved_meta['metrics']['balanced_accuracy']:.4f}")
print(f"Calculated Macro-F1:          {macro_f1:.4f} | Saved in Metadata: {saved_meta['metrics']['macro_f1']:.4f}")
print(f"Calculated Weighted-F1:       {weighted_f1:.4f} | Saved in Metadata: {saved_meta['metrics']['weighted_f1']:.4f}")

# Assert exact match
assert round(acc, 4) == round(saved_meta['metrics']['accuracy'], 4), "Accuracy mismatch!"
assert round(bal_acc, 4) == round(saved_meta['metrics']['balanced_accuracy'], 4), "Balanced accuracy mismatch!"
assert round(macro_f1, 4) == round(saved_meta['metrics']['macro_f1'], 4), "Macro-F1 mismatch!"
assert round(weighted_f1, 4) == round(saved_meta['metrics']['weighted_f1'], 4), "Weighted-F1 mismatch!"
print("Metrics exact match: PASS.")

print("\n--- 4. CONFUSION MATRIX VERIFICATION ---")
saved_cm = np.array(saved_meta['metrics']['confusion_matrix']['matrix'])
print("Calculated Confusion Matrix:")
print(cm)
print("Saved Confusion Matrix:")
print(saved_cm)
assert np.array_equal(cm, saved_cm), "Confusion matrix mismatch!"
print("Confusion Matrix exact match: PASS.")

print("\n--- 5. PER-CLASS METRIC VERIFICATION ---")
precisions = precision_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
recalls = recall_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
f1s = f1_score(y_test, y_pred, labels=classes, average=None, zero_division=0)

for i, cls in enumerate(classes):
    saved_p = saved_meta['metrics']['per_class'][cls]['precision']
    saved_r = saved_meta['metrics']['per_class'][cls]['recall']
    saved_f = saved_meta['metrics']['per_class'][cls]['f1_score']
    saved_s = saved_meta['metrics']['per_class'][cls]['support']
    calc_s = int((y_test == cls).sum())
    
    print(f"Class '{cls}':")
    print(f"  Precision: Calc={precisions[i]:.4f}, Saved={saved_p:.4f} -> Match: {round(precisions[i], 4) == round(saved_p, 4)}")
    print(f"  Recall:    Calc={recalls[i]:.4f}, Saved={saved_r:.4f} -> Match: {round(recalls[i], 4) == round(saved_r, 4)}")
    print(f"  F1-Score:  Calc={f1s[i]:.4f}, Saved={saved_f:.4f} -> Match: {round(f1s[i], 4) == round(saved_f, 4)}")
    print(f"  Support:   Calc={calc_s}, Saved={saved_s} -> Match: {calc_s == saved_s}")
    
    assert round(precisions[i], 4) == round(saved_p, 4)
    assert round(recalls[i], 4) == round(saved_r, 4)
    assert round(f1s[i], 4) == round(saved_f, 4)
    assert calc_s == saved_s

print("\nAll per-class metrics matched down to 4 decimal places: PASS.")
