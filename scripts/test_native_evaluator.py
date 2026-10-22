import joblib
import pandas as pd
import numpy as np

# Load STS model
sts_pipeline = joblib.load("artifacts/sts_decision_tree_v1.joblib")
test_df = pd.read_csv("data/sts_cleaned.csv")
features = [
    "AGE", "DURATION", "HGT", "WGT", "bmi", "SYS", "DIA", "FBS",
    "FT3", "FT4", "TSH", "Anti tpo", "Visfatin", "Thyroglobulin",
    "IL6", "TCHOL", "TGL", "HDL", "LDL", "HB", "WBC", "PLT", "SEX"
]

def native_predict_sts(row):
    anti_tpo = float(row.get("Anti tpo", row.get("Anti_tpo", 0)))
    tsh = float(row.get("TSH", 0))

    rules = []
    if anti_tpo > 37.5:
        rules.append(f"Decision Node 0: Anti tpo ({anti_tpo:.2f}) > threshold 37.50 -> Branch Right")
        return "Autoimmune Thyroid Disease", {
            "Autoimmune Thyroid Disease": 1.0, "Euthyroid / Normal": 0.0,
            "Hyperthyroid": 0.0, "Primary Hypothyroidism": 0.0
        }, rules
    
    rules.append(f"Decision Node 0: Anti tpo ({anti_tpo:.2f}) <= threshold 37.50 -> Branch Left")
    if tsh <= 0.5815:
        rules.append(f"Decision Node 1: TSH ({tsh:.2f}) <= threshold 0.58 -> Branch Left")
        return "Hyperthyroid", {
            "Autoimmune Thyroid Disease": 0.0, "Euthyroid / Normal": 0.0,
            "Hyperthyroid": 1.0, "Primary Hypothyroidism": 0.0
        }, rules
    
    rules.append(f"Decision Node 1: TSH ({tsh:.2f}) > threshold 0.58 -> Branch Right")
    if tsh > 5.165:
        rules.append(f"Decision Node 3: TSH ({tsh:.2f}) > threshold 5.16 -> Branch Right")
        return "Primary Hypothyroidism", {
            "Autoimmune Thyroid Disease": 0.0, "Euthyroid / Normal": 0.0,
            "Hyperthyroid": 0.0, "Primary Hypothyroidism": 1.0
        }, rules
    
    rules.append(f"Decision Node 3: TSH ({tsh:.2f}) <= threshold 5.16 -> Branch Left")
    if tsh <= 0.9253:
        rules.append(f"Decision Node 4: TSH ({tsh:.2f}) <= threshold 0.93 -> Branch Left")
    else:
        rules.append(f"Decision Node 4: TSH ({tsh:.2f}) > threshold 0.93 -> Branch Right")
    
    return "Euthyroid / Normal", {
        "Autoimmune Thyroid Disease": 0.0, "Euthyroid / Normal": 1.0,
        "Hyperthyroid": 0.0, "Primary Hypothyroidism": 0.0
    }, rules

# Test on ALL 269 records in dataset!
mismatches = 0
for _, row in test_df.iterrows():
    sample_df = pd.DataFrame([row[features]])
    joblib_pred = sts_pipeline.predict(sample_df)[0]
    native_pred, _, _ = native_predict_sts(row)
    if joblib_pred != native_pred:
        mismatches += 1

print(f"Total rows tested: {len(test_df)}")
print(f"Mismatches between scikit-learn and native evaluator: {mismatches}")
assert mismatches == 0, "Discrepancy detected!"
print("STS Clinical Model: 100.00% EXACT REPRODUCTION ON EVERY SAMPLE!")
