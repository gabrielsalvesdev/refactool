from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Dict, Optional, Callable
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil não instalado. Métricas de sistema desativadas.")

# Métricas de sistema
system_memory_usage = Gauge(
    'system_memory_usage_percent',
    'Uso de memória do sistema em porcentagem'
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'Uso de CPU do sistema em porcentagem'
)

# Métricas de task
task_duration = Histogram(
    'task_duration_seconds',
    'Duração das tasks em segundos',
    buckets=[30, 60, 120, 180, 240, 300]
)

task_memory = Gauge(
    'task_memory_bytes',
    'Uso de memória por task'
)

# Métricas de cache
cache_hits = Counter(
    'cache_hits_total',
    'Total de hits no cache'
)

cache_misses = Counter(
    'cache_misses_total',
    'Total de misses no cache'
)

def update_system_metrics():
    """
    Atualiza métricas do sistema.
    """
    if not PSUTIL_AVAILABLE:
        return
        
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        system_cpu_usage.set(cpu)
        system_memory_usage.set(memory.percent)
    except Exception as e:
        logger.error(f"Erro ao atualizar métricas do sistema: {str(e)}")

def record_task_completion(status: str = 'success') -> None:
    """
    Registra conclusão de task.
    """
    try:
        if status == 'success':
            task_duration.observe(0)  # Placeholder para compatibilidade
    except Exception as e:
        logger.error(f"Erro ao registrar conclusão de task: {str(e)}")

def record_cache_hit() -> None:
    """
    Registra hit no cache.
    """
    try:
        cache_hits.inc()
    except Exception as e:
        logger.error(f"Erro ao registrar cache hit: {str(e)}")

def record_cache_miss() -> None:
    """
    Registra miss no cache.
    """
    try:
        cache_misses.inc()
    except Exception as e:
        logger.error(f"Erro ao registrar cache miss: {str(e)}")

@contextmanager
def MetricsTimer():
    """
    Context manager para medir duração de operações.
    """
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        task_duration.observe(duration)

# Métricas de execução de tasks
task_timeouts = Counter(
    'task_timeouts_total',
    'Número total de timeouts'
)

task_retries = Counter(
    'task_retries_total',
    'Número total de retentativas'
)

# Métricas de tarefas
tasks_completed = Counter(
    'refactool_tasks_completed_total',
    'Total de tarefas completadas',
    ['status']
)

tasks_duration = Histogram(
    'refactool_task_duration_seconds',
    'Duração das tarefas em segundos',
    ['task_type']
)

active_tasks = Gauge(
    'refactool_active_tasks',
    'Número de tarefas ativas'
)

# Métricas de cache
cache_memory = Gauge(
    'cache_memory_bytes',
    'Uso de memória do cache',
    ['cache_type']
)

# Métricas de sistema
system_memory = Gauge(
    'refactool_system_memory_bytes',
    'Uso de memória do sistema'
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'Uso de CPU',
    ['core']
)

# Métricas de sistema
system_cpu = Gauge(
    'refactool_system_cpu_percent',
    'Uso de CPU do sistema'
)

# Métricas de cache
cache_size = Gauge(
    'refactool_cache_size_bytes',
    'Tamanho atual do cache em bytes'
)

def monitor_task(func: Callable) -> Callable:
    """
    Decorator para monitorar execução de tasks
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with MetricsTimer() as timer:
            start_time = time.time()
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                task_duration.observe(duration)
                
                # Atualiza métricas de memória
                final_memory = process.memory_info().rss
                memory_used = final_memory - initial_memory
                task_memory.set(memory_used)
                
                return result
                
            except TimeoutError:
                task_timeouts.inc()
                raise
            finally:
                # Atualiza métricas do sistema
                memory = psutil.virtual_memory()
                system_memory.set(process.memory_info().rss)
                system_cpu.set(psutil.cpu_percent())
                
                for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                    cpu_usage.labels(f'core_{i}').set(percentage)
    
    return wrapper

def update_cache_metrics(cache_type: str, hit: bool = True) -> None:
    """
    Atualiza métricas de cache
    """
    if hit:
        cache_hits.inc()
    else:
        cache_misses.inc()

def update_cache_memory(cache_type: str, bytes_used: int) -> None:
    """
    Atualiza métricas de memória do cache
    """
    cache_memory.labels(cache_type).set(bytes_used)

def log_retry(task_id: Optional[str] = None) -> None:
    """
    Registra uma tentativa de retry
    """
    task_retries.inc()

def get_metrics() -> Dict[str, float]:
    """
    Retorna um dicionário com as métricas atuais do sistema.
    """
    try:
        success_count = tasks_completed._value.get({'status': 'success'}, 0)
        error_count = tasks_completed._value.get({'status': 'error'}, 0)
        
        return {
            "tasks_completed": success_count,
            "tasks_failed": error_count,
            "cache_hits": cache_hits._value.get({}, 0),
            "cache_misses": cache_misses._value.get({}, 0),
            "active_tasks": active_tasks._value.get({}, 0),
            "cache_size": cache_size._value.get({}, 0),
            "system_memory": system_memory._value.get({}, 0),
            "system_cpu": system_cpu._value.get({}, 0)
        }
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {str(e)}")
        return {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "active_tasks": 0,
            "cache_size": 0,
            "system_memory": 0,
            "system_cpu": 0
        }

def record_task_duration(duration: float, task_type: str = 'analysis') -> None:
    """
    Registra a duração de uma tarefa.
    """
    try:
        tasks_duration.labels(task_type=task_type).observe(duration)
    except Exception as e:
        logger.error(f"Erro ao registrar duração de tarefa: {str(e)}")

def update_cache_size(size_bytes: int) -> None:
    """
    Atualiza o tamanho do cache.
    """
    try:
        cache_size.set(size_bytes)
    except Exception as e:
        logger.error(f"Erro ao atualizar tamanho do cache: {str(e)}")

class MetricsCollector:
    def __init__(self):
        self._prom_metrics = {}
        
    def collect_cpu_usage(self):
        if PSUTIL_AVAILABLE:
            return psutil.cpu_percent(interval=1)
        return 0  # Fallback quando psutil não está disponível
        
    def collect_memory_usage(self):
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().percent
        return 0  # Fallback quando psutil não está disponível

    def collect_system_metrics(self):
        if not PSUTIL_AVAILABLE:
            logging.info("Métricas de sistema desativadas - psutil não disponível")
            return {}
            
        return {
            'cpu_percent': self.collect_cpu_usage(),
            'memory_percent': self.collect_memory_usage()
        } 