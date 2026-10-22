import pytest
from fastapi.testclient import TestClient
import uuid
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import ResearchParticipant, Prediction, User

client = TestClient(app)

def test_participant_nonexistent_fails():
    """Verify that submitting a prediction for a non-existent participant returns 404."""
    payload = {
        "participant_id": "non-existent-uuid-12345",
        "model_type": "sts_clinical",
        "sts_features": {
            "AGE": 45.0, "SEX": "F", "FT3": 2.5, "FT4": 1.0, "TSH": 3.0, "Anti_tpo": 10.0
        }
    }
    res = client.post("/api/predictions", json=payload)
    assert res.status_code == 404
    assert "Participant not found" in res.json()["detail"]

def test_invalid_model_type_fails():
    """Verify that an invalid model type returns 422 validation error."""
    # First get an existing participant
    p_res = client.get("/api/participants")
    p_id = p_res.json()[0]["id"]

    payload = {
        "participant_id": p_id,
        "model_type": "quantum_neural_network_invalid",
        "sts_features": {
            "AGE": 45.0, "SEX": "F", "FT3": 2.5, "FT4": 1.0, "TSH": 3.0, "Anti_tpo": 10.0
        }
    }
    res = client.post("/api/predictions", json=payload)
    assert res.status_code == 422

def test_missing_features_validation():
    """Verify that missing required features like TSH or Anti_tpo fails with 422."""
    p_res = client.get("/api/participants")
    p_id = p_res.json()[0]["id"]

    payload = {
        "participant_id": p_id,
        "model_type": "sts_clinical",
        "sts_features": {
            "AGE": 45.0,
            "SEX": "F"
            # Missing FT3, FT4, TSH, Anti_tpo
        }
    }
    res = client.post("/api/predictions", json=payload)
    assert res.status_code == 422

def test_out_of_range_features_validation():
    """Verify that impossible values (e.g. AGE = -10 or AGE = 500) fail validation with 422."""
    p_res = client.get("/api/participants")
    p_id = p_res.json()[0]["id"]

    payload = {
        "participant_id": p_id,
        "model_type": "sts_clinical",
        "sts_features": {
            "AGE": -10.0, # Invalid age
            "SEX": "F",
            "FT3": 2.5,
            "FT4": 1.0,
            "TSH": 3.0,
            "Anti_tpo": 10.0
        }
    }
    res = client.post("/api/predictions", json=payload)
    assert res.status_code == 422

def test_sql_injection_resilience():
    """Verify search endpoint safely parameterizes inputs against SQL injection."""
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE predictions; --",
        "UNION SELECT * FROM users --",
        "1' OR 1=1--"
    ]
    for injection in sql_payloads:
        res = client.get(f"/api/participants?search={injection}")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        pred_res = client.get(f"/api/predictions?search={injection}")
        assert pred_res.status_code == 200
        assert isinstance(pred_res.json(), list)

def test_persistence_integrity_and_cascade_delete():
    """Verify relational foreign key constraints and cascade deletion."""
    test_code = f"CASCADE-TEST-{uuid.uuid4().hex[:6]}"
    p_res = client.post("/api/participants", json={
        "research_participant_code": test_code,
        "display_name": "Cascade Test Subject",
        "age": 50.0,
        "sex": "F",
        "consent_status": True
    })
    assert p_res.status_code == 201
    p_id = p_res.json()["id"]

    # Submit 2 predictions for this participant
    for tsh_val in [2.5, 45.0]:
        pred_res = client.post("/api/predictions", json={
            "participant_id": p_id,
            "model_type": "sts_clinical",
            "sts_features": {
                "AGE": 50.0, "SEX": "F", "DURATION": 1.0, "HGT": 160.0, "WGT": 65.0,
                "bmi": 25.4, "SYS": 120.0, "DIA": 80.0, "FBS": 90.0, "FT3": 2.5,
                "FT4": 1.0, "TSH": tsh_val, "Anti_tpo": 8.0, "Visfatin": 22.0,
                "Thyroglobulin": 20.0, "IL6": 3.0, "TCHOL": 180.0, "TGL": 120.0,
                "HDL": 50.0, "LDL": 100.0, "HB": 13.0, "WBC": 6500.0, "PLT": 250.0
            }
        })
        assert pred_res.status_code == 201

    # Verify participant has 2 predictions
    preds_before = client.get(f"/api/predictions?participant_id={p_id}").json()
    assert len(preds_before) == 2

    # Delete participant -> predictions must be cascade-deleted
    del_res = client.delete(f"/api/participants/{p_id}")
    assert del_res.status_code == 204

    # Verify predictions are gone
    preds_after = client.get(f"/api/predictions?participant_id={p_id}").json()
    assert len(preds_after) == 0

def test_export_endpoint():
    """Verify research CSV export endpoint produces valid formatted CSV data."""
    res = client.get("/api/research/export?anonymize=true")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    lines = content.strip().split("\r\n") if "\r\n" in content else content.strip().split("\n")
    assert len(lines) >= 1 # Has header
    assert "Record_ID" in lines[0]
    assert "Model_Name" in lines[0]
