# Build stage
FROM python:3.8-slim as builder

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Criar e definir diretório de trabalho
WORKDIR /build

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Final stage
FROM python:3.8-slim

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Criar e definir diretório de trabalho
WORKDIR /app

# Criar usuário não-root
RUN useradd -m -r appuser && \
    chown appuser:appuser /app

# Copiar wheels do stage anterior
COPY --from=builder /build/wheels /wheels

# Instalar dependências
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copiar código fonte
COPY --chown=appuser:appuser microservices/ /app/microservices/
COPY --chown=appuser:appuser tests/ /app/tests/

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para executar a aplicação
CMD ["python", "-m", "uvicorn", "microservices.source_provider.src.main:app", "--host", "0.0.0.0", "--port", "8000"] 