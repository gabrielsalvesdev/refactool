import pytest
import asyncio
from unittest.mock import patch
from api.src.tasks import analyze_code_task

async def get_task_result(task, timeout=5):
    """
    Obtém o resultado de uma task de forma assíncrona.
    """
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        if task.ready():
            return task.result
        await asyncio.sleep(0.1)
    raise TimeoutError("Task não completou no tempo esperado")

@pytest.mark.asyncio
async def test_analyze_code_task_validation():
    """
    Testa validação de caminho None.
    """
    task = analyze_code_task.delay(None)
    result = await get_task_result(task)
    assert result["status"] == "ERROR"
    assert "Caminho não pode ser vazio" in result["message"]

@pytest.mark.asyncio
async def test_analyze_code_task_empty_path():
    """
    Testa validação de caminho vazio.
    """
    task = analyze_code_task.delay("")
    result = await get_task_result(task)
    assert result["status"] == "ERROR"
    assert "Caminho não pode ser vazio" in result["message"]

@pytest.mark.asyncio
@patch('api.src.tasks.os.path.exists')
async def test_analyze_code_task_nonexistent_path(mock_exists):
    """
    Testa validação de caminho inexistente.
    """
    mock_exists.return_value = False
    task = analyze_code_task.delay("/path/not/exists")
    result = await get_task_result(task)
    assert result["status"] == "ERROR"
    assert "Caminho não existe" in result["message"]

@pytest.mark.asyncio
@patch('api.src.tasks.os.path.exists')
async def test_analyze_code_task_success(mock_exists):
    """
    Testa análise bem sucedida.
    """
    mock_exists.return_value = True
    task = analyze_code_task.delay("/valid/path")
    result = await get_task_result(task)
    assert result["status"] == "COMPLETED" 