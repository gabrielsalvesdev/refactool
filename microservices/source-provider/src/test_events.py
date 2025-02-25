"""
Testes para o sistema de eventos.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from webhook_manager import WebhookManager
import events

@pytest.fixture
def mock_webhook_manager():
    """Fixture que fornece um mock do WebhookManager."""
    manager = MagicMock(spec=WebhookManager)
    manager.trigger_event = AsyncMock()
    events.set_webhook_manager(manager)
    return manager

@pytest.mark.asyncio
async def test_workspace_created(mock_webhook_manager):
    """Testa o evento de workspace criado."""
    workspace_id = "test-workspace"
    repo_url = "https://github.com/test/repo"
    
    await events.workspace_created(workspace_id, repo_url)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "workspace.created",
        {
            "workspace_id": workspace_id,
            "repository_url": repo_url
        }
    )

@pytest.mark.asyncio
async def test_workspace_deleted(mock_webhook_manager):
    """Testa o evento de workspace deletado."""
    workspace_id = "test-workspace"
    
    await events.workspace_deleted(workspace_id)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "workspace.deleted",
        {
            "workspace_id": workspace_id
        }
    )

@pytest.mark.asyncio
async def test_changes_applied(mock_webhook_manager):
    """Testa o evento de mudanças aplicadas."""
    workspace_id = "test-workspace"
    changes = {"file": "test.py", "type": "modify"}
    
    await events.changes_applied(workspace_id, changes)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "changes.applied",
        {
            "workspace_id": workspace_id,
            "changes": changes
        }
    )

@pytest.mark.asyncio
async def test_changes_failed(mock_webhook_manager):
    """Testa o evento de falha ao aplicar mudanças."""
    workspace_id = "test-workspace"
    error = "Test error message"
    
    await events.changes_failed(workspace_id, error)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "changes.failed",
        {
            "workspace_id": workspace_id,
            "error": error
        }
    )

@pytest.mark.asyncio
async def test_analysis_started(mock_webhook_manager):
    """Testa o evento de início de análise."""
    workspace_id = "test-workspace"
    config = {"type": "test-analysis"}
    
    await events.analysis_started(workspace_id, config)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "analysis.started",
        {
            "workspace_id": workspace_id,
            "config": config
        }
    )

@pytest.mark.asyncio
async def test_analysis_completed(mock_webhook_manager):
    """Testa o evento de análise concluída."""
    workspace_id = "test-workspace"
    results = {"status": "success", "findings": []}
    
    await events.analysis_completed(workspace_id, results)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "analysis.completed",
        {
            "workspace_id": workspace_id,
            "results": results
        }
    )

@pytest.mark.asyncio
async def test_analysis_failed(mock_webhook_manager):
    """Testa o evento de falha na análise."""
    workspace_id = "test-workspace"
    error = "Test error message"
    
    await events.analysis_failed(workspace_id, error)
    
    mock_webhook_manager.trigger_event.assert_called_once_with(
        "analysis.failed",
        {
            "workspace_id": workspace_id,
            "error": error
        }
    )

def test_get_webhook_manager_not_initialized():
    """Testa o erro ao tentar obter o gerenciador não inicializado."""
    events._webhook_manager = None
    with pytest.raises(RuntimeError, match="WebhookManager não inicializado"):
        events.get_webhook_manager() 