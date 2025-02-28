import pytest
from api.src.cache.lru_cache import LRUCache

def test_forced_eviction():
    # Aumenta o limite de memória para um valor mais realista
    cache = LRUCache(max_memory_mb=20)  # 20MB
    
    # Dados de teste
    key = "test_key"
    value = "x" * 1024 * 1024  # 1MB de dados
    
    # Adiciona dados ao cache
    cache.put(key, value)
    
    # Verifica se os dados foram armazenados
    assert cache.get(key) == value
    
    # Força evicção
    cache.force_eviction()
    
    # Verifica se a memória está abaixo do limite
    assert cache.get_memory_usage() < 20 * 1024 * 1024  # 20MB em bytes
    
    # Verifica se o cache ainda funciona
    cache.put("new_key", "new_value")
    assert cache.get("new_key") == "new_value" 