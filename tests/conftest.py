"""Configurações globais para testes."""
import pytest
from redis import Redis
import os

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Configura variáveis de ambiente para testes."""
    os.environ["REDIS_HOST"] = "redis"
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
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    redis = Redis(
        host=redis_host,
        port=redis_port,
        db=1,  # Usar DB 1 para testes
        decode_responses=False,
        retry_on_timeout=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    
    try:
        # Testa a conexão com retry
        for _ in range(3):  # Tenta 3 vezes
            try:
                redis.ping()
                break
            except:
                import time
                time.sleep(1)  # Espera 1 segundo entre tentativas
        else:
            pytest.skip("Redis não está disponível após 3 tentativas")
    except Exception as e:
        pytest.skip(f"Redis não está disponível: {str(e)}")
    
    # Limpa o banco antes dos testes
    redis.flushdb()
    
    yield redis
    
    # Limpa o banco após os testes
    redis.flushdb()
    redis.close()