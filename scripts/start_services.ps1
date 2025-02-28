# Inicia Redis com a nova configuração
Start-Process redis-server -ArgumentList "tests/redis.conf" -NoNewWindow

# Aguarda Redis iniciar
Start-Sleep -Seconds 2

# Inicia workers Celery para diferentes filas
$env:PYTHONPATH = "."
Start-Process powershell -ArgumentList "-NoProfile -Command celery -A api.src.tasks worker -Q analysis -c 4 --loglevel=INFO" -NoNewWindow
Start-Process powershell -ArgumentList "-NoProfile -Command celery -A api.src.tasks worker -Q default -c 2 --loglevel=INFO" -NoNewWindow

# Inicia Flower para monitoramento
Start-Process powershell -ArgumentList "-NoProfile -Command celery -A api.src.tasks flower" -NoNewWindow

Write-Host "Serviços iniciados com sucesso!" 