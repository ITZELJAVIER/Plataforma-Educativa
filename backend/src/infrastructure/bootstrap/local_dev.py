"""Punto de entrada temporal para desarrollo local sin PostgreSQL.

Este módulo construye un grafo de objetos completamente en memoria y exporta
la aplicación ASGI como ``app``. No importa ni modifica el punto de entrada de
producción (``asgi.py``) y todos los datos desaparecen al detener el proceso.

Arranque previsto (terminal interactiva)::

    python -m uvicorn src.infrastructure.bootstrap.local_dev:app \
        --host 127.0.0.1 --port 8000

Para arranques automatizados (scripts o servicios) se puede definir
``PLATAFORMA_DEV_ADMIN_PASSWORD`` y se omite la pregunta interactiva. También
se aprovisionan usuarios temporales de prueba para los tres roles, con
contraseñas configurables mediante ``PLATAFORMA_DEV_DOCENTE_PASSWORD`` y
``PLATAFORMA_DEV_ESTUDIANTE_PASSWORD``. Estas variables solo tienen efecto en
este bootstrap en memoria; nunca se usan en el punto de entrada de producción.
"""

from __future__ import annotations

import getpass
import os
import secrets

from src.adapters.outbound.persistence.in_memory import (
    InMemoryAuditRepository,
    InMemoryPeripheralTypeRepository,
    InMemorySessionRepository,
    InMemoryUserRepository,
)
from src.adapters.outbound.security.pbkdf2_password_hasher import Pbkdf2PasswordHasher
from src.adapters.outbound.security.random_token_generator import RandomTokenGenerator
from src.application.use_cases.peripheral_catalog import PeripheralCatalogService
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.user import User
from src.domain.value_objects.role import Role
from src.infrastructure.bootstrap.app import (
    build_in_memory_device_service,
    create_app,
)
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.logging.config import configure_logging

ADMIN_ID = "admin"
DOCENTE_ID = "docente"
ESTUDIANTE_ID = "estudiante"
SESSION_TTL_SECONDS = 8 * 60 * 60

# Usuarios de desarrollo, uno por rol. Las contraseñas por defecto son solo
# locales y pueden sustituirse con variables de entorno.
DEV_USERS: tuple[tuple[str, Role, str, str], ...] = (
    (ADMIN_ID, Role.ADMINISTRADOR, "PLATAFORMA_DEV_ADMIN_PASSWORD", "dev-admin"),
    (DOCENTE_ID, Role.DOCENTE, "PLATAFORMA_DEV_DOCENTE_PASSWORD", "clave-docente"),
    (
        ESTUDIANTE_ID,
        Role.ESTUDIANTE,
        "PLATAFORMA_DEV_ESTUDIANTE_PASSWORD",
        "clave-estudiante",
    ),
)


def _request_password() -> str:
    """Solicita y confirma la contraseña del administrador sin mostrarla.

    Si ``PLATAFORMA_DEV_ADMIN_PASSWORD`` está definida, se usa su valor y no se
    solicita entrada interactiva. Es un mecanismo exclusivo de desarrollo local.
    """
    configured = os.environ.get("PLATAFORMA_DEV_ADMIN_PASSWORD")
    if configured:
        return configured

    while True:
        password = getpass.getpass(f"Contraseña para el administrador '{ADMIN_ID}': ")
        confirmation = getpass.getpass("Confirme la contraseña: ")

        if not password or not confirmation:
            print("La contraseña no puede estar vacía. Inténtelo de nuevo.", flush=True)
            continue
        if not secrets.compare_digest(password, confirmation):
            print("Las contraseñas no coinciden. Inténtelo de nuevo.", flush=True)
            continue
        return password


def _build_auth_service() -> UserAuthService:
    users = InMemoryUserRepository()
    hasher = Pbkdf2PasswordHasher()

    service = UserAuthService(
        users=users,
        sessions=InMemorySessionRepository(),
        audit=InMemoryAuditRepository(),
        hasher=hasher,
        tokens=RandomTokenGenerator(),
        clock=SystemClock(),
        session_ttl_seconds=SESSION_TTL_SECONDS,
    )

    passwords: dict[str, str] = {}
    for user_id, _role, env_name, default in DEV_USERS:
        if user_id == ADMIN_ID:
            passwords[user_id] = _request_password()
        else:
            passwords[user_id] = os.environ.get(env_name) or default

    for user_id, role, _env_name, _default in DEV_USERS:
        if users.get(user_id) is None:
            users.add(
                User(
                    id=user_id,
                    password_hash=hasher.hash(passwords[user_id]),
                    role=role,
                    active=True,
                )
            )
    del passwords

    print(
        "Usuarios temporales aprovisionados en memoria: "
        + ", ".join(f"{user_id} ({role.value})" for user_id, role, _, _ in DEV_USERS),
        flush=True,
    )
    return service


def _build_catalog(auth_service: UserAuthService) -> PeripheralCatalogService:
    catalog = PeripheralCatalogService(
        types=InMemoryPeripheralTypeRepository(),
        auth=auth_service,
    )
    catalog.initialize_base_types()
    return catalog


configure_logging()

_auth_service = _build_auth_service()
_catalog = _build_catalog(_auth_service)
_devices = build_in_memory_device_service(_auth_service)

app = create_app(
    settings=None,
    service=_auth_service,
    catalog=_catalog,
    devices=_devices,
)
