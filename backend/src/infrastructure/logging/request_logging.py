"""Registro centralizado de peticiones y excepciones HTTP.

Los handlers registran una sola vez cada error. El middleware solo registra
respuestas correctas, de modo que no se duplican los eventos de error.
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, PlainTextResponse

from src.infrastructure.logging.config import log_event

_LOGGER_NAME = "plataforma_educativa.http"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


def _resolve_request_id(request: Request) -> str:
    """Conserva IDs válidos y genera un UUID cuando la cabecera no es fiable."""
    candidate = request.headers.get("x-request-id")
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid.uuid4())


def _duration_ms(request: Request) -> float:
    start = getattr(request.state, "start_time", None)
    if start is None:
        return 0.0
    return round((time.perf_counter() - start) * 1000, 2)


def _base_context(request: Request, **extra: Any) -> dict[str, Any]:
    context: dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
        "request_id": getattr(request.state, "request_id", None),
        "duration_ms": _duration_ms(request),
    }
    context.update(extra)
    return context


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Asigna un identificador de petición y registra solo respuestas correctas."""
    request.state.start_time = time.perf_counter()
    request.state.request_id = _resolve_request_id(request)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    if response.status_code < 400:
        log_event(
            logging.INFO,
            "request_completed",
            logger_name=_LOGGER_NAME,
            **_base_context(request, status_code=response.status_code),
        )
    return response


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> Response:
    """Registra una vez cada HTTPException y conserva la respuesta original."""
    level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    log_event(
        level,
        "http_error",
        logger_name=_LOGGER_NAME,
        **_base_context(
            request,
            status_code=exc.status_code,
            exception_type=type(exc).__name__,
        ),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> Response:
    """Registra ubicación y tipo de error sin incluir valores del payload."""
    errores = [
        {"loc": error.get("loc"), "type": error.get("type")}
        for error in exc.errors()
    ]
    log_event(
        logging.WARNING,
        "request_validation_error",
        logger_name=_LOGGER_NAME,
        **_base_context(
            request,
            status_code=422,
            exception_type=type(exc).__name__,
            errors=errores,
        ),
    )
    return await request_validation_exception_handler(request, exc)


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """Registra una vez una excepción no controlada sin exponer su mensaje."""
    log_event(
        logging.ERROR,
        "unhandled_exception",
        logger_name=_LOGGER_NAME,
        exc_info=exc,
        **_base_context(
            request,
            status_code=500,
            exception_type=type(exc).__name__,
        ),
    )
    return PlainTextResponse("Internal Server Error", status_code=500)
