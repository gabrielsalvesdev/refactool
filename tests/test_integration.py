# tests/test_integration.py
import os
from pathlib import Path
from fastapi.testclient import TestClient
from api.src.main import app
import pytest
from api.src.tasks import analyze_code_task
from api.src.cache.cluster import RedisCluster

client = TestClient(app)

@pytest.mark.integration
def test_analyze_happy_path(redis_connection):
    path = "tests/sample_project"
    result = analyze_code_task.delay(path)
    assert result is not None
    task_result = result.get(timeout=30)
    assert task_result["status"] == "COMPLETED"
    assert "results" in task_result

@pytest.mark.integration
def test_cache_integration(redis_connection):
    path = "tests/sample_project"
    
    # Primeira execução
    result1 = analyze_code_task.delay(path)
    task_result1 = result1.get(timeout=30)
    
    # Segunda execução (deve usar cache)
    result2 = analyze_code_task.delay(path)
    task_result2 = result2.get(timeout=30)
    
    assert task_result1 == task_result2
    assert task_result1["status"] == "COMPLETED"

@pytest.mark.integration
def test_analyze_invalid_path(redis_connection):
    with pytest.raises(ValueError):
        result = analyze_code_task.delay("/invalid/path")
        result.get(timeout=30)

@pytest.mark.integration
def test_api_analyze_happy_path():
    """Testa o caminho feliz da análise de código via API"""
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

@pytest.mark.integration
def test_api_analyze_invalid_path():
    """Testa análise com caminho inválido via API"""
    api_key = os.getenv("API_KEY", "test_key")
    
    response = client.post(
        "/analyze", 
        headers={"Authorization": f"Bearer {api_key}"},
        json={"path": "/invalid/path"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
