from celery import Celery
from celery.signals import worker_ready
import os

# Configurações do broker Redis
broker_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
result_backend = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/1"

app = Celery('microservices',
             broker=broker_url,
             backend=result_backend,
             include=['api.src.tasks'])  # Importa as tasks

# Configurações para melhorar a estabilidade
app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_connection_timeout=30,
    result_expires=3600,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    redis_socket_connect_timeout=30,
    redis_socket_timeout=30,
    redis_retry_on_timeout=True,
    imports=['api.src.tasks']  # Garante que as tasks sejam importadas
)

@worker_ready.connect
def at_start(sender, **kwargs):
    print("Celery worker está pronto!") 