#!/bin/bash

# Inicia Redis com a nova configuração
redis-server tests/redis.conf &

# Aguarda Redis iniciar
sleep 2

# Inicia workers Celery para diferentes filas
celery -A api.src.tasks worker -Q analysis -c 4 --loglevel=INFO &
celery -A api.src.tasks worker -Q default -c 2 --loglevel=INFO &

# Inicia Flower para monitoramento
celery -A api.src.tasks flower &

echo "Serviços iniciados com sucesso!" 