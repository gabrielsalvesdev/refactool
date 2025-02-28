from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Optional, Callable
import psutil
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    import logging
    logging.warning("psutil não instalado. Métricas de sistema desativadas.")

# Métricas de execução de tasks
task_duration = Histogram(
    'task_analysis_duration_seconds',
    'Tempo de execução das tasks de análise',
    buckets=[30, 60, 120, 180, 240, 300, 360]
)

task_memory_usage = Gauge(
    'task_memory_usage_bytes',
    'Uso de memória por task'
)

task_timeouts = Counter(
    'task_timeouts_total',
    'Número total de timeouts'
)

task_retries = Counter(
    'task_retries_total',
    'Número total de retentativas'
)

# Métricas de cache
cache_hits = Counter(
    'cache_hits_total',
    'Número total de hits no cache',
    ['cache_type']  # LRU ou Redis
)

cache_misses = Counter(
    'cache_misses_total',
    'Número total de misses no cache',
    ['cache_type']
)

cache_memory = Gauge(
    'cache_memory_bytes',
    'Uso de memória do cache',
    ['cache_type']
)

# Métricas de sistema
system_memory = Gauge(
    'system_memory_bytes',
    'Uso de memória do sistema',
    ['type']  # total, used, free
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'Uso de CPU',
    ['core']
)

def monitor_task(func: Callable) -> Callable:
    """
    Decorator para monitorar execução de tasks
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
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
            task_memory_usage.set(memory_used)
            
            return result
            
        except TimeoutError:
            task_timeouts.inc()
            raise
        finally:
            # Atualiza métricas do sistema
            memory = psutil.virtual_memory()
            system_memory.labels('total').set(memory.total)
            system_memory.labels('used').set(memory.used)
            system_memory.labels('free').set(memory.free)
            
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                cpu_usage.labels(f'core_{i}').set(percentage)
    
    return wrapper

def update_cache_metrics(cache_type: str, hit: bool = True) -> None:
    """
    Atualiza métricas de cache
    """
    if hit:
        cache_hits.labels(cache_type).inc()
    else:
        cache_misses.labels(cache_type).inc()

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