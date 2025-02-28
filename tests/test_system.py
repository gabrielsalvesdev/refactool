import pytest
import time
from api.src.tasks import analyze_code_task
from api.src.cache.cluster import RedisCluster
from api.src.monitoring.metrics import get_metrics
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def setup_test_env(redis_connection):
    """
    Configura ambiente de teste e limpa o cache.
    """
    try:
        redis_connection.flushall()
    except Exception as e:
        logger.warning(f"Erro ao limpar cache: {str(e)}")
    yield
    try:
        redis_connection.flushall()
    except Exception as e:
        logger.warning(f"Erro ao limpar cache após teste: {str(e)}")

@pytest.mark.system
def test_end_to_end_analysis(redis_connection):
    """
    Testa o fluxo completo de análise de código.
    """
    path = "tests/sample_project"
    
    # Executa análise
    result = analyze_code_task.delay(path)
    task_result = result.get(timeout=60)
    
    assert task_result["status"] == "COMPLETED"
    assert "result" in task_result
    assert isinstance(task_result["result"], dict)

@pytest.mark.system
def test_system_metrics(redis_connection):
    """
    Testa a coleta de métricas do sistema.
    """
    path = "tests/sample_project"
    
    # Executa algumas análises
    results = []
    for _ in range(3):
        result = analyze_code_task.delay(path)
        results.append(result)
    
    # Aguarda conclusão
    for result in results:
        task_result = result.get(timeout=60)
        assert task_result["status"] == "COMPLETED"
    
    # Verifica métricas
    metrics = get_metrics()
    assert metrics["tasks_completed"] >= 3
    assert metrics["cache_hits"] >= 0
    assert metrics["cache_misses"] >= 0
    assert metrics["system_memory"] > 0
    assert metrics["system_cpu"] >= 0

@pytest.mark.system
def test_system_recovery(redis_connection):
    """
    Testa a recuperação do sistema após falha no Redis.
    """
    path = "tests/sample_project"
    
    # Simula falha no Redis
    try:
        redis_connection.client_kill(type='normal')
    except Exception as e:
        logger.warning(f"Erro ao simular falha no Redis: {str(e)}")
    
    # Aguarda um momento para reconexão
    time.sleep(1)
    
    # Tenta executar análise após falha
    result = analyze_code_task.delay(path)
    task_result = result.get(timeout=60)
    
    assert task_result["status"] == "COMPLETED"
    assert not task_result.get("cached", False)  # Não deve usar cache após falha

@pytest.mark.system
def test_concurrent_analysis(redis_connection):
    """
    Testa análise concorrente de código.
    """
    path = "tests/sample_project"
    
    # Executa múltiplas análises concorrentes
    tasks = [analyze_code_task.delay(path) for _ in range(5)]
    
    # Aguarda conclusão
    results = []
    for task in tasks:
        try:
            result = task.get(timeout=60)
            results.append(result)
        except Exception as e:
            logger.error(f"Erro em task concorrente: {str(e)}")
    
    # Verifica resultados
    successful = [r for r in results if r and r["status"] == "COMPLETED"]
    assert len(successful) >= len(tasks) * 0.8  # Pelo menos 80% de sucesso 