# pyrefly: ignore[missing-import]
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"]["sts_clinical"] is True
    assert data["models_loaded"]["uci_benchmark"] is True

def test_model_info():
    res = client.get("/api/model/info")
    assert res.status_code == 200
    data = res.json()
    assert len(data["active_models"]) == 2

def test_model_metrics():
    res = client.get("/api/model/metrics?model_id=sts_clinical")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["accuracy"] > 0.90
    assert "confusion_matrix" in data["metrics"]

def test_participants_crud_and_prediction_flow():
    # 1. Create test participant
    code = "TEST-PART-999"
    p_data = {
        "research_participant_code": code,
        "display_name": "Test Subject 999",
        "age": 49.0,
        "sex": "F",
        "consent_status": True,
        "notes": "Automated integration testing profile"
    }
    p_res = client.post("/api/participants", json=p_data)
    assert p_res.status_code == 201
    participant = p_res.json()
    p_id = participant["id"]
    assert participant["research_participant_code"] == code

    # 2. Submit Prediction for this participant
    pred_payload = {
        "participant_id": p_id,
        "model_type": "sts_clinical",
        "sts_features": {
            "AGE": 49.0, "SEX": "F", "DURATION": 3.0, "HGT": 152.0, "WGT": 58.0,
            "bmi": 25.1, "SYS": 120.0, "DIA": 80.0, "FBS": 92.0, "FT3": 2.0,
            "FT4": 0.50, "TSH": 32.0, "Anti_tpo": 3.5, "Visfatin": 22.0,
            "Thyroglobulin": 18.0, "IL6": 4.0, "TCHOL": 190.0, "TGL": 130.0,
            "HDL": 50.0, "LDL": 110.0, "HB": 12.5, "WBC": 6800.0, "PLT": 250.0
        }
    }
    pred_res = client.post("/api/predictions", json=pred_payload)
    assert pred_res.status_code == 201
    prediction = pred_res.json()
    assert prediction["participant_id"] == p_id
    assert prediction["predicted_class"] == "Primary Hypothyroidism"
    assert len(prediction["explanation_rules"]) > 0
    pred_id = prediction["id"]

    # 3. Retrieve Prediction by ID
    get_pred = client.get(f"/api/predictions/{pred_id}")
    assert get_pred.status_code == 200
    assert get_pred.json()["id"] == pred_id

    # 4. List predictions with filter
    list_preds = client.get(f"/api/predictions?participant_id={p_id}")
    assert list_preds.status_code == 200
    assert len(list_preds.json()) >= 1

    # 5. Clean up: Delete prediction & participant
    del_pred = client.delete(f"/api/predictions/{pred_id}")
    assert del_pred.status_code == 204

    del_p = client.delete(f"/api/participants/{p_id}")
    assert del_p.status_code == 204

def test_overview_stats():
    res = client.get("/api/overview/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_participants" in data
    assert "total_predictions" in data
    assert "model_performance_summary" in data

def test_dataset_summary():
    res = client.get("/api/dataset/summary")
    assert res.status_code == 200
    data = res.json()
    assert "dictionary" in data
    assert "sts_stats" in data
