"""Configurações globais para testes."""
import pytest
from redis import Redis
import os

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
def redis_connection():
    """Fixture para conexão com Redis."""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    redis = Redis(
        host=redis_host,
        port=redis_port,
        db=1,  # Usar DB 1 para testes
        decode_responses=False,
        retry_on_timeout=True,
        socket_connect_timeout=1,
        socket_timeout=1
    )
    
    try:
        # Testa a conexão
        redis.ping()
    except:
        pytest.skip("Redis não está disponível")
    
    # Limpa o banco antes dos testes
    redis.flushdb()
    
    yield redis
    
    # Limpa o banco após os testes
    redis.flushdb()
    redis.close()