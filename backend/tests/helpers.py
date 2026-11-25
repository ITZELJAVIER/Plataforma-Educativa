from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.adapters.outbound.device.mqtt import MqttDeviceAdapter
from src.adapters.outbound.device.simulated import SimulatedDeviceAdapter
from src.adapters.outbound.device.transport import TransporteFalso
from src.adapters.outbound.persistence.in_memory import (
    InMemoryAuditRepository,
    InMemoryDeviceRepository,
    InMemoryDeviceStateEventRepository,
    InMemoryPeripheralTypeRepository,
    InMemorySessionRepository,
    InMemoryUserRepository,
)
from src.adapters.outbound.security.pbkdf2_password_hasher import Pbkdf2PasswordHasher
from src.application.use_cases.device_management import DeviceManagementService
from src.application.use_cases.peripheral_catalog import PeripheralCatalogService
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.user import User
from src.domain.ports.device_adapter import DeviceAdapter
from src.domain.value_objects.role import Role

ADMIN_ID = "admin-prueba"
ADMIN_PASSWORD = "clave-admin-solo-prueba"


class FakeClock:
    def __init__(self, start: datetime | None = None) -> None:
        self.current = start or datetime(2026, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: int) -> None:
        self.current += timedelta(seconds=seconds)


class SequenceTokenGenerator:
    def __init__(self, tokens: list[str] | None = None) -> None:
        self.tokens = list(tokens or [])
        self.index = 0

    def generate(self) -> str:
        if self.index < len(self.tokens):
            token = self.tokens[self.index]
        else:
            token = f"token-{self.index}"
        self.index += 1
        return token


@dataclass
class Harness:
    service: UserAuthService
    users: InMemoryUserRepository
    sessions: InMemorySessionRepository
    audit: InMemoryAuditRepository
    clock: FakeClock
    hasher: Pbkdf2PasswordHasher


def build_harness(
    *, ttl_seconds: int = 60, tokens: list[str] | None = None
) -> Harness:
    hasher = Pbkdf2PasswordHasher()
    users = InMemoryUserRepository(
        [
            User(
                id=ADMIN_ID,
                password_hash=hasher.hash(ADMIN_PASSWORD),
                role=Role.ADMINISTRADOR,
                active=True,
            )
        ]
    )
    sessions = InMemorySessionRepository()
    audit = InMemoryAuditRepository()
    clock = FakeClock()
    service = UserAuthService(
        users=users,
        sessions=sessions,
        audit=audit,
        hasher=hasher,
        tokens=SequenceTokenGenerator(tokens),
        clock=clock,
        session_ttl_seconds=ttl_seconds,
    )
    return Harness(
        service=service,
        users=users,
        sessions=sessions,
        audit=audit,
        clock=clock,
        hasher=hasher,
    )


@dataclass
class CatalogHarness:
    auth: Harness
    repository: InMemoryPeripheralTypeRepository
    service: PeripheralCatalogService


def build_catalog_harness(
    *, ttl_seconds: int = 60, tokens: list[str] | None = None
) -> CatalogHarness:
    auth = build_harness(ttl_seconds=ttl_seconds, tokens=tokens)
    repository = InMemoryPeripheralTypeRepository()
    service = PeripheralCatalogService(types=repository, auth=auth.service)
    service.initialize_base_types()
    return CatalogHarness(auth=auth, repository=repository, service=service)


@dataclass
class DeviceHarness:
    auth: Harness
    devices: InMemoryDeviceRepository
    events: InMemoryDeviceStateEventRepository
    adapters: dict[str, DeviceAdapter]
    transporte: TransporteFalso
    service: DeviceManagementService

    @property
    def simulado(self) -> SimulatedDeviceAdapter:
        return self.adapters["simulado"]  # type: ignore[return-value]

    @property
    def mqtt(self) -> MqttDeviceAdapter:
        return self.adapters["mqtt"]  # type: ignore[return-value]


def build_device_harness(
    *, ttl_seconds: int = 60, tokens: list[str] | None = None
) -> DeviceHarness:
    auth = build_harness(ttl_seconds=ttl_seconds, tokens=tokens)
    transporte = TransporteFalso()
    simulado = SimulatedDeviceAdapter(transporte)
    mqtt = MqttDeviceAdapter(transporte)
    adapters: dict[str, DeviceAdapter] = {simulado.name: simulado, mqtt.name: mqtt}
    devices = InMemoryDeviceRepository()
    events = InMemoryDeviceStateEventRepository()
    service = DeviceManagementService(
        devices=devices,
        events=events,
        adapters=adapters,
        auth=auth.service,
        audit=auth.audit,
        clock=auth.clock,
    )
    return DeviceHarness(
        auth=auth,
        devices=devices,
        events=events,
        adapters=adapters,
        transporte=transporte,
        service=service,
    )
