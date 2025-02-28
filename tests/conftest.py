"""Configurações globais para testes."""
import pytest
from redis import Redis, ConnectionError
import os
import time
import redis
from typing import Generator
from prometheus_client import CollectorRegistry

def pytest_configure(config):
    """Configuração global dos testes"""
    config.addinivalue_line(
        "markers",
        "unit: testes unitários rápidos (timeout: 3s)"
    )
    config.addinivalue_line(
        "markers",
        "integration: testes de integração (timeout: 30s)"
    )
    config.addinivalue_line(
        "markers",
        "system: testes de sistema completo (timeout: 120s)"
    )
    config.addinivalue_line(
        "markers",
        "stress: testes de carga e performance (ambiente dedicado)"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Configura variáveis de ambiente para testes."""
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["CACHE_TTL"] = "3600"
    os.environ["API_KEY"] = "test_key"
    yield
    # Limpa as variáveis após os testes
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)
    os.environ.pop("CACHE_TTL", None)
    os.environ.pop("API_KEY", None)

@pytest.fixture(scope="session")
def redis_connection() -> Generator[redis.Redis, None, None]:
    """Conexão Redis com configuração baseada no tipo de teste"""
    if pytest.current_test.get_closest_marker("stress"):
        # Configuração para testes de stress
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=1,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
            retry_on_timeout=True,
            max_connections=50
        )
    else:
        # Configuração padrão para outros testes
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=1,
            socket_timeout=2.0,
            decode_responses=True
        )
    
    try:
        yield client
    finally:
        client.close()

@pytest.fixture(autouse=True)
def setup_test_env(request):
    """Configura ambiente baseado no tipo de teste"""
    marker = request.node.get_closest_marker("stress")
    if marker:
        # Configuração para testes de stress
        os.environ["CELERY_WORKER_POOL"] = "prefork"
        os.environ["CELERY_MAX_TASKS_PER_CHILD"] = "100"
        os.environ["CELERY_WORKER_CONCURRENCY"] = "4"
    else:
        # Configuração padrão
        os.environ["CELERY_WORKER_POOL"] = "solo"
        os.environ["CELERY_MAX_TASKS_PER_CHILD"] = "10"
        os.environ["CELERY_WORKER_CONCURRENCY"] = "1"

@pytest.fixture
def metrics_registry():
    """Registry isolado para métricas de teste"""
    return CollectorRegistry()

@pytest.fixture(autouse=True)
def timeout_setup(request):
    """Configura timeouts dinâmicos baseados no tipo de teste"""
    marker = request.node.get_closest_marker("unit")
    if marker:
        request.node.add_marker(pytest.mark.timeout(3))
    elif request.node.get_closest_marker("integration"):
        request.node.add_marker(pytest.mark.timeout(30))
    elif request.node.get_closest_marker("system"):
        request.node.add_marker(pytest.mark.timeout(120))
    elif request.node.get_closest_marker("stress"):
        request.node.add_marker(pytest.mark.timeout(300))