from redis import Redis, RedisError
import os

def get_slot_distribution():
    """
    Retorna informações sobre a distribuição de slots no cluster Redis
    """
    redis = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )
    
    try:
        # Tenta obter informações do cluster
        info = redis.cluster("info")
        
        # Verifica se o cluster está realmente habilitado
        if info.get('cluster_enabled', '0') == '1':
            slots = int(info.get('cluster_slots', 16384))
            nodes = int(info.get('cluster_known_nodes', 3))  # Padrão para 3 nodes em cluster
            return {
                'total_slots': slots,
                'nodes': nodes,
                'slots_per_node': slots / nodes
            }
        else:
            # Modo standalone
            return {
                'total_slots': 16384,
                'nodes': 1,
                'slots_per_node': 16384
            }
            
    except RedisError:
        # Fallback para modo standalone em caso de erro
        return {
            'total_slots': 16384,
            'nodes': 1,
            'slots_per_node': 16384
        }
    finally:
        redis.close() 