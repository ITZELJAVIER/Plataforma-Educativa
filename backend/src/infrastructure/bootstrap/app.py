from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.inbound.rest.device_router import router as device_router
from src.adapters.inbound.rest.peripheral_router import router as peripheral_router
from src.adapters.inbound.rest.router import router
from src.adapters.outbound.device.mqtt import MqttDeviceAdapter
from src.adapters.outbound.device.simulated import SimulatedDeviceAdapter
from src.adapters.outbound.device.transport import TransporteFalso
from src.adapters.outbound.persistence.in_memory import (
    InMemoryDeviceRepository,
    InMemoryDeviceStateEventRepository,
    InMemoryPeripheralTypeRepository,
)
from src.adapters.outbound.persistence.postgres import (
    PostgresAuditRepository,
    PostgresDeviceRepository,
    PostgresDeviceStateEventRepository,
    PostgresPeripheralTypeRepository,
    PostgresSessionRepository,
    PostgresUserRepository,
    initialize_schema,
)
from src.adapters.outbound.security.pbkdf2_password_hasher import Pbkdf2PasswordHasher
from src.adapters.outbound.security.random_token_generator import RandomTokenGenerator
from src.application.use_cases.device_management import DeviceManagementService
from src.application.use_cases.peripheral_catalog import PeripheralCatalogService
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.user import User
from src.domain.ports.device_adapter import DeviceAdapter
from src.domain.value_objects.role import Role
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.config.settings import Settings, load_settings
from src.infrastructure.logging.config import configure_logging
from src.infrastructure.logging.request_logging import (
    http_error_handler,
    request_logging_middleware,
    request_validation_error_handler,
    unhandled_exception_handler,
)


def _seed_initial_users(users: PostgresUserRepository) -> None:
    """Aprovisiona los usuarios de prueba cuando la base está vacía.

    Solo se ejecuta si no existe ningún usuario. Las contraseñas vienen de
    variables de entorno y son valores de prueba; deben cambiarse en un
    despliegue real.
    """
    if users.list():
        return

    seeds = (
        ("admin", Role.ADMINISTRADOR, "INITIAL_ADMIN_PASSWORD", "dev-admin"),
        ("docente", Role.DOCENTE, "INITIAL_DOCENTE_PASSWORD", "clave-docente"),
        (
            "estudiante",
            Role.ESTUDIANTE,
            "INITIAL_ESTUDIANTE_PASSWORD",
            "clave-estudiante",
        ),
    )
    hasher = Pbkdf2PasswordHasher()
    for user_id, role, env_name, default in seeds:
        password = os.getenv(env_name) or default
        users.add(
            User(
                id=user_id,
                password_hash=hasher.hash(password),
                role=role,
                active=True,
            )
        )


def build_service(settings: Settings) -> UserAuthService:
    initialize_schema(settings.database_url)
    users = PostgresUserRepository(settings.database_url)
    _seed_initial_users(users)
    return UserAuthService(
        users=users,
        sessions=PostgresSessionRepository(settings.database_url),
        audit=PostgresAuditRepository(settings.database_url),
        hasher=Pbkdf2PasswordHasher(),
        tokens=RandomTokenGenerator(),
        clock=SystemClock(),
        session_ttl_seconds=settings.session_ttl_seconds,
    )


def build_catalog_service(
    settings: Settings, auth_service: UserAuthService
) -> PeripheralCatalogService:
    service = PeripheralCatalogService(
        types=PostgresPeripheralTypeRepository(settings.database_url),
        auth=auth_service,
    )
    service.initialize_base_types()
    return service


def _device_adapters() -> dict[str, DeviceAdapter]:
    transporte = TransporteFalso()
    simulado = SimulatedDeviceAdapter(transporte)
    mqtt = MqttDeviceAdapter(transporte)
    return {simulado.name: simulado, mqtt.name: mqtt}


def build_device_service(
    settings: Settings, auth_service: UserAuthService
) -> DeviceManagementService:
    return DeviceManagementService(
        devices=PostgresDeviceRepository(settings.database_url),
        events=PostgresDeviceStateEventRepository(settings.database_url),
        adapters=_device_adapters(),
        auth=auth_service,
        audit=auth_service.audit,
        clock=SystemClock(),
        default_adapter=settings.device_adapter,
    )


def build_in_memory_device_service(
    auth_service: UserAuthService,
) -> DeviceManagementService:
    return DeviceManagementService(
        devices=InMemoryDeviceRepository(),
        events=InMemoryDeviceStateEventRepository(),
        adapters=_device_adapters(),
        auth=auth_service,
        audit=auth_service.audit,
        clock=SystemClock(),
    )


def _cors_origins(settings: Settings | None) -> list[str]:
    if settings is not None:
        return list(settings.cors_allowed_origins)
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app(
    settings: Settings | None = None,
    *,
    service: UserAuthService | None = None,
    catalog: PeripheralCatalogService | None = None,
    devices: DeviceManagementService | None = None,
) -> FastAPI:
    configure_logging()
    app = FastAPI(title="Plataforma Educativa API", version="1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(settings),
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.middleware("http")(request_logging_middleware)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    if service is None:
        resolved_settings = settings or load_settings()
        resolved_service = build_service(resolved_settings)
    else:
        resolved_service = service
        resolved_settings = settings

    if catalog is None:
        if resolved_settings is None:
            catalog = PeripheralCatalogService(
                types=InMemoryPeripheralTypeRepository(),
                auth=resolved_service,
            )
            catalog.initialize_base_types()
        else:
            catalog = build_catalog_service(resolved_settings, resolved_service)

    if devices is None:
        if resolved_settings is None:
            devices = build_in_memory_device_service(resolved_service)
        else:
            devices = build_device_service(resolved_settings, resolved_service)

    app.state.user_auth = resolved_service
    app.state.peripheral_catalog = catalog
    app.state.devices = devices
    app.include_router(router, prefix="/api/v1")
    app.include_router(peripheral_router, prefix="/api/v1")
    app.include_router(device_router, prefix="/api/v1")
    return app
