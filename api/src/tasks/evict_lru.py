from celery import shared_task

# Define o limite máximo de memória em bytes (exemplo: 1GB)
MAX_MEMORY = 1_000_000_000

@shared_task(name="tasks.evict_lru")
def evict_lru():
    from src.cache.lru_tracker import evict_oldest
    evict_oldest(MAX_MEMORY) 