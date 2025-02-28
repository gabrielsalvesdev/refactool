import os
from redis import Redis

# Configurar o cliente Redis para o cluster LRU
cluster = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,  # Use database 0 (pode ser ajustado conforme necessário)
    decode_responses=True
) 