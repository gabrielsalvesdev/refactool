import time
from src.cache.cluster import cluster


def track_access(key):
    timestamp = time.time()
    # Usa sorted set com score como timestamp
    cluster.zadd("lru_access", {key: timestamp})


def evict_oldest(max_memory):
    # Obtém uso atual da memória
    current_mem = int(cluster.info("memory")["used_memory"])
    if current_mem < max_memory:
        return

    # Calcula quantos keys serão removidos (10% dos acessos)
    total_keys = cluster.zcard("lru_access")
    num_to_remove = int(0.1 * total_keys)
    if num_to_remove < 1:
        num_to_remove = 1

    oldest_keys = cluster.zrange("lru_access", 0, num_to_remove - 1)
    if oldest_keys:
        cluster.delete(*oldest_keys)
        cluster.zrem("lru_access", *oldest_keys) 