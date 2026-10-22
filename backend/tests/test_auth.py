from fastapi.testclient import TestClient
from backend.app.main import app
import uuid

client = TestClient(app)

def test_auth_workflow():
    unique_email = f"researcher_{uuid.uuid4().hex[:6]}@example.com"
    pwd = "ValidPassword123!"

    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": pwd,
        "role": "researcher"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]

    # 2. Duplicate registration fails
    dup_res = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": pwd
    })
    assert dup_res.status_code == 400

    # 3. Login
    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": pwd
    })
    assert login_res.status_code == 200
    login_token = login_res.json()["access_token"]

    # 4. Profile /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email
