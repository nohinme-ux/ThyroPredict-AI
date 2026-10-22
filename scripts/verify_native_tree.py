import joblib
import pandas as pd
import numpy as np

# Load the scikit-learn model
model = joblib.load("artifacts/sts_decision_tree_v1.joblib")
clf = model.named_steps["classifier"]
prep = model.named_steps["preprocessor"]

# Print the tree parameters
tree = clf.tree_
print("Tree feature indices:", tree.feature)
print("Tree thresholds:", tree.threshold)
print("Tree values:", tree.value)
print("Classes:", clf.classes_)
