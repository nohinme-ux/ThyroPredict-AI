import requests

try:
    r = requests.get('http://127.0.0.1:8000/api/participants')
    participants = r.json()
    assert len(participants) > 0, "No participants found"
    p = participants[0]
    print(f"Testing live prediction for participant: {p['research_participant_code']} (ID: {p['id']})")

    pred_payload = {
        'participant_id': p['id'],
        'model_type': 'sts_clinical',
        'sts_features': {
            'AGE': 42.0, 'SEX': 'F', 'DURATION': 3.0, 'HGT': 155.0, 'WGT': 60.0,
            'bmi': 25.0, 'SYS': 120.0, 'DIA': 80.0, 'FBS': 95.0, 'FT3': 2.8,
            'FT4': 0.8, 'TSH': 15.0, 'Anti_tpo': 250.0, 'Visfatin': 25.0,
            'Thyroglobulin': 30.0, 'IL6': 5.0, 'TCHOL': 190.0, 'TGL': 130.0,
            'HDL': 48.0, 'LDL': 110.0, 'HB': 13.0, 'WBC': 6800.0, 'PLT': 250.0
        }
    }
    res = requests.post('http://127.0.0.1:8000/api/predictions', json=pred_payload)
    print("Prediction HTTP Status:", res.status_code)
    pred_data = res.json()
    print("Predicted Class:", pred_data['predicted_class'])
    print("Decision Rules (Explainability):", pred_data['explanation_rules'])
    print("Probabilities:", pred_data['class_probabilities'])

    # Verify audit persistence
    audit_res = requests.get('http://127.0.0.1:8000/api/predictions')
    records = audit_res.json()
    print(f"Total audit records in database: {len(records)}")
    assert any(rec['id'] == pred_data['id'] for rec in records), "New record not persisted in DB!"
    print("Verification Successful: Record persisted and retrievable!")
except Exception as e:
    print("Error during live transaction test:", e)
