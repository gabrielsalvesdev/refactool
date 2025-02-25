"""
Gerenciamento de eventos do sistema.
"""

from typing import Any, Dict, Optional

from webhook_manager import WebhookManager

# Instância global do gerenciador de webhooks
_webhook_manager: Optional[WebhookManager] = None

def get_webhook_manager() -> WebhookManager:
    """
    Retorna a instância global do gerenciador de webhooks.
    """
    if _webhook_manager is None:
        raise RuntimeError("WebhookManager não inicializado")
    return _webhook_manager

def set_webhook_manager(manager: WebhookManager):
    """
    Define a instância global do gerenciador de webhooks.
    """
    global _webhook_manager
    _webhook_manager = manager

async def workspace_created(workspace_id: str, repository_url: str):
    """
    Evento disparado quando um workspace é criado.
    """
    await get_webhook_manager().trigger_event(
        "workspace.created",
        {
            "workspace_id": workspace_id,
            "repository_url": repository_url
        }
    )

async def workspace_deleted(workspace_id: str):
    """
    Evento disparado quando um workspace é deletado.
    """
    await get_webhook_manager().trigger_event(
        "workspace.deleted",
        {
            "workspace_id": workspace_id
        }
    )

async def changes_applied(workspace_id: str, changes: Dict[str, Any]):
    """
    Evento disparado quando mudanças são aplicadas com sucesso.
    """
    await get_webhook_manager().trigger_event(
        "changes.applied",
        {
            "workspace_id": workspace_id,
            "changes": changes
        }
    )

async def changes_failed(workspace_id: str, error: str):
    """
    Evento disparado quando ocorre um erro ao aplicar mudanças.
    """
    await get_webhook_manager().trigger_event(
        "changes.failed",
        {
            "workspace_id": workspace_id,
            "error": error
        }
    )

async def analysis_started(workspace_id: str, config: Dict[str, Any]):
    """
    Evento disparado quando uma análise é iniciada.
    """
    await get_webhook_manager().trigger_event(
        "analysis.started",
        {
            "workspace_id": workspace_id,
            "config": config
        }
    )

async def analysis_completed(workspace_id: str, results: Dict[str, Any]):
    """
    Evento disparado quando uma análise é concluída.
    """
    await get_webhook_manager().trigger_event(
        "analysis.completed",
        {
            "workspace_id": workspace_id,
            "results": results
        }
    )

async def analysis_failed(workspace_id: str, error: str):
    """
    Evento disparado quando ocorre um erro durante a análise.
    """
    await get_webhook_manager().trigger_event(
        "analysis.failed",
        {
            "workspace_id": workspace_id,
            "error": error
        }
    ) 