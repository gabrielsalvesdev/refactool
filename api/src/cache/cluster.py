from redis import Redis, RedisError, ConnectionPool
import os
import logging
import redis
from typing import Optional, Any

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
        except RedisError as e:
            logging.warning(f"Erro ao fechar conexão Redis: {str(e)}") 

class RedisCluster:
    def __init__(self, host: str = None, port: int = None, db: int = 0):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.db = db
        self._client = None
        self.logger = logging.getLogger(__name__)

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True
            )
        return self._client

    def get(self, key: str) -> Optional[Any]:
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            self.logger.error(f"Erro ao obter chave {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            return self.client.set(key, value, ex=ttl)
        except redis.RedisError as e:
            self.logger.error(f"Erro ao definir chave {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            self.logger.error(f"Erro ao deletar chave {key}: {str(e)}")
            return False

    def flushall(self) -> bool:
        try:
            return bool(self.client.flushall())
        except redis.RedisError as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")
            return False

    def client_kill_filter(self, _all: bool = False) -> bool:
        try:
            return bool(self.client.client_kill_filter(_all=_all))
        except redis.RedisError as e:
            self.logger.error(f"Erro ao matar conexões: {str(e)}")
            return False

    def close(self) -> None:
        if self._client:
            try:
                self._client.close()
            except redis.RedisError as e:
                self.logger.error(f"Erro ao fechar conexão: {str(e)}")
            finally:
                self._client = None 