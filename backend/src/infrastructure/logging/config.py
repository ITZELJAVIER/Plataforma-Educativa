"""Configuración de logging estructurado mediante la biblioteca estándar.

Este módulo pertenece a la capa de infraestructura. Expone un formateador JSON,
una configuración idempotente y un helper para emitir eventos con contexto.
El dominio y los casos de uso no importan este módulo.

Política de redacción: todo valor se normaliza a tipos JSON nativos antes de
serializar. No se invocan ``__str__``, ``__repr__`` ni ``__deepcopy__`` de objetos
ajenos; los objetos desconocidos se sustituyen por un marcador de tipo.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import os
import re
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

_MARKER = "_plataforma_educativa_handler"
_MAX_DEPTH = 8

_SENSITIVE_KEY = re.compile(
    r"password|passwd|pwd|token|secret|authorization|api[_-]?key|credential|dsn|database_url",
    re.IGNORECASE,
)
_KV_SENSITIVE = re.compile(
    r"\b(password|passwd|pwd|token|secret|authorization|api[_-]?key|credential|dsn|database_url)\b"
    r"\s*[:=]\s*"
    r"(\"[^\"]*\"|'[^']*'|Bearer\s+[A-Za-z0-9._~+/=-]+|[^\s,;]+)",
    re.IGNORECASE,
)
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_DSN = re.compile(
    r"\b(postgres(?:ql)?(?:\+[\w.]+)?://[^\s:/@]+:)[^\s@/]+(@)",
    re.IGNORECASE,
)


def _redact_text(texto: str) -> str:
    """Redacta secretos en texto aplicando las reglas en orden seguro."""
    texto = _BEARER.sub("Bearer [REDACTED]", texto)
    texto = _DSN.sub(lambda m: f"{m.group(1)}[REDACTED]{m.group(2)}", texto)
    return _KV_SENSITIVE.sub(lambda m: f"{m.group(1)}=[REDACTED]", texto)


def _safe_type_name(valor: object) -> str:
    """Nombre de tipo sin invocar ganchos personalizados."""
    try:
        nombre = type(valor).__name__
    except Exception:
        return "[DESCONOCIDO]"
    return nombre if isinstance(nombre, str) else "[DESCONOCIDO]"


def _safe_key(clave: Any) -> str | int | float | bool | None:
    """Normaliza una clave a un tipo aceptado por ``json.dumps``."""
    if clave is None or isinstance(clave, (str, int, float, bool)):
        return _redact_text(clave) if isinstance(clave, str) else clave
    return "[CLAVE_NO_SEGURA]"


def _sanitize(valor: Any, profundidad: int, vistos: set[int]) -> Any:
    """Convierte ``valor`` a tipos JSON nativos, redactando antes de serializar."""
    if isinstance(valor, str):
        return _redact_text(valor)
    if valor is None or isinstance(valor, (bool, int, float)):
        return valor
    if profundidad >= _MAX_DEPTH:
        return "[PROFUNDIDAD_MAXIMA]"

    identidad = id(valor)
    if identidad in vistos:
        return "[CIRCULAR]"

    if isinstance(valor, Mapping):
        vistos.add(identidad)
        try:
            resultado: dict[Any, Any] = {}
            for clave, item in valor.items():
                clave_segura = _safe_key(clave)
                if isinstance(clave_segura, str) and _SENSITIVE_KEY.search(clave_segura):
                    resultado[clave_segura] = "[REDACTED]"
                else:
                    resultado[clave_segura] = _sanitize(item, profundidad + 1, vistos)
            return resultado
        finally:
            vistos.discard(identidad)

    if isinstance(valor, (list, tuple, set, frozenset)):
        vistos.add(identidad)
        try:
            return [_sanitize(item, profundidad + 1, vistos) for item in valor]
        finally:
            vistos.discard(identidad)

    if dataclasses.is_dataclass(valor) and not isinstance(valor, type):
        vistos.add(identidad)
        try:
            try:
                atributos = object.__getattribute__(valor, "__dict__")
            except Exception:
                atributos = {}
            resultado: dict[str, Any] = {}
            for campo in dataclasses.fields(valor):
                nombre = campo.name
                if nombre in atributos:
                    if _SENSITIVE_KEY.search(nombre):
                        resultado[nombre] = "[REDACTED]"
                    else:
                        resultado[nombre] = _sanitize(
                            atributos[nombre], profundidad + 1, vistos
                        )
            if resultado:
                return resultado
        finally:
            vistos.discard(identidad)

    return {"__tipo__": _safe_type_name(valor), "__valor__": "[OMITIDO]"}


def redact_sensitive(value: Any) -> Any:
    """Devuelve una copia segura de ``value`` para incluirla en un registro."""
    return _sanitize(value, 0, set())


def _safe_traceback(exc_info: tuple[Any, Any, Any]) -> dict[str, Any]:
    """Resume un traceback sin invocar ``str(exc)`` ni capturar variables."""
    tipo, _exc, tb = exc_info
    nombre = tipo.__name__ if isinstance(tipo, type) else "[DESCONOCIDO]"
    if not isinstance(nombre, str):
        nombre = "[DESCONOCIDO]"
    marcos: list[dict[str, Any]] = []
    try:
        for marco in traceback.extract_tb(tb):
            archivo = os.path.basename(marco.filename)
            marcos.append(
                {
                    "archivo": _redact_text(archivo) if isinstance(archivo, str) else "[OMITIDO]",
                    "linea": marco.lineno,
                    "funcion": _redact_text(marco.name) if isinstance(marco.name, str) else "[OMITIDO]",
                }
            )
    except Exception:
        marcos = []
    return {"tipo": _redact_text(nombre), "frames": marcos}


class JsonFormatter(logging.Formatter):
    """Convierte cada ``LogRecord`` en un objeto JSON con campos estables."""

    def format(self, record: logging.LogRecord) -> str:
        instante = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        payload: dict[str, Any] = {
            "timestamp": instante,
            "level": record.levelname,
            "logger": record.name,
            "message": _redact_text(record.getMessage()),
            "context": _sanitize(getattr(record, "context", {}) or {}, 0, set()),
        }
        exc_info = getattr(record, "exc_info", None)
        if exc_info:
            payload["traceback"] = _safe_traceback(exc_info)
        try:
            return json.dumps(payload, ensure_ascii=False)
        except (TypeError, ValueError, RecursionError):
            return json.dumps(
                {
                    "timestamp": instante,
                    "level": record.levelname,
                    "logger": record.name,
                    "message": "[LOG_SERIALIZATION_FAILED]",
                    "context": {},
                },
                ensure_ascii=False,
            )


def _configure_uvicorn_loggers(handler: logging.Handler) -> None:
    """Enruta errores de Uvicorn al handler JSON sin duplicar emisiones."""
    loggers = [logging.getLogger(nombre) for nombre in ("uvicorn", "uvicorn.error")]
    if not any(logger.handlers for logger in loggers):
        return
    for logger in loggers:
        if logger.handlers:
            logger.handlers = [handler]
            logger.propagate = False


def configure_logging(level: str = "INFO") -> None:
    """Instala un único handler JSON en stdout. Llamadas posteriores no hacen nada.

    La primera llamada fija el nivel (M-1). El vocabulario de redacción es
    inglés (M-6); no se registran cabeceras, bodies ni query strings.
    """
    root = logging.getLogger()
    for handler in root.handlers:
        if getattr(handler, _MARKER, False):
            return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    setattr(handler, _MARKER, True)
    root.addHandler(handler)
    root.setLevel(getattr(logging, str(level).upper(), logging.INFO))
    _configure_uvicorn_loggers(handler)


def log_event(
    level: int,
    message: str,
    *,
    logger_name: str = "plataforma_educativa",
    exc_info: Any = None,
    **context: Any,
) -> None:
    """Emite un evento estructurado con contexto adicional."""
    logging.getLogger(logger_name).log(
        level, message, extra={"context": context}, exc_info=exc_info
    )
