from redis import Redis
import os

def get_slot_distribution():
    """
    Retorna informações sobre a distribuição de slots no cluster Redis
    """
    redis = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0
    )
    
    try:
        info = redis.cluster("info")
        return {
            'total_slots': info.get('cluster_slots', 16384),
            'nodes': info.get('cluster_known_nodes', 1),
            'slots_per_node': info.get('cluster_slots', 16384) / max(info.get('cluster_known_nodes', 1), 1)
        }
    except Exception:
        # Fallback para não-cluster
        return {
            'total_slots': 16384,
            'nodes': 1,
            'slots_per_node': 16384
        }
    finally:
        redis.close() 