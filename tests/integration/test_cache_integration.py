import hashlib
import time
from api.src.tasks import analyze_code_task, redis_cache, get_project_size
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_cache_hit():
    path = "tests/sample_project"
    # Primeira execução (miss)
    task_1 = analyze_code_task.delay(path)
    result_1 = task_1.get(timeout=60)
    assert not result_1.get("cached", False), "Primeira execução deveria não ter cache"
    
    # Segunda execução (hit)
    task_2 = analyze_code_task.delay(path)
    result_2 = task_2.get(timeout=60)
    assert result_2.get("cached", False), "Segunda execução deveria usar cache"


def test_cache_expiry():
    path = "tests/sample_project"
    # Preencher cache
    analyze_code_task.delay(path).get(timeout=60)
    # Forçar expiração do cache para 1 segundo
    cache_key = f"analysis:{hashlib.sha256(path.encode()).hexdigest()}"
    redis_cache.expire(cache_key, 1)
    time.sleep(2)  # Espera a expiração
    task = analyze_code_task.delay(path)
    result = task.get(timeout=60)
    assert not result.get("cached", False), "Após expiração, não deve ter cache"


def test_cache_ttl():
    path = "tests/sample_project"
    analyze_code_task.delay(path).get(timeout=60)
    cache_key = f"analysis:{hashlib.sha256(path.encode()).hexdigest()}"
    ttl = redis_cache.ttl(cache_key)
    project_size = get_project_size(path)
    if project_size < 1_000_000:
        assert 3580 < ttl <= 3600, f"TTL should be near 3600, but got {ttl}"
    else:
        assert 580 < ttl <= 600, f"TTL should be near 600, but got {ttl}"


def test_cache_invalidation_api():
    path = "tests/sample_project"
    # Preenche o cache
    analyze_code_task.delay(path).get(timeout=60)
    hash_val = hashlib.sha256(path.encode()).hexdigest()
    cache_key = f"analysis:{hash_val}"
    response = client.delete(f"/invalidate-cache/{cache_key}")
    assert response.json()["status"] == "deleted"
    assert redis_cache.get(cache_key) is None 