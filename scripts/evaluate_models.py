import joblib
import json
import os
import pandas as pd
import numpy as np

def verify_sts():
    model_path = "artifacts/sts_decision_tree_v1.joblib"
    meta_path = "artifacts/sts_model_metadata.json"
    
    assert os.path.exists(model_path), f"Missing {model_path}"
    assert os.path.exists(meta_path), f"Missing {meta_path}"
    
    pipeline = joblib.load(model_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    print(f"Loaded STS Model v{meta['version']}. Accuracy: {meta['metrics']['accuracy']}")
    
    # Test inference on a hypothyroid sample
    sample = pd.DataFrame([{
        "AGE": 45.0, "SEX": "F", "DURATION": 3.0, "HGT": 155.0, "WGT": 68.0,
        "bmi": 28.3, "SYS": 130.0, "DIA": 85.0, "FBS": 95.0, "FT3": 2.1,
        "FT4": 0.65, "TSH": 25.4, "Anti tpo": 5.2, "Visfatin": 22.0,
        "Thyroglobulin": 18.0, "IL6": 4.5, "TCHOL": 220.0, "TGL": 160.0,
        "HDL": 42.0, "LDL": 140.0, "HB": 12.5, "WBC": 6500.0, "PLT": 250.0
    }])
    
    pred = pipeline.predict(sample)[0]
    probs = pipeline.predict_proba(sample)[0]
    classes = pipeline.named_steps["classifier"].classes_
    prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
    
    print(f"STS Sample Prediction: '{pred}', Probabilities: {prob_dict}")
    assert pred == "Primary Hypothyroidism", f"Expected Primary Hypothyroidism, got {pred}"
    print("STS Verification Passed!\n")

def verify_uci():
    model_path = "artifacts/uci_decision_tree_v1.joblib"
    meta_path = "artifacts/uci_model_metadata.json"
    
    assert os.path.exists(model_path), f"Missing {model_path}"
    assert os.path.exists(meta_path), f"Missing {meta_path}"
    
    pipeline = joblib.load(model_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    print(f"Loaded UCI Model v{meta['version']}. Accuracy: {meta['metrics']['accuracy']}")
    
    sample = pd.DataFrame([{
        "age": 55, "sex": "F", "on_thyroxine": 0, "query_on_thyroxine": 0,
        "on_antithyroid_medication": 0, "sick": 0, "pregnant": 0, "thyroid_surgery": 0,
        "I131_treatment": 0, "query_hypothyroid": 0, "query_hyperthyroid": 0,
        "lithium": 0, "goitre": 0, "tumor": 0, "hypopituitary": 0, "psych": 0,
        "TSH": 45.0, "T3": 1.2, "TT4": 40.0, "T4U": 1.1, "FTI": 36.0
    }])
    
    pred = pipeline.predict(sample)[0]
    probs = pipeline.predict_proba(sample)[0]
    classes = pipeline.named_steps["classifier"].classes_
    prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
    
    print(f"UCI Sample Prediction: '{pred}', Probabilities: {prob_dict}")
    assert "hypothyroid" in pred, f"Expected hypothyroid class, got {pred}"
    print("UCI Verification Passed!")

if __name__ == "__main__":
    verify_sts()
    verify_uci()
