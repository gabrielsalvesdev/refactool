# tests/test_auth.py
from fastapi.testclient import TestClient
from api.src.main import app
import os

client = TestClient(app)

def test_valid_token():
    os.environ["API_KEY"] = "SECRETO"
    response = client.post("/analyze", headers={"Authorization": "Bearer SECRETO"}, json={"path": "/valid/project"})
    # Deve permitir acesso, ou seja, status diferente de 403 (Forbidden)
    assert response.status_code != 403


def test_invalid_token():
    os.environ["API_KEY"] = "SECRETO"
    response = client.post("/analyze", headers={"Authorization": "Bearer ERRO"}, json={"path": "/valid/project"})
    # Com token inválido, espera-se status 403
    assert response.status_code == 403 