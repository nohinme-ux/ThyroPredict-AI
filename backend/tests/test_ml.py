import os
import json
import joblib
import pandas as pd
import numpy as np
import pytest

from backend.app.services.ml_service import ml_service
from backend.app.core.config import settings

def test_sts_model_loaded():
    assert ml_service.sts_model is not None, "STS model failed to load"
    assert ml_service.sts_meta is not None, "STS metadata failed to load"
    assert ml_service.sts_meta["version"] == "1.0.0"
    assert "accuracy" in ml_service.sts_meta["metrics"]

def test_uci_model_loaded():
    assert ml_service.uci_model is not None, "UCI model failed to load"
    assert ml_service.uci_meta is not None, "UCI metadata failed to load"
    assert ml_service.uci_meta["version"] == "1.0.0"
    assert "accuracy" in ml_service.uci_meta["metrics"]

def test_sts_prediction_inference():
    # Primary hypothyroid test vector
    sample = {
        "AGE": 52.0, "SEX": "F", "DURATION": 4.0, "HGT": 150.0, "WGT": 62.0,
        "bmi": 27.5, "SYS": 130.0, "DIA": 85.0, "FBS": 90.0, "FT3": 2.2,
        "FT4": 0.55, "TSH": 28.0, "Anti_tpo": 4.0, "Visfatin": 20.0,
        "Thyroglobulin": 15.0, "IL6": 3.5, "TCHOL": 210.0, "TGL": 150.0,
        "HDL": 45.0, "LDL": 135.0, "HB": 12.0, "WBC": 6400.0, "PLT": 260.0
    }
    res = ml_service.predict_sts(sample)
    assert res["predicted_class"] == "Primary Hypothyroidism"
    assert res["model_version"] == "1.0.0"
    assert "Primary Hypothyroidism" in res["class_probabilities"]
    assert sum(res["class_probabilities"].values()) == pytest.approx(1.0, abs=0.01)
    assert len(res["explanation_rules"]) > 0

def test_sts_autoimmune_inference():
    # Autoimmune thyroiditis test vector (high Anti-TPO)
    sample = {
        "AGE": 38.0, "SEX": "F", "DURATION": 2.0, "HGT": 158.0, "WGT": 55.0,
        "bmi": 22.0, "SYS": 115.0, "DIA": 75.0, "FBS": 88.0, "FT3": 3.2,
        "FT4": 1.1, "TSH": 3.8, "Anti_tpo": 280.0, "Visfatin": 25.0,
        "Thyroglobulin": 40.0, "IL6": 6.0, "TCHOL": 180.0, "TGL": 110.0,
        "HDL": 55.0, "LDL": 100.0, "HB": 13.5, "WBC": 7100.0, "PLT": 270.0
    }
    res = ml_service.predict_sts(sample)
    assert res["predicted_class"] == "Autoimmune Thyroid Disease"
    assert len(res["explanation_rules"]) > 0

def test_uci_prediction_inference():
    sample = {
        "age": 45, "sex": "F", "on_thyroxine": False, "query_on_thyroxine": False,
        "on_antithyroid_medication": False, "sick": False, "pregnant": False,
        "thyroid_surgery": False, "I131_treatment": False, "query_hypothyroid": False,
        "query_hyperthyroid": False, "lithium": False, "goitre": False, "tumor": False,
        "hypopituitary": False, "psych": False, "TSH": 35.0, "T3": 1.1, "TT4": 30.0,
        "T4U": 1.2, "FTI": 25.0
    }
    res = ml_service.predict_uci(sample)
    assert "hypothyroid" in res["predicted_class"]
    assert sum(res["class_probabilities"].values()) == pytest.approx(1.0, abs=0.01)
