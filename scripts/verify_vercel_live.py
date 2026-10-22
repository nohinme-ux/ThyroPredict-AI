import urllib.request
import json
import sys

BASE_URL = 'https://thyropredict-ai.vercel.app'

print(f"Connecting to live production deployment: {BASE_URL}")

# 1. Login
data = json.dumps({'email': 'researcher@thyropredict.ai', 'password': 'Research@2026'}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/auth/login', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
token = json.loads(resp.read().decode())['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print(f"[PASS] Authentication HTTP {resp.status} - JWT token issued")

# 2. Model Catalog
req = urllib.request.Request(f'{BASE_URL}/api/model/info', headers=headers)
resp = urllib.request.urlopen(req)
models = json.loads(resp.read().decode())['active_models']
print(f"[PASS] Model Catalog HTTP {resp.status} - Active models: {[m['id'] for m in models]}")

# 3. Model Metrics
req = urllib.request.Request(f'{BASE_URL}/api/model/metrics', headers=headers)
resp = urllib.request.urlopen(req)
metrics = json.loads(resp.read().decode())
acc = metrics['metrics']['accuracy']
macro_f1 = metrics['metrics']['macro_f1']
print(f"[PASS] Model Metrics HTTP {resp.status} - STS Accuracy: {acc*100:.2f}% | Macro F1: {macro_f1*100:.2f}%")

# 4. Create Participant
import time
unique_code = f"VERCEL-TEST-{int(time.time())}"
p_data = json.dumps({
    'research_participant_code': unique_code,
    'display_name': 'Live Vercel Verification Subject',
    'age': 48.0,
    'sex': 'F',
    'consent_status': True,
    'notes': 'Automated live Vercel cloud test'
}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/participants', data=p_data, headers=headers)
resp = urllib.request.urlopen(req)
participant = json.loads(resp.read().decode())
pid = participant['id']
print(f"[PASS] Participant Creation HTTP {resp.status} - Code: {unique_code} | ID: {pid}")

# 5. STS Clinical Model Prediction
pred_data = json.dumps({
    'participant_id': pid,
    'model_type': 'sts_clinical',
    'sts_features': {
        'AGE': 45.0,
        'SEX': 'F',
        'DURATION': 1.0,
        'HGT': 160.0,
        'WGT': 65.0,
        'bmi': 25.4,
        'SYS': 120.0,
        'DIA': 80.0,
        'FBS': 95.0,
        'FT3': 2.8,
        'FT4': 1.2,
        'TSH': 8.5,
        'Anti_tpo': 150.0,
        'Visfatin': 25.0,
        'Thyroglobulin': 20.0,
        'IL6': 4.0,
        'TCHOL': 180.0,
        'TGL': 130.0,
        'HDL': 45.0,
        'LDL': 100.0,
        'HB': 13.0,
        'WBC': 7000.0,
        'PLT': 250.0
    }
}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/predictions', data=pred_data, headers=headers)
resp = urllib.request.urlopen(req)
prediction = json.loads(resp.read().decode())
pred_class = prediction['predicted_class']
prob = prediction['class_probabilities'].get(pred_class, 1.0)
print(f"[PASS] STS Prediction HTTP {resp.status} - Predicted: '{pred_class}' (Probability: {prob*100:.1f}%)")
print(f"       Explanation Rule: {prediction['explanation_rules'][0] if prediction['explanation_rules'] else 'N/A'}")

# 6. UCI Benchmark Model Prediction
uci_pred_data = json.dumps({
    'participant_id': pid,
    'model_type': 'uci_benchmark',
    'uci_features': {
        'age': 55.0,
        'sex': 'F',
        'on_thyroxine': False,
        'query_on_thyroxine': False,
        'on_antithyroid_medication': False,
        'sick': False,
        'pregnant': False,
        'thyroid_surgery': False,
        'I131_treatment': False,
        'query_hypothyroid': True,
        'query_hyperthyroid': False,
        'lithium': False,
        'goitre': False,
        'tumor': False,
        'hypopituitary': False,
        'psych': False,
        'TSH': 15.0,
        'T3': 1.2,
        'TT4': 45.0,
        'T4U': 0.95,
        'FTI': 47.4
    }
}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/predictions', data=uci_pred_data, headers=headers)
resp = urllib.request.urlopen(req)
uci_pred = json.loads(resp.read().decode())
uci_class = uci_pred['predicted_class']
uci_prob = uci_pred['class_probabilities'].get(uci_class, 1.0)
print(f"[PASS] UCI Prediction HTTP {resp.status} - Predicted: '{uci_class}' (Probability: {uci_prob*100:.1f}%)")
print(f"       Explanation Rule: {uci_pred['explanation_rules'][0] if uci_pred['explanation_rules'] else 'N/A'}")

# 7. Analytics Overview
req = urllib.request.Request(f'{BASE_URL}/api/overview/stats', headers=headers)
resp = urllib.request.urlopen(req)
stats = json.loads(resp.read().decode())
print(f"[PASS] Analytics Overview HTTP {resp.status} - Total Participants: {stats['total_participants']} | Total Predictions: {stats['total_predictions']}")

# 8. Research Export
req = urllib.request.Request(f'{BASE_URL}/api/research/export', headers=headers)
resp = urllib.request.urlopen(req)
export_data = resp.read().decode()
row_count = len(export_data.strip().split('\n'))
print(f"[PASS] Research Audit CSV Export HTTP {resp.status} - Exported {row_count} rows")

print("\n=======================================================")
print("ALL LIVE PRODUCTION VERIFICATION TESTS PASSED ON VERCEL!")
print("Production URL: https://thyropredict-ai.vercel.app")
print("=======================================================")
