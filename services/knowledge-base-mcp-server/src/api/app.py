"""FastAPI application factory for knowledge-base-mcp-server."""
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.errors import register_error_handlers
from api.middleware import RequestContextMiddleware
from infrastructure.config import get_settings
from infrastructure.logging import configure_logging
from infrastructure.telemetry import configure_telemetry

_SERVICE_NAME = "knowledge-base-mcp-server"


def create_app() -> FastAPI:
    configure_telemetry(_SERVICE_NAME)
    settings = get_settings()  # fail fast if required config is missing
    configure_logging(settings.log_level)

    app = FastAPI(title="Pulse knowledge-base-mcp-server", version="0.1.0")
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    FastAPIInstrumentor.instrument_app(app)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": _SERVICE_NAME}

    return app
