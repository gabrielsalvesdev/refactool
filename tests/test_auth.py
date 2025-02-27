# tests/test_auth.py
import os
import pytest
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_missing_token():
    """Testa acesso sem token de autenticação"""
    response = client.post("/analyze", json={"path": "/valid/project"})
    assert response.status_code == 401

def test_invalid_token():
    """Testa acesso com token inválido"""
    response = client.post(
        "/analyze", 
        headers={"Authorization": "Bearer invalid_token"}, 
        json={"path": "/valid/project"}
    )
    assert response.status_code == 403

def test_valid_token():
    """Testa acesso com token válido"""
    api_key = os.getenv("API_KEY", "test_key")
    response = client.post(
        "/analyze", 
        headers={"Authorization": f"Bearer {api_key}"}, 
        json={"path": "/valid/project"}
    )
    assert response.status_code == 200 