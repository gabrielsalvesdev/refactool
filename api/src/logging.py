# api/src/logging.py
import json
import structlog

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(
            serializer=lambda data, **kwargs: json.dumps(data, ensure_ascii=False)
        ),
        structlog.processors.add_log_level
    ],
    context_class=structlog.contextvars.wrap_dict(dict),
)

logger = structlog.get_logger() 