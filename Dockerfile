# Build stage
FROM python:3.9-slim as builder

WORKDIR /build

# Instalar dependências de build
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

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