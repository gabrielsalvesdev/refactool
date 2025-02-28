import os
import multiprocessing

# Configurações de broker e backend
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

# Configurações de timeout e retry
task_time_limit = 300  # 5 minutos
task_soft_time_limit = 240  # 4 minutos
task_default_retry_delay = 5
task_max_retries = 3

# Configurações de worker
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 100
worker_concurrency = multiprocessing.cpu_count()

# Configurações de task
task_acks_late = True
task_reject_on_worker_lost = True
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

# Configurações de rate limiting
task_annotations = {
    'analyze_code_task': {
        'rate_limit': '10/m'
    },
    'analyze_directory': {
        'rate_limit': '20/m'
    }
}

# Configurações de monitoramento
worker_send_task_events = True
task_send_sent_event = True

# Configurações de logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s'

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