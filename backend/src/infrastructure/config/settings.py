from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import quote

POSTGRES_KEYS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    database_url: str
    session_ttl_seconds: int
    cors_allowed_origins: tuple[str, ...] = ("http://localhost:5173",)
    device_adapter: str = "simulado"


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = environ if environ is not None else os.environ

    ttl_raw = env.get("SESSION_TTL_SECONDS")
    if not ttl_raw:
        raise ConfigError("Falta la variable obligatoria: SESSION_TTL_SECONDS")
    try:
        ttl = int(ttl_raw)
    except ValueError as exc:
        raise ConfigError("SESSION_TTL_SECONDS debe ser un entero") from exc
    if ttl <= 0:
        raise ConfigError("SESSION_TTL_SECONDS debe ser mayor que cero")

    raw_origins = env.get("CORS_ALLOWED_ORIGINS") or "http://localhost:5173"
    cors_allowed_origins = tuple(
        origin.strip() for origin in raw_origins.split(",") if origin.strip()
    )

    database_url = env.get("DATABASE_URL")
    if not database_url:
        missing = [key for key in POSTGRES_KEYS if not env.get(key)]
        if missing:
            raise ConfigError(
                "Faltan variables obligatorias: " + ", ".join(missing)
            )
        user = quote(env["POSTGRES_USER"], safe="")
        password = quote(env["POSTGRES_PASSWORD"], safe="")
        host = env["POSTGRES_HOST"]
        port = env["POSTGRES_PORT"]
        name = env["POSTGRES_DB"]
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"

    device_adapter = env.get("DEVICE_ADAPTER", "simulado").strip() or "simulado"

    return Settings(
        database_url=database_url,
        session_ttl_seconds=ttl,
        cors_allowed_origins=cors_allowed_origins,
        device_adapter=device_adapter,
    )
