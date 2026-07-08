"""Per-request correlation context, propagated via contextvars.

- request_id  : correlation id for the whole request (client- or gateway-supplied,
                generated if absent). Ties an authenticated call across services.
- operation   : logical operation name (HTTP method + path).
- operation_id : unique id for this single operation/handler invocation.
- principal   : authenticated subject, when the auth/gateway layer supplies it (Day 2).
"""
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
operation_var: ContextVar[str | None] = ContextVar("operation", default=None)
operation_id_var: ContextVar[str | None] = ContextVar("operation_id", default=None)
principal_var: ContextVar[str | None] = ContextVar("principal", default=None)
