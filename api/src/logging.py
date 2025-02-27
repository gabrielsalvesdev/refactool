# api/src/logging.py
import json
import structlog
from structlog.contextvars import merge_contextvars

structlog.configure(
    processors=[
        merge_contextvars,
        structlog.processors.JSONRenderer(
            serializer=lambda data, **kwargs: json.dumps(data, ensure_ascii=False)
        ),
        structlog.processors.add_log_level
    ],
    context_class=dict,
)

logger = structlog.get_logger() 