"""Structured (JSON) logging with OpenTelemetry / request correlation.

Every record is emitted as one JSON line and enriched with the correlation context
(request_id, operation, operation_id, principal) plus the active span's trace_id/span_id.
A log collector can ship stdout straight to the OTel pipeline.
"""
import json
import logging
import sys
from datetime import datetime, timezone

from opentelemetry import trace

from infrastructure.context import (
    operation_id_var,
    operation_var,
    principal_var,
    request_id_var,
)

# LogRecord attributes that are not user-supplied structured extras.
_RESERVED = frozenset(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "taskName"}


class CorrelationFilter(logging.Filter):
    """Attach correlation context + trace ids onto each record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.operation = operation_var.get()
        record.operation_id = operation_id_var.get()
        record.principal = principal_var.get()
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            record.trace_id = format(span_context.trace_id, "032x")
            record.span_id = format(span_context.span_id, "016x")
        return True


class JsonFormatter(logging.Formatter):
    """Render each record as a single-line JSON object, including `extra=` fields."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_") and value is not None:
                payload[key] = value
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(CorrelationFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.getLevelNamesMapping().get(level.upper(), logging.INFO))
