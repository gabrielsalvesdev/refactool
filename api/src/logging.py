# api/src/logging.py
import json
import structlog
from structlog.contextvars import merge_contextvars
import logging

# Configurar logging básico
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
)

# Configurar processadores do structlog
processors = [
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.JSONRenderer()
]

# Configurar structlog
structlog.configure(
    processors=processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Criar logger
logger = structlog.get_logger() 