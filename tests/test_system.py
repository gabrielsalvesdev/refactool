import pytest
import time
from api.src.tasks import analyze_code_task
from api.src.cache.cluster import RedisCluster
from api.src.monitoring.metrics import get_metrics

@pytest.mark.system
def test_end_to_end_analysis(redis_connection):
    path = "tests/sample_project"
    
    # Limpa o cache antes do teste
    redis_connection.flushall()
    
    # Executa análise
    result = analyze_code_task.delay(path)
    task_result = result.get(timeout=60)
    
    assert task_result["status"] == "COMPLETED"
    assert "results" in task_result
    assert len(task_result["results"]) > 0

@pytest.mark.system
def test_system_metrics(redis_connection):
    path = "tests/sample_project"
    
    # Executa algumas análises
    tasks = [analyze_code_task.delay(path) for _ in range(3)]
    results = [t.get(timeout=60) for t in tasks]
    
    # Verifica métricas
    metrics = get_metrics()
    assert metrics["tasks_completed"] >= 3
    assert metrics["cache_hits"] >= 0
    assert metrics["cache_misses"] >= 0

@pytest.mark.system
def test_system_recovery(redis_connection):
    path = "tests/sample_project"
    
    # Simula falha no Redis
    redis_connection.client_kill_filter(_all=True)
    time.sleep(1)  # Aguarda reconexão
    
    # Tenta análise após recuperação
    result = analyze_code_task.delay(path)
    task_result = result.get(timeout=60)
    
    assert task_result["status"] == "COMPLETED" 