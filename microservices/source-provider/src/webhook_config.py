"""
Configuração dos webhooks do sistema.
"""

import os
from typing import List

from webhook_manager import WebhookConfig, WebhookManager

def get_discord_webhook_config() -> WebhookConfig:
    """
    Retorna a configuração do webhook do Discord.
    """
    url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not url:
        raise ValueError("DISCORD_WEBHOOK_URL não configurada")
    
    return WebhookConfig(
        url=url,
        event_types=[
            "workspace.created",
            "workspace.deleted",
            "changes.applied",
            "changes.failed",
            "analysis.started",
            "analysis.completed",
            "analysis.failed"
        ],
        headers={"Content-Type": "application/json"}
    )

def get_webhook_configs() -> List[WebhookConfig]:
    """
    Retorna todas as configurações de webhook do sistema.
    """
    configs = []
    
    # Discord webhook (se configurado)
    try:
        discord_config = get_discord_webhook_config()
        configs.append(discord_config)
    except ValueError:
        pass
    
    return configs

def setup_webhook_manager() -> WebhookManager:
    """
    Configura e retorna o gerenciador de webhooks.
    """
    manager = WebhookManager()
    
    # Registra todos os webhooks configurados
    for config in get_webhook_configs():
        manager.register_webhook(config)
    
    return manager 