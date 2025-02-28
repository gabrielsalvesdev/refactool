import pytest
import time
import logging
import asyncio
from redis import Redis
from api.src.tasks import analyze_code_task

logger = logging.getLogger(__name__)

@pytest.fixture
def redis_connection():
    return Redis(host='localhost', port=6379, db=1)

@pytest.fixture(autouse=True)
async def setup_test_env(redis_connection):
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

async def wait_for_task_result(task, timeout=60):
    """
    Aguarda o resultado de uma task de forma assíncrona.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if task.ready():
            return task.result
        await asyncio.sleep(0.1)
    raise TimeoutError("Task não completou no tempo esperado")

@pytest.mark.asyncio
async def test_end_to_end_analysis(redis_connection):
    """
    Testa o fluxo completo de análise de código.
    """
    path = "tests/sample_project"
    
    # Executa análise
    task = analyze_code_task.delay(path)
    result = await wait_for_task_result(task)
    
    assert result["status"] == "COMPLETED"
    assert "message" in result

@pytest.mark.asyncio
async def test_system_metrics(redis_connection):
    """
    Testa a coleta de métricas do sistema.
    """
    path = "tests/sample_project"
    
    # Executa análises em paralelo
    tasks = [analyze_code_task.delay(path) for _ in range(3)]
    
    # Aguarda resultados
    results = []
    for task in tasks:
        try:
            result = await wait_for_task_result(task)
            results.append(result)
        except Exception as e:
            logger.error(f"Erro em task: {str(e)}")
    
    successful = [r for r in results if r["status"] == "COMPLETED"]
    assert len(successful) >= len(tasks) * 0.8

@pytest.mark.asyncio
async def test_system_recovery(redis_connection):
    """
    Testa a recuperação do sistema após falha no Redis.
    """
    path = "tests/sample_project"
    
    # Simula falha no Redis
    try:
        redis_connection.client_kill_filter(type='normal')
    except Exception as e:
        logger.warning(f"Erro ao simular falha no Redis: {str(e)}")
    
    # Aguarda reconexão
    await asyncio.sleep(1)
    
    # Tenta análise após falha
    task = analyze_code_task.delay(path)
    result = await wait_for_task_result(task)
    
    assert result["status"] == "COMPLETED"

@pytest.mark.asyncio
async def test_concurrent_analysis(redis_connection):
    """
    Testa análise concorrente de código.
    """
    path = "tests/sample_project"
    
    # Executa análises concorrentes
    tasks = [analyze_code_task.delay(path) for _ in range(5)]
    
    # Aguarda resultados
    results = []
    for task in tasks:
        try:
            result = await wait_for_task_result(task)
            results.append(result)
        except Exception as e:
            logger.error(f"Erro em task concorrente: {str(e)}")
    
    successful = [r for r in results if r["status"] == "COMPLETED"]
    assert len(successful) >= len(tasks) * 0.8 