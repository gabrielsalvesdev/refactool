# api/src/tasks.py
import subprocess
from pathlib import Path
from celery import Celery
from api.src.utils.code_analysis import parse_pylint_output
from api.src.logging import logger
import traceback
import hashlib
import json
import os
from redis import Redis

# Atualização: Usar DB 1 para cache
redis_cache = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=1,
    decode_responses=False,  # Armazena como bytes
    retry_on_timeout=True
)

# Importar métricas de cache
from api.src.monitoring.celery_metrics import cache_hits, cache_misses

# Função para calcular o tamanho do projeto
def get_project_size(path):
    return sum(f.stat().st_size for f in Path(path).rglob('*.*'))

celery = Celery(__name__, broker="redis://redis:6379/0", backend="redis://redis:6379/0")

@celery.task(bind=True, name="analyze_code_task", autoretry_for=(subprocess.TimeoutExpired,), max_retries=3)
def analyze_code_task(self, project_path: str):
    try:
        # Geração do hash único do projeto e definição da chave de cache
        project_hash = hashlib.sha256(project_path.encode()).hexdigest()
        cache_key = f"analysis:{project_hash}"

        # Verifica se o resultado já está em cache
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            logger.info("Cache hit", project_path=project_path, cache_key=cache_key)
            cache_hits.add(1)
            result_data = json.loads(cached_result.decode('utf-8'))
            result_data["cached"] = True
            return result_data

        if not Path(project_path).is_dir():
            raise ValueError("Diretório inválido")
        result = subprocess.run(
            ["pylint", "--output-format=json", project_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )
        analysis_data = parse_pylint_output(result.stdout)
        result_data = {
            "status": "COMPLETED",
            "metrics": analysis_data,
            "cached": False
        }

        # Incrementa cache miss
        cache_misses.add(1)

        # Calcula TTL dinâmico com base no tamanho do projeto
        project_size = get_project_size(project_path)
        ttl = 3600 if project_size < 1_000_000 else 600

        # Armazena o resultado no cache com TTL dinâmico
        redis_cache.setex(cache_key, ttl, json.dumps(result_data).encode('utf-8'))
        return result_data
    except Exception:
        logger.error("Erro ao processar tarefa")
        return {"status": "FAILED", "error": "Erro ao processar tarefa", "trace": traceback.format_exc()}

# -------------------- Estratégias Avançadas de Cache e Otimização --------------------

CACHE_VERSION = 2

def hash_path(project_path):
    return hashlib.sha256(project_path.encode()).hexdigest()

def get_cache_key(project_path, project_id=None):
    if project_id:
        return f"analysis_v{CACHE_VERSION}:{project_id}:{hash_path(project_path)}"
    else:
        return f"analysis_v{CACHE_VERSION}:{hash_path(project_path)}"


def atualizar_banco(novos_dados):
    # Stub: implementar atualização no banco de dados
    pass


def atualizar_analise(project_path, novos_dados, project_id=None):
    atualizar_banco(novos_dados)
    key = get_cache_key(project_path, project_id)
    redis_cache.setex(key, 3600, json.dumps(novos_dados).encode('utf-8'))
    return novos_dados


def invalidar_projeto(project_id):
    # Invalidação por namespace: busca chaves que contêm o project_id
    keys = redis_cache.keys(f"analysis_v{CACHE_VERSION}:*:{project_id}")
    if keys:
        redis_cache.delete(*keys)
    return keys

# Integração do RedisBloom para otimização de cache
try:
    from redisbloom.client import Client
    rb = Client()
except Exception as e:
    rb = None
    logger.warning("RedisBloom não disponível")

@celery.task(bind=True, name="analyze_code_task_with_bloom", autoretry_for=(subprocess.TimeoutExpired,), max_retries=3)
def analyze_code_task_with_bloom(self, project_path: str):
    try:
        project_hash = hashlib.sha256(project_path.encode()).hexdigest()
        cache_key = get_cache_key(project_path)  # Usa chave com versionamento
        
        # Uso do Bloom Filter para controle adicional
        if rb is not None:
            try:
                if rb.bfExists("cached_projects", project_hash):
                    logger.info("Bloom filter: chave existente", project_hash=project_hash)
                else:
                    rb.bfAdd("cached_projects", project_hash)
                    logger.info("Bloom filter: adicionando chave", project_hash=project_hash)
            except Exception as ex:
                logger.warning("Falha no uso do RedisBloom", exc_info=ex)
        
        # Verifica cache
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            logger.info("Cache hit", project_path=project_path, cache_key=cache_key)
            cache_hits.add(1)
            result_data = json.loads(cached_result.decode('utf-8'))
            result_data["cached"] = True
            return result_data
        
        if not Path(project_path).is_dir():
            raise ValueError("Diretório inválido")
        result = subprocess.run(
            ["pylint", "--output-format=json", project_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        analysis_data = parse_pylint_output(result.stdout)
        result_data = {
            "status": "COMPLETED",
            "metrics": analysis_data,
            "cached": False
        }
        
        cache_misses.add(1)
        
        project_size = get_project_size(project_path)
        ttl = 3600 if project_size < 1_000_000 else 600
        
        redis_cache.setex(cache_key, ttl, json.dumps(result_data).encode('utf-8'))
        return result_data
    except Exception:
        logger.error("Erro ao processar tarefa")
        return {"status": "FAILED", "error": "Erro ao processar tarefa", "trace": traceback.format_exc()}

# Tarefa de pré-aquecimento dos caches (Cache Warmup) via Celery Beat
celery.conf.beat_schedule = {
    'precache-popular-projects': {
        'task': 'precache_projects',
        'schedule': 3600.0,  # Executa a cada hora
    },
}

@celery.task(name='precache_projects')
def precache_projects():
    popular_projects = get_projects_mais_acessados()
    for p in popular_projects:
        analyze_code_task.delay(p['path'])


def get_projects_mais_acessados():
    # Stub: retorna uma lista de projetos populares
    return [{'path': 'tests/sample_project'}]

# -------------------- Fim das Estratégias Avançadas -------------------- 