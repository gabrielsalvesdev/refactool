"""
Testes para o sistema de cache.
"""

import pytest
import hashlib
from fastapi.testclient import TestClient
from api.src.main import app
from api.src.tasks import analyze_code_task

@pytest.fixture
def test_client():
    """Fixture para o cliente de testes."""
    return TestClient(app)

def test_cache_hit(redis_connection):
    """Testa hit no cache."""
    path = "tests/sample_project"
    # Primeira execução (miss)
    task_1 = analyze_code_task.delay(path)
    result_1 = task_1.get(timeout=60)
    assert not result_1.get("cached", False), "Primeira execução deveria não ter cache"

    # Segunda execução (hit)
    task_2 = analyze_code_task.delay(path)
    result_2 = task_2.get(timeout=60)
    assert result_2.get("cached", False), "Segunda execução deveria usar cache"

def test_cache_invalidation(redis_connection, test_client):
    """Testa invalidação do cache."""
    path = "tests/sample_project"
    analyze_code_task.delay(path).get(timeout=60)
    hash_val = hashlib.sha256(path.encode()).hexdigest()
    cache_key = f"analysis:{hash_val}"
    response = test_client.delete(f"/invalidate-cache/{cache_key}")
    assert response.json()["status"] == "deleted"
    assert redis_connection.get(cache_key) is None 