# tests/test_integration.py
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_analyze_happy_path():
    response = client.post("/analyze", json={"path": "/valid/project"})
    assert response.status_code == 200
    assert "issues" in response.json()
