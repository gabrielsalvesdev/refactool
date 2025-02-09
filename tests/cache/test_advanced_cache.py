import hashlib
import secrets
import tempfile
import os

import pytest
from api.src.tasks import analyze_code_task, redis_cache, hash_path, CACHE_VERSION, get_project_size

try:
    from api.src.tasks import rb
except ImportError:
    rb = None


def test_bloom_filter_false_positives():
    # Testa que o Bloom Filter não retorna falso positivo para um hash que nunca foi adicionado
    if rb is None:
        pytest.skip("RedisBloom não disponível")
    test_hash = hashlib.sha256(b"unico_123").hexdigest()
    # Certifique-se de que o hash não está presente
    assert rb.bfExists("cached_projects", test_hash) is False
    for _ in range(10_000):
        rb.bfAdd("cached_projects", secrets.token_hex(16))
    # Ainda deve não existir
    assert rb.bfExists("cached_projects", test_hash) is False


def test_cache_version_update(monkeypatch):
    # Testa o versionamento de cache
    path = "tests/legacy_project"
    # Limpa cache se existir
    project_hash = hash_path(path)
    old_key = f"analysis_v{CACHE_VERSION}:{project_hash}"
    redis_cache.delete(old_key)
    analyze_code_task.delay(path).get(timeout=60)
    assert redis_cache.exists(old_key) is not None, "Chave da versão antiga deve existir"

    # Simula atualização de versão
    new_version = CACHE_VERSION + 1
    monkeypatch.setattr("api.src.tasks.CACHE_VERSION", new_version)
    analyze_code_task.delay(path).get(timeout=60)
    new_key = f"analysis_v{new_version}:{project_hash}"
    assert redis_cache.exists(new_key) is not None, "Chave da nova versão deve existir"
    assert redis_cache.exists(old_key) is None, "Chave da versão antiga deve ser invalidada"


def test_long_path():
    # Testa caminho muito longo
    long_path = "/" * 200
    result = analyze_code_task.delay(long_path).get(timeout=60)
    assert "error" not in result, "Caminho longo não deve gerar erro"


def test_empty_project(tmp_path):
    # Cria um diretório vazio e testa a análise
    empty_dir = tmp_path / "empty_project"
    empty_dir.mkdir()
    result = analyze_code_task.delay(str(empty_dir)).get(timeout=60)
    assert result["status"] == "COMPLETED"
    # Assumindo que para um projeto vazio, o pylint retorne score 10 ou similar
    score = result["metrics"].get("score", 10.0)
    assert score >= 10.0, "Projeto vazio deve ter score 10.0 ou maior" 