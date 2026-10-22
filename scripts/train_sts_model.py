import pandas as pd
import numpy as np
import os
import json
import joblib
from datetime import datetime, timezone
import hashlib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix, classification_report
)
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

data_path = "data/sts_cleaned.csv"
artifacts_dir = "artifacts"
os.makedirs(artifacts_dir, exist_ok=True)

df = pd.read_csv(data_path)

# Calculate dataset fingerprint (MD5)
with open(data_path, "rb") as f:
    dataset_md5 = hashlib.md5(f.read()).hexdigest()

# Select high-yield clinical features
numeric_features = [
    "AGE", "DURATION", "HGT", "WGT", "bmi", "SYS", "DIA", "FBS",
    "FT3", "FT4", "TSH", "Anti tpo", "Visfatin", "Thyroglobulin",
    "IL6", "TCHOL", "TGL", "HDL", "LDL", "HB", "WBC", "PLT"
]
categorical_features = ["SEX"]

feature_columns = numeric_features + categorical_features
X = df[feature_columns].copy()
y = df["target"].copy()

# Stratified split: 80% train, 20% held-out test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
print("Test class distribution:\n", y_test.value_counts())

# Build unified preprocessing and model pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("num", SimpleImputer(strategy="median"), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False), categorical_features)
    ]
)

clf = DecisionTreeClassifier(
    criterion="gini",
    max_depth=5,
    min_samples_split=6,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", clf)
])

# Cross-validation on training set (5-fold stratified)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
print(f"5-Fold CV Macro-F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Fit on training data only
pipeline.fit(X_train, y_train)

# Evaluate strictly on held-out test set
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)

classes = list(pipeline.named_steps["classifier"].classes_)
cm = confusion_matrix(y_test, y_pred, labels=classes)

test_acc = accuracy_score(y_test, y_pred)
test_bal_acc = balanced_accuracy_score(y_test, y_pred)
test_f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
test_f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

per_class_precision = precision_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
per_class_recall = recall_score(y_test, y_pred, labels=classes, average=None, zero_division=0)
per_class_f1 = f1_score(y_test, y_pred, labels=classes, average=None, zero_division=0)

per_class_metrics = {}
for i, cls_name in enumerate(classes):
    per_class_metrics[cls_name] = {
        "precision": round(float(per_class_precision[i]), 4),
        "recall": round(float(per_class_recall[i]), 4),
        "f1_score": round(float(per_class_f1[i]), 4),
        "support": int((y_test == cls_name).sum())
    }

# Feature importances
transformed_num_names = numeric_features
transformed_cat_names = list(pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features))
all_feature_names = transformed_num_names + transformed_cat_names

importances = pipeline.named_steps["classifier"].feature_importances_
feature_importance_list = [
    {"feature": feat, "importance": round(float(imp), 4)}
    for feat, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)
    if imp > 0.0001
]

# Export tree rules text for explainability
tree_rules = export_text(pipeline.named_steps["classifier"], feature_names=all_feature_names)

# Save pipeline artifact
model_filename = "sts_decision_tree_v1.joblib"
model_path = os.path.join(artifacts_dir, model_filename)
joblib.dump(pipeline, model_path)
print(f"Saved model pipeline artifact to {model_path}")

metadata = {
    "model_id": "sts_clinical_decision_tree",
    "version": "1.0.0",
    "algorithm": "DecisionTreeClassifier (scikit-learn)",
    "training_timestamp": datetime.now(timezone.utc).isoformat(),
    "dataset": {
        "name": "STS Clinical Thyroid Study Dataset",
        "file": "sts thyroid data.xlsx",
        "fingerprint_md5": dataset_md5,
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "split_strategy": "Stratified 80/20 train/test split (random_state=42)"
    },
    "hyperparameters": {
        "criterion": "gini",
        "max_depth": 5,
        "min_samples_split": 6,
        "min_samples_leaf": 3,
        "class_weight": "balanced",
        "random_state": 42
    },
    "features": {
        "numeric": numeric_features,
        "categorical": categorical_features,
        "all_transformed": all_feature_names
    },
    "classes": classes,
    "metrics": {
        "accuracy": round(float(test_acc), 4),
        "balanced_accuracy": round(float(test_bal_acc), 4),
        "macro_f1": round(float(test_f1_macro), 4),
        "weighted_f1": round(float(test_f1_weighted), 4),
        "cross_val_macro_f1_mean": round(float(cv_scores.mean()), 4),
        "cross_val_macro_f1_std": round(float(cv_scores.std()), 4),
        "confusion_matrix": {
            "labels": classes,
            "matrix": cm.tolist()
        },
        "per_class": per_class_metrics
    },
    "feature_importances": feature_importance_list,
    "tree_structure": {
        "depth": int(pipeline.named_steps["classifier"].get_depth()),
        "n_leaves": int(pipeline.named_steps["classifier"].get_n_leaves()),
        "rules_text": tree_rules
    },
    "limitations": [
        "Trained on an observational clinical cohort of 269 subjects.",
        "Model outputs are research classifications and not confirmed clinical diagnoses.",
        "Anti-TPO is the primary discriminator for autoimmune etiology; laboratory variations in assay calibration may affect predictive thresholds.",
        "Rare clinical presentations or complex dual pathologies require full physician evaluation."
    ]
}

metadata_path = os.path.join(artifacts_dir, "sts_model_metadata.json")
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)
print(f"Saved metadata to {metadata_path}")

print(f"\nModel Performance Summary:")
print(f"Accuracy: {test_acc:.4f}")
print(f"Balanced Accuracy: {test_bal_acc:.4f}")
print(f"Macro F1: {test_f1_macro:.4f}")
print("\nConfusion Matrix:")
print(cm)
