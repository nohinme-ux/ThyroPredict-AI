import pandas as pd
import numpy as np
import os
import json
import joblib
from datetime import datetime, timezone
import hashlib

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

train_path = "data/uci_train.csv"
test_path = "data/uci_test.csv"
artifacts_dir = "artifacts"
os.makedirs(artifacts_dir, exist_ok=True)

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# Drop extremely rare secondary hypothyroid (only 2 samples in train, 0 in test)
train_df = train_df[train_df["target"].isin(["negative", "compensated hypothyroid", "primary hypothyroid"])].copy()
test_df = test_df[test_df["target"].isin(["negative", "compensated hypothyroid", "primary hypothyroid"])].copy()

# Calculate fingerprint
with open(train_path, "rb") as f:
    train_md5 = hashlib.md5(f.read()).hexdigest()

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

train_clean = clean_uci_df(train_df)
test_clean = clean_uci_df(test_df)

X_train = train_clean[feature_columns]
y_train = train_clean["target"]

X_test = test_clean[feature_columns]
y_test = test_clean["target"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", SimpleImputer(strategy="median"), numeric_features),
        ("bool", SimpleImputer(strategy="most_frequent"), boolean_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False), categorical_features)
    ]
)

clf = DecisionTreeClassifier(
    criterion="gini",
    max_depth=6,
    min_samples_split=8,
    min_samples_leaf=4,
    class_weight="balanced",
    random_state=42
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", clf)
])

# Fit strictly on official training partition
pipeline.fit(X_train, y_train)

# Evaluate strictly on official held-out test partition
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

transformed_names = numeric_features + boolean_features + list(pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features))
importances = pipeline.named_steps["classifier"].feature_importances_
feature_importance_list = [
    {"feature": feat, "importance": round(float(imp), 4)}
    for feat, imp in sorted(zip(transformed_names, importances), key=lambda x: x[1], reverse=True)
    if imp > 0.0001
]

tree_rules = export_text(pipeline.named_steps["classifier"], feature_names=transformed_names)

model_filename = "uci_decision_tree_v1.joblib"
model_path = os.path.join(artifacts_dir, model_filename)
joblib.dump(pipeline, model_path)
print(f"Saved UCI model pipeline artifact to {model_path}")

metadata = {
    "model_id": "uci_benchmark_decision_tree",
    "version": "1.0.0",
    "algorithm": "DecisionTreeClassifier (scikit-learn)",
    "training_timestamp": datetime.now(timezone.utc).isoformat(),
    "dataset": {
        "name": "UCI Thyroid Disease Benchmark Dataset (allhypo)",
        "source": "UCI Machine Learning Repository / Garavan Institute",
        "fingerprint_md5": train_md5,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "split_strategy": "Official UCI independent test partition (allhypo.test)"
    },
    "hyperparameters": {
        "criterion": "gini",
        "max_depth": 6,
        "min_samples_split": 8,
        "min_samples_leaf": 4,
        "class_weight": "balanced",
        "random_state": 42
    },
    "features": {
        "numeric": numeric_features,
        "boolean": boolean_features,
        "categorical": categorical_features,
        "all_transformed": transformed_names
    },
    "classes": classes,
    "metrics": {
        "accuracy": round(float(test_acc), 4),
        "balanced_accuracy": round(float(test_bal_acc), 4),
        "macro_f1": round(float(test_f1_macro), 4),
        "weighted_f1": round(float(test_f1_weighted), 4),
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
        "Historical Garavan Institute dataset collected in 1987.",
        "Model predictions serve solely as an experimental research tool.",
        "High test accuracy on negative class reflects pronounced class imbalance typical of general screening cohorts."
    ]
}

metadata_path = os.path.join(artifacts_dir, "uci_model_metadata.json")
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)
print(f"Saved UCI metadata to {metadata_path}")

print(f"\nUCI Model Performance Summary on Held-out Test Set (N={len(X_test)}):")
print(f"Accuracy: {test_acc:.4f}")
print(f"Balanced Accuracy: {test_bal_acc:.4f}")
print(f"Macro F1: {test_f1_macro:.4f}")
print("\nConfusion Matrix:")
print(cm)
