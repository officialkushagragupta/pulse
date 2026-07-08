"""Global error handling: normalize failures into a typed, correlated JSON envelope."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from infrastructure.context import operation_id_var, request_id_var

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
    operation_id: str | None = None


def _envelope(status_code: int, error: str, detail: str | None) -> JSONResponse:
    body = ErrorResponse(
        error=error,
        detail=detail,
        request_id=request_id_var.get(),
        operation_id=operation_id_var.get(),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _envelope(exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _envelope(422, "validation_error", str(exc.errors()))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception")
        return _envelope(500, "internal_error", "An unexpected error occurred.")
