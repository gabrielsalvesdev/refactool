from redis import Redis, RedisError, ConnectionPool
import os
import logging

# Configuração do pool de conexões Redis
REDIS_POOL = ConnectionPool(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
    max_connections=50,
    socket_timeout=30,
    socket_connect_timeout=30,
    retry_on_timeout=True
)

def get_slot_distribution():
    """
    Retorna informações sobre a distribuição de slots no cluster Redis
    com melhor tratamento de erros e timeouts
    """
    redis = Redis(connection_pool=REDIS_POOL)
    
    try:
        # Tenta obter informações do cluster com timeout
        info = redis.cluster("info")
        
        # Verifica se o cluster está realmente habilitado
        if info and info.get('cluster_enabled', '0') == '1':
            slots = int(info.get('cluster_slots', 16384))
            nodes = int(info.get('cluster_known_nodes', 3))
            return {
                'total_slots': slots,
                'nodes': nodes,
                'slots_per_node': slots / nodes if nodes > 0 else slots
            }
        else:
            # Modo standalone
            return {
                'total_slots': 16384,
                'nodes': 1,
                'slots_per_node': 16384
            }
            
    except RedisError as e:
        # Log do erro específico
        logging.error(f"Erro ao acessar Redis cluster: {str(e)}")
        # Fallback para modo standalone
        return {
            'total_slots': 16384,
            'nodes': 1,
            'slots_per_node': 16384
        }
    finally:
        try:
            redis.close()
        except:
            pass 