# tests/test_integration.py
import os
from pathlib import Path
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_analyze_happy_path():
    """Testa o caminho feliz da análise de código"""
    # Usa o diretório de testes como projeto válido
    test_dir = Path(__file__).parent
    
    api_key = os.getenv("API_KEY", "test_key")
    response = client.post(
        "/analyze", 
        headers={"Authorization": f"Bearer {api_key}"},
        json={"path": str(test_dir)}
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "SUCCESS"

def test_analyze_invalid_path():
    """Testa análise com caminho inválido"""
    api_key = os.getenv("API_KEY", "test_key")
    response = client.post(
        "/analyze", 
        headers={"Authorization": f"Bearer {api_key}"},
        json={"path": "/invalid/path"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
