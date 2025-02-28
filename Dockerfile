# Build stage
FROM python:3.9-slim as builder

WORKDIR /build

# Instalar dependências de build e atualizar pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip==25.0.1

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Atualizar pip antes de instalar os wheels
RUN python -m pip install --upgrade pip==25.0.1

# Copiar wheels e instalar
COPY --from=builder /wheels /wheels
COPY . .

RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expor porta
EXPOSE ${PORT}

# Comando para iniciar
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 