"""
Testes para a configuração dos webhooks.
"""

import os
from unittest.mock import patch

import pytest

from webhook_config import get_discord_webhook_config, get_webhook_configs, setup_webhook_manager
from webhook_manager import WebhookConfig, WebhookManager

def test_get_discord_webhook_config_missing_url():
    """Testa o erro quando a URL do Discord não está configurada."""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="DISCORD_WEBHOOK_URL não configurada"):
            get_discord_webhook_config()

def test_get_discord_webhook_config_success():
    """Testa a configuração do webhook do Discord com sucesso."""
    test_url = "https://discord.webhook/test"
    with patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": test_url}):
        config = get_discord_webhook_config()
        
        assert isinstance(config, WebhookConfig)
        assert config.url == test_url
        assert "workspace.created" in config.event_types
        assert "workspace.deleted" in config.event_types
        assert "changes.applied" in config.event_types
        assert "changes.failed" in config.event_types
        assert "analysis.started" in config.event_types
        assert "analysis.completed" in config.event_types
        assert "analysis.failed" in config.event_types
        assert config.headers == {"Content-Type": "application/json"}

def test_get_webhook_configs_no_discord():
    """Testa obter configurações quando Discord não está configurado."""
    with patch.dict(os.environ, clear=True):
        configs = get_webhook_configs()
        assert len(configs) == 0

def test_get_webhook_configs_with_discord():
    """Testa obter configurações com Discord configurado."""
    test_url = "https://discord.webhook/test"
    with patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": test_url}):
        configs = get_webhook_configs()
        assert len(configs) == 1
        assert configs[0].url == test_url

def test_setup_webhook_manager_no_configs():
    """Testa configurar o gerenciador sem webhooks configurados."""
    with patch.dict(os.environ, clear=True):
        manager = setup_webhook_manager()
        assert isinstance(manager, WebhookManager)
        assert len(manager.webhooks) == 0

def test_setup_webhook_manager_with_discord():
    """Testa configurar o gerenciador com webhook do Discord."""
    test_url = "https://discord.webhook/test"
    with patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": test_url}):
        manager = setup_webhook_manager()
        assert isinstance(manager, WebhookManager)
        assert len(manager.webhooks) == 1
        assert manager.webhooks[0].url == test_url 