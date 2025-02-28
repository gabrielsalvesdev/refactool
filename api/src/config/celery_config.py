import os
import multiprocessing
from celery.signals import worker_ready
from prometheus_client import Counter, Gauge

# Configurações base
broker_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0"
result_backend = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1"

# Configurações de Pool
worker_pool = os.getenv("CELERY_WORKER_POOL", "solo")
worker_concurrency = int(os.getenv("CELERY_WORKER_CONCURRENCY", "1"))
worker_max_tasks_per_child = int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "10"))

# Timeouts e Retries
task_acks_late = True
task_reject_on_worker_lost = True
task_time_limit = 300  # 5 minutos
task_soft_time_limit = 240  # 4 minutos

# Configurações de Retry
task_default_retry_delay = 5  # 5 segundos
task_max_retries = 3

# Configurações de Queue
task_default_queue = "default"
task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    },
    "high_priority": {
        "exchange": "high_priority",
        "routing_key": "high_priority",
    },
    "stress_tests": {
        "exchange": "stress_tests",
        "routing_key": "stress_tests",
    }
}

# Métricas
worker_tasks_active = Gauge(
    "celery_worker_tasks_active",
    "Number of tasks currently being executed",
    ["worker_name"]
)

worker_tasks_completed = Counter(
    "celery_worker_tasks_completed",
    "Number of tasks completed by the worker",
    ["worker_name", "status"]
)

@worker_ready.connect
def setup_worker_metrics(sender, **kwargs):
    """Configura métricas quando o worker inicia"""
    worker_tasks_active.labels(sender.hostname).set(0)

# Configurações de Logging
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s"

# Configurações de Rate Limiting
task_annotations = {
    "tasks.analyze_code_task": {
        "rate_limit": "10/m"  # 10 execuções por minuto
    }
}

# Configurações específicas para testes de stress
if os.getenv("TEST_TYPE") == "stress":
    worker_concurrency = 4
    worker_max_tasks_per_child = 100
    task_time_limit = 600  # 10 minutos
    task_soft_time_limit = 540  # 9 minutos
    task_default_retry_delay = 10
    task_annotations = {
        "tasks.analyze_code_task": {
            "rate_limit": "30/m"  # 30 execuções por minuto em testes de stress
        }
    }

# Configurações de worker
worker_prefetch_multiplier = 4
worker_concurrency = multiprocessing.cpu_count()

# Configurações de task
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Configurações de Redis
redis_socket_connect_timeout = 30
redis_socket_timeout = 30
broker_transport_options = {
    'visibility_timeout': 3600,
    'socket_timeout': 30,
    'socket_connect_timeout': 30
}

# Configurações de roteamento
task_routes = {
    'analyze_code_task': {'queue': 'analysis'},
    'analyze_directory': {'queue': 'analysis'},
    'merge_results': {'queue': 'merge'}
}

# Configurações de monitoramento
worker_send_task_events = True
task_send_sent_event = True

# Configurações de pool
worker_pool_restarts = True

# Configurações de memória
worker_max_memory_per_child = 150_000  # 150MB

# Configurações de heartbeat
broker_heartbeat = 10

# Configurações de retry
broker_connection_retry = True
broker_connection_max_retries = 0  # Infinito

# Configurações de resultado
result_expires = 3600  # 1 hora
result_cache_max = 10_000

# Configurações de prioridade
task_queue_max_priority = 10
task_default_priority = 5

# Configurações de timeout de resultado
result_chord_join_timeout = 3600
result_chord_retry_interval = 5 