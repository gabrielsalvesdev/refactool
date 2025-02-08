import os
import logging
import structlog

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)

logger = structlog.get_logger() 