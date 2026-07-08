"""ASGI middleware establishing per-request correlation context.

Reads an inbound X-Request-Id (or generates one), assigns a fresh operation id, derives
the operation name, and captures the authenticated principal when the gateway/auth layer
forwards it. Echoes the ids back on the response for client-side tracing.
"""
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from infrastructure.context import (
    operation_id_var,
    operation_var,
    principal_var,
    request_id_var,
)

_REQUEST_ID_HEADER = b"x-request-id"
_PRINCIPAL_HEADER = b"x-user-id"  # populated by the auth/gateway layer (Day 2)


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        request_id = headers.get(_REQUEST_ID_HEADER, b"").decode() or uuid.uuid4().hex
        operation_id = uuid.uuid4().hex
        operation = f"{scope['method']} {scope['path']}"
        principal = headers.get(_PRINCIPAL_HEADER, b"").decode() or None

        tokens = (
            request_id_var.set(request_id),
            operation_var.set(operation),
            operation_id_var.set(operation_id),
            principal_var.set(principal),
        )

        async def send_with_ids(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    [
                        (b"x-request-id", request_id.encode()),
                        (b"x-operation-id", operation_id.encode()),
                    ]
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_ids)
        finally:
            request_id_var.reset(tokens[0])
            operation_var.reset(tokens[1])
            operation_id_var.reset(tokens[2])
            principal_var.reset(tokens[3])
