import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("INDEPENDENT INFERENCE PIPELINE VERIFICATION")
print("=" * 60)

# Check health
health = requests.get(f"{BASE_URL}/health").json()
print("Health Status:", health)
assert health["status"] == "healthy"
assert health["models_loaded"]["sts_clinical"] is True
assert health["models_loaded"]["uci_benchmark"] is True

# Get a test participant
parts = requests.get(f"{BASE_URL}/api/participants").json()
assert len(parts) > 0, "No participants in database"
p_id = parts[0]["id"]
print(f"Using Participant ID: {p_id} ({parts[0]['research_participant_code']})")

test_cases = [
    {
        "name": "Case 1: Autoimmune Thyroid Disease (High Anti-TPO)",
        "features": {
            "AGE": 42.0, "SEX": "F", "DURATION": 3.0, "HGT": 155.0, "WGT": 60.0,
            "bmi": 25.0, "SYS": 120.0, "DIA": 80.0, "FBS": 95.0, "FT3": 2.8,
            "FT4": 0.8, "TSH": 15.0, "Anti_tpo": 320.0, "Visfatin": 25.0,
            "Thyroglobulin": 30.0, "IL6": 5.0, "TCHOL": 190.0, "TGL": 130.0,
            "HDL": 48.0, "LDL": 110.0, "HB": 13.0, "WBC": 6800.0, "PLT": 250.0
        },
        "expected_class": "Autoimmune Thyroid Disease",
        "expected_rule_substring": "Anti tpo"
    },
    {
        "name": "Case 2: Primary Hypothyroidism (High TSH, Low Anti-TPO)",
        "features": {
            "AGE": 55.0, "SEX": "F", "DURATION": 5.0, "HGT": 150.0, "WGT": 62.0,
            "bmi": 27.5, "SYS": 130.0, "DIA": 85.0, "FBS": 90.0, "FT3": 2.2,
            "FT4": 0.55, "TSH": 48.0, "Anti_tpo": 4.0, "Visfatin": 20.0,
            "Thyroglobulin": 15.0, "IL6": 3.5, "TCHOL": 210.0, "TGL": 150.0,
            "HDL": 45.0, "LDL": 135.0, "HB": 12.0, "WBC": 6400.0, "PLT": 260.0
        },
        "expected_class": "Primary Hypothyroidism",
        "expected_rule_substring": "TSH"
    },
    {
        "name": "Case 3: Hyperthyroid (Suppressed TSH < 0.4, Normal Anti-TPO)",
        "features": {
            "AGE": 30.0, "SEX": "F", "DURATION": 1.0, "HGT": 162.0, "WGT": 50.0,
            "bmi": 19.0, "SYS": 135.0, "DIA": 75.0, "FBS": 92.0, "FT3": 6.5,
            "FT4": 3.2, "TSH": 0.005, "Anti_tpo": 8.0, "Visfatin": 22.0,
            "Thyroglobulin": 40.0, "IL6": 4.0, "TCHOL": 160.0, "TGL": 100.0,
            "HDL": 46.0, "LDL": 95.0, "HB": 12.5, "WBC": 6000.0, "PLT": 240.0
        },
        "expected_class": "Hyperthyroid",
        "expected_rule_substring": "TSH"
    },
    {
        "name": "Case 4: Euthyroid Normal (Normal TSH, Normal Anti-TPO)",
        "features": {
            "AGE": 38.0, "SEX": "F", "DURATION": 0.0, "HGT": 160.0, "WGT": 58.0,
            "bmi": 22.6, "SYS": 110.0, "DIA": 70.0, "FBS": 88.0, "FT3": 3.2,
            "FT4": 1.2, "TSH": 2.1, "Anti_tpo": 6.0, "Visfatin": 20.0,
            "Thyroglobulin": 20.0, "IL6": 2.5, "TCHOL": 170.0, "TGL": 110.0,
            "HDL": 55.0, "LDL": 95.0, "HB": 13.5, "WBC": 6500.0, "PLT": 250.0
        },
        "expected_class": "Euthyroid / Normal",
        "expected_rule_substring": "threshold"
    }
]

for tc in test_cases:
    payload = {
        "participant_id": p_id,
        "model_type": "sts_clinical",
        "sts_features": tc["features"]
    }
    res = requests.post(f"{BASE_URL}/api/predictions", json=payload)
    assert res.status_code == 201, f"Failed for {tc['name']}: {res.text}"
    data = res.json()
    
    pred_class = data["predicted_class"]
    rules = data["explanation_rules"]
    probs = data["class_probabilities"]
    
    print(f"\n{tc['name']}:")
    print(f"  Predicted: {pred_class} (Expected: {tc['expected_class']})")
    print(f"  Probabilities: {probs}")
    print(f"  Rules ({len(rules)} nodes):")
    for r in rules:
        print(f"    • {r}")
    
    assert pred_class == tc["expected_class"], f"Mismatch for {tc['name']}: got {pred_class}"
    assert any(tc["expected_rule_substring"] in r for r in rules), f"Expected rule missing: {tc['expected_rule_substring']}"
    assert sum(probs.values()) == 1.0 or abs(sum(probs.values()) - 1.0) < 0.01

print("\n--- TEST: Malformed & Invalid Inputs ---")
# 1. Missing mandatory field TSH
bad_payload_1 = {
    "participant_id": p_id,
    "model_type": "sts_clinical",
    "sts_features": {"AGE": 40.0, "SEX": "F"}
}
r1 = requests.post(f"{BASE_URL}/api/predictions", json=bad_payload_1)
print("Missing TSH HTTP Status:", r1.status_code, "(Expected: 422)")
assert r1.status_code == 422

# 2. Impossible value (Age = 999)
bad_payload_2 = {
    "participant_id": p_id,
    "model_type": "sts_clinical",
    "sts_features": {
        "AGE": 999.0, "SEX": "F", "FT3": 2.5, "FT4": 1.0, "TSH": 2.0, "Anti_tpo": 5.0
    }
}
r2 = requests.post(f"{BASE_URL}/api/predictions", json=bad_payload_2)
print("Impossible Age=999 HTTP Status:", r2.status_code, "(Expected: 422)")
assert r2.status_code == 422

# 3. Invalid SEX category
bad_payload_3 = {
    "participant_id": p_id,
    "model_type": "sts_clinical",
    "sts_features": {
        "AGE": 40.0, "SEX": "UNKNOWN_SEX", "FT3": 2.5, "FT4": 1.0, "TSH": 2.0, "Anti_tpo": 5.0
    }
}
r3 = requests.post(f"{BASE_URL}/api/predictions", json=bad_payload_3)
print("Invalid SEX HTTP Status:", r3.status_code, "(Expected: 422)")
assert r3.status_code == 422

print("\nAll inference pipeline verifications PASSED!")
