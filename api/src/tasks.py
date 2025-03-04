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
from typing import Dict, Optional, Any
from api.src.analyzers.code_analyzer import CodeAnalyzer
from api.src.cache.lru_cache import LRUCache
from api.src.monitoring.metrics import (
    monitor_task, 
    update_cache_metrics, 
    update_cache_memory,
    log_retry,
    tasks_completed,
    active_tasks,
    cache_hits,
    cache_misses,
    update_system_metrics,
    record_task_completion,
    record_cache_hit,
    record_cache_miss,
    record_task_duration,
    MetricsTimer
)
from celery import chain, group
import sys

# Configuração do cache LRU global
lru_cache = LRUCache(max_memory_mb=100, version=2)

# Atualização: Usar variáveis de ambiente para configuração do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Atualização: Usar DB 1 para cache com retry e timeout
redis_cache = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=1,
    decode_responses=True,  # Decodifica automaticamente
    retry_on_timeout=True,
    socket_connect_timeout=10,
    socket_timeout=10
)

# Importar métricas de cache
from api.src.monitoring.celery_metrics import cache_hits, cache_misses

# Função para calcular o tamanho do projeto
def get_project_size(path: str) -> int:
    """
    Calcula o tamanho total do projeto em bytes.
    """
    try:
        return sum(f.stat().st_size for f in Path(path).rglob('*.*'))
    except Exception as e:
        logger.warning(f"Erro ao calcular tamanho do projeto: {str(e)}")
        return 0

# Configuração do Celery usando variáveis de ambiente
celery = Celery(
    __name__,
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
)

# Configurações otimizadas para melhor performance
celery.conf.update(
    task_time_limit=300,  # 5 minutos
    task_soft_time_limit=240,  # 4 minutos
    worker_prefetch_multiplier=4,  # Ajustado para melhor throughput
    worker_max_tasks_per_child=100,  # Aumentado para reduzir overhead
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    redis_socket_connect_timeout=30,
    redis_socket_timeout=30,
    broker_transport_options={
        'visibility_timeout': 3600,
        'socket_timeout': 30,
        'socket_connect_timeout': 30
    },
    broker_connection_retry_on_startup=True
)

def should_partition_task(path: str) -> bool:
    """
    Determina se uma task deve ser particionada baseado no tamanho do projeto
    """
    try:
        size = get_project_size(path)
        return size > 5_000_000  # 5MB
    except (OSError, IOError) as e:
        logger.warning(f"Erro ao calcular tamanho do projeto: {str(e)}")
        return False

@celery.task(name="analyze_directory")
def analyze_directory(path: str) -> Dict:
    """
    Analisa um diretório específico do projeto.
    """
    try:
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_project(path)
        return {
            "status": "COMPLETED",
            "result": result,
            "path": path
        }
    except Exception as e:
        logger.error(f"Erro ao analisar diretório: {str(e)}")
        return {
            "status": "ERROR",
            "error": str(e),
            "path": path
        }

@celery.task(name="merge_results")
def merge_results(results: list) -> Dict:
    """
    Combina resultados de múltiplas análises
    """
    merged = {
        "status": "SUCCESS",
        "result": {},
        "errors": []
    }
    
    for r in results:
        if r["status"] == "SUCCESS":
            merged["result"].update(r["result"])
        else:
            merged["errors"].append(r)
    
    return merged

@celery.task(
    bind=True,
    name="analyze_code_task",
    autoretry_for=(subprocess.TimeoutExpired, ConnectionError),
    max_retries=3,
    default_retry_delay=5
)
def analyze_code_task(self, path: str) -> Dict[str, Any]:
    """
    Analisa o código no caminho especificado.
    """
    # Validações
    if not path:
        error_msg = "Caminho não pode ser vazio"
        logger.error(error_msg)
        return {"status": "ERROR", "message": error_msg}
        
    if not os.path.exists(path):
        error_msg = f"Caminho não existe: {path}"
        logger.error(error_msg)
        return {"status": "ERROR", "message": error_msg}

    try:
        # Verifica cache
        cache_key = f"analysis:{path}"
        cached_result = redis_cache.get(cache_key)
        
        if cached_result:
            record_cache_hit()
            return {"status": "COMPLETED", "result": cached_result}
            
        record_cache_miss()
        
        # Executa análise
        with MetricsTimer():
            # TODO: Implementar análise real
            result = {"status": "COMPLETED", "message": "Análise concluída"}
            
        # Armazena no cache
        redis_cache.setex(
            cache_key,
            3600,  # 1 hora
            str(result)
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Erro ao analisar código: {str(e)}"
        logger.error(error_msg)
        return {"status": "ERROR", "message": error_msg}

# -------------------- Estratégias Avançadas de Cache e Otimização --------------------

CACHE_VERSION = 2

def hash_path(path: str) -> str:
    """
    Gera um hash único para o caminho.
    """
    if not path:
        return ""
    return hashlib.sha256(path.encode()).hexdigest()

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
except Exception:
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
        
        # Verifica cache LRU primeiro
        cached_result = lru_cache.get(project_hash)
        if cached_result:
            logger.info("Cache LRU hit", project_path=project_path)
            cache_hits.add(1)
            return json.loads(cached_result)
        
        # Verifica cache Redis
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            logger.info("Cache Redis hit", project_path=project_path, cache_key=cache_key)
            # Atualiza o cache LRU
            lru_cache.put(project_hash, cached_result)
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
        
        # Serializa resultado
        result_json = json.dumps(result_data)
        
        # Calcula TTL baseado no tamanho do projeto
        project_size = get_project_size(project_path)
        ttl = 3600 if project_size < 1_000_000 else 600
        
        # Salva no Redis
        redis_cache.setex(cache_key, ttl, result_json.encode('utf-8'))
        
        # Salva no LRU
        lru_cache.put(project_hash, result_json)
        
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