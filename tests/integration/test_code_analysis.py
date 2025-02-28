import pytest
from api.src.tasks import analyze_code_task
from pathlib import Path

@pytest.fixture
def valid_project_path():
    return "tests/sample_project"

@pytest.fixture
def invalid_project_path():
    return "tests/nonexistent_folder"


def test_analysis_with_valid_path(valid_project_path):
    task = analyze_code_task.delay(valid_project_path)
    result = task.get(timeout=30)
    assert result["status"] == "COMPLETED"
    assert result["metrics"]["score"] >= 6.0  # Score mínimo tolerável


def test_analysis_with_invalid_path():
    task = analyze_code_task.delay("/caminho/inexistente")
    result = task.get(timeout=10)
    assert result["status"] == "FAILED"
    assert "Diretório inválido" in result["error"]


@pytest.mark.stress
@pytest.mark.timeout(300)
def test_concurrent_analysis(valid_project_path):
    tasks = [analyze_code_task.delay(valid_project_path) for _ in range(20)]
    results = []
    for t in tasks:
        try:
            result = t.get(timeout=45)
            results.append(result)
        except Exception as e:
            print(f"Task failed: {str(e)}")
            
    successful = [r for r in results if r and r.get("status") == "COMPLETED"]
    assert len(successful) >= len(tasks) * 0.8, f"Expected at least 80% success rate, got {len(successful)}/{len(tasks)}" 