import pytest
from api.src.tasks import analyze_code_task
from unittest.mock import patch, MagicMock

@pytest.mark.unit
def test_analyze_code_task_validation():
    with pytest.raises(ValueError):
        analyze_code_task.delay(None)

@pytest.mark.unit
def test_analyze_code_task_empty_path():
    with pytest.raises(ValueError):
        analyze_code_task.delay("")

@pytest.mark.unit
@patch('api.src.tasks.os.path.exists')
def test_analyze_code_task_nonexistent_path(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(ValueError):
        analyze_code_task.delay("/path/not/exists")

@pytest.mark.unit
@patch('api.src.tasks.os.path.exists')
@patch('api.src.tasks.analyze_directory')
def test_analyze_code_task_success(mock_analyze, mock_exists):
    mock_exists.return_value = True
    mock_analyze.return_value = {"status": "COMPLETED", "results": []}
    
    result = analyze_code_task.delay("/valid/path")
    assert result is not None 