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
    config.addinivalue_line("markers", "unit: testes unitários rápidos (timeout: 3s)")
    config.addinivalue_line("markers", "integration: testes de integração (timeout: 30s)")
    config.addinivalue_line("markers", "system: testes de sistema completo (timeout: 120s)")
    config.addinivalue_line("markers", "stress: testes de carga e performance (ambiente dedicado)")
    config.addinivalue_line("markers", "normal: testes com configuração padrão")

def pytest_collection_modifyitems(config, items):
    """Validação e modificação dos itens de teste coletados"""
    for item in items:
        if "redis_connection" in item.fixturenames:
            if item.get_closest_marker("stress") is None:
                item.add_marker(pytest.mark.normal)

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Configura variáveis de ambiente para testes."""
    test_env = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "CACHE_TTL": "3600",
        "API_KEY": "test_key"
    }
    
    # Backup das variáveis existentes
    old_env = {k: os.environ.get(k) for k in test_env}
    
    # Configura ambiente de teste
    os.environ.update(test_env)
    
    yield
    
    # Restaura ambiente original
    for k, v in old_env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

@pytest.fixture(scope="function")
def redis_connection(request) -> Generator[redis.Redis, None, None]:
    """Conexão Redis com configuração baseada no tipo de teste"""
    is_stress = request.node.get_closest_marker("stress") is not None
    
    if is_stress:
        config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': 0,
            'socket_timeout': 30,
            'socket_connect_timeout': 30,
            'retry_on_timeout': True,
            'max_connections': 100,
            'health_check_interval': 30
        }
    else:
        config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': 1,
            'socket_timeout': 5,
            'decode_responses': True,
            'health_check_interval': 5
        }
    
    client = None
    try:
        client = redis.Redis(**config)
        # Validação da conexão
        client.ping()
        yield client
    except redis.ConnectionError as e:
        pytest.skip(f"Redis não disponível: {str(e)}")
    finally:
        if client:
            client.close()

@pytest.fixture(autouse=True)
def check_test_context(request):
    """Validação do contexto de teste"""
    if "redis_connection" in request.fixturenames:
        conn = request.getfixturevalue("redis_connection")
        if request.node.get_closest_marker("stress"):
            assert conn.connection_pool.connection_kwargs.get("max_connections") >= 100, \
                "Configuração de stress não aplicada corretamente"

@pytest.fixture(scope="function")
def metrics_registry():
    """Registry isolado para métricas de teste"""
    return CollectorRegistry()

@pytest.fixture(autouse=True)
def timeout_setup(request):
    """Configura timeouts dinâmicos baseados no tipo de teste"""
    timeouts = {
        "unit": 3,
        "integration": 30,
        "system": 120,
        "stress": 300
    }
    
    for marker_name, timeout in timeouts.items():
        if request.node.get_closest_marker(marker_name):
            request.node.add_marker(pytest.mark.timeout(timeout))
            break

@pytest.fixture(autouse=True)
def setup_test_env(request):
    """Configura ambiente baseado no tipo de teste"""
    is_stress = request.node.get_closest_marker("stress") is not None
    
    if is_stress:
        config = {
            "CELERY_WORKER_POOL": "prefork",
            "CELERY_MAX_TASKS_PER_CHILD": "100",
            "CELERY_WORKER_CONCURRENCY": "4",
            "CELERY_TASK_TIME_LIMIT": "300"
        }
    else:
        config = {
            "CELERY_WORKER_POOL": "solo",
            "CELERY_MAX_TASKS_PER_CHILD": "10",
            "CELERY_WORKER_CONCURRENCY": "1",
            "CELERY_TASK_TIME_LIMIT": "30"
        }
    
    # Backup e atualização do ambiente
    old_env = {k: os.environ.get(k) for k in config}
    os.environ.update(config)
    
    yield
    
    # Restauração do ambiente
    for k, v in old_env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v