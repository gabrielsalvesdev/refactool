from api.src.tasks import analyze_code_task
from pathlib import Path
import pytest


def test_task_success():
    # Usa o diretório de testes como projeto válido
    test_dir = Path(__file__).parent
    result = analyze_code_task.apply(args=[str(test_dir)]).get()
    assert result["status"] == "SUCCESS"
    assert "result" in result
    assert "metrics" in result["result"]
    assert "smells" in result["result"]


def test_task_failure():
    # Testa com um caminho inválido
    result = analyze_code_task.apply(args=["/invalid/path"]).get()
    assert result["status"] == "ERROR"
    assert "error" in result 