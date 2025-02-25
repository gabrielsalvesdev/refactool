import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientResponse, ClientSession

from webhook_manager import WebhookConfig, WebhookManager, WebhookPayload

@pytest.fixture
def webhook_manager():
    return WebhookManager()

@pytest.fixture
def webhook_config():
    return WebhookConfig(
        url="http://test.com/webhook",
        event_types=["test.event"],
        headers={"X-Test": "true"},
        retry_count=2,
        timeout=5
    )

@pytest.mark.asyncio
async def test_webhook_manager_init(webhook_manager):
    assert webhook_manager.webhooks == []
    assert webhook_manager.session is None
    assert webhook_manager._running is False
    assert webhook_manager._task is None

@pytest.mark.asyncio
async def test_webhook_manager_start_stop(webhook_manager):
    await webhook_manager.start()
    assert webhook_manager._running is True
    assert webhook_manager.session is not None
    assert webhook_manager._task is not None

    await webhook_manager.stop()
    assert webhook_manager._running is False
    assert webhook_manager._task is None

@pytest.mark.asyncio
async def test_register_webhook(webhook_manager, webhook_config):
    webhook_manager.register_webhook(webhook_config)
    assert len(webhook_manager.webhooks) == 1
    assert webhook_manager.webhooks[0] == webhook_config

@pytest.mark.asyncio
async def test_trigger_event_no_webhooks(webhook_manager):
    await webhook_manager.start()
    await webhook_manager.trigger_event("test.event", {"message": "test"})
    await webhook_manager.stop()

@pytest.mark.asyncio
async def test_trigger_event_with_webhook(webhook_manager, webhook_config):
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200

    mock_session = AsyncMock(spec=ClientSession)
    mock_session.post.return_value.__aenter__.return_value = mock_response

    webhook_manager.register_webhook(webhook_config)
    await webhook_manager.start()

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await webhook_manager.trigger_event("test.event", {"message": "test"})
        await asyncio.sleep(0.1)  # Allow queue processing

    mock_session.post.assert_called_once()
    args, kwargs = mock_session.post.call_args
    assert args[0] == webhook_config.url
    assert kwargs["headers"] == webhook_config.headers

    await webhook_manager.stop()

@pytest.mark.asyncio
async def test_webhook_payload_serialization():
    data = {"message": "test"}
    payload = WebhookPayload(event_type="test.event", data=data)
    
    assert payload.event_type == "test.event"
    assert payload.data == data
    assert isinstance(payload.timestamp, datetime)

@pytest.mark.asyncio
async def test_webhook_retry_mechanism(webhook_manager, webhook_config):
    # Configurar mock para falhar nas primeiras tentativas
    responses = [
        AsyncMock(spec=ClientResponse, status=500),
        AsyncMock(spec=ClientResponse, status=500),
        AsyncMock(spec=ClientResponse, status=200)
    ]
    
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.post.return_value.__aenter__.side_effect = responses

    webhook_manager.register_webhook(webhook_config)
    await webhook_manager.start()

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await webhook_manager.trigger_event("test.event", {"message": "test"})
        await asyncio.sleep(0.5)  # Allow retries to complete

    assert mock_session.post.call_count == 3  # Initial + 2 retries
    await webhook_manager.stop() 