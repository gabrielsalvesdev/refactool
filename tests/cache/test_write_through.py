import hashlib
from api.src.tasks import analyze_code_task, redis_cache


def clear_cache(project_path):
    project_hash = hashlib.sha256(project_path.encode()).hexdigest()
    key_basic = f"analysis:{project_hash}"
    key_versioned = f"analysis_v2:{project_hash}"
    redis_cache.delete(key_basic)
    redis_cache.delete(key_versioned)


def test_cache_coherency():
    path = "tests/project_x"
    clear_cache(path)
    # Primeira execução: cache miss
    result1 = analyze_code_task.delay(path).get(timeout=60)
    # Segunda execução: deve ser cache hit
    result2 = analyze_code_task.delay(path).get(timeout=60)

    assert result1.get("cached") is False, "Primeira execução não deve usar cache"
    assert result2.get("cached") is True, "Segunda execução deve usar cache"
    assert result1.get("metrics") == result2.get("metrics"), "Os resultados devem ser idênticos" 