import os

# Broker settings
broker_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
result_backend = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/1"

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
timezone = 'UTC'

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 50
worker_max_memory_per_child = 150_000
worker_concurrency = 4

# Queue settings
task_queues = {
    'analysis': {
        'exchange': 'analysis',
        'routing_key': 'analysis',
    },
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    }
}

task_routes = {
    'analyze_code_task': {'queue': 'analysis'},
    'analyze_directory': {'queue': 'analysis'},
    'merge_results': {'queue': 'default'}
}

# Task execution settings
task_time_limit = 300
task_soft_time_limit = 240
task_acks_late = True
task_reject_on_worker_lost = True

# Redis settings
broker_transport_options = {
    'visibility_timeout': 3600,
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'max_retries': 3,
    'retry_on_timeout': True
}

# Result settings
result_expires = 3600
result_cache_max = 10000

# Monitoring settings
worker_send_task_events = True
task_send_sent_event = True
task_track_started = True
task_track_received = True
worker_state_db = 'worker_state.db'

# Rate limiting
task_annotations = {
    'analyze_code_task': {
        'rate_limit': '100/m',
        'max_retries': 3,
        'default_retry_delay': 5
    }
} 