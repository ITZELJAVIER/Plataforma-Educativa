from __future__ import annotations

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.domain.entities.audit_event import AuditEvent
from src.domain.entities.device import Device
from src.domain.entities.device_state_event import DeviceStateEvent
from src.domain.entities.peripheral_type import PeripheralType
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.domain.value_objects.connection_state import ConnectionState
from src.domain.value_objects.role import Role

SCHEMA_USER_AUTH = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    active BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL
);
"""

SCHEMA_PERIPHERAL_CATALOG = """
CREATE TABLE IF NOT EXISTS peripheral_types (
    tipo TEXT PRIMARY KEY,
    metadata JSONB NOT NULL
);
"""

SCHEMA_DEVICE_MANAGEMENT = """
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    perfil_hardware TEXT NOT NULL,
    ubicacion TEXT,
    habilitado BOOLEAN NOT NULL,
    adaptador TEXT NOT NULL,
    estado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS device_state_events (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(id),
    estado_anterior TEXT NOT NULL,
    estado_nuevo TEXT NOT NULL,
    ocurrido_en TIMESTAMPTZ NOT NULL
);
"""


def initialize_schema(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_USER_AUTH)
            cursor.execute(SCHEMA_PERIPHERAL_CATALOG)
            cursor.execute(SCHEMA_DEVICE_MANAGEMENT)


class PostgresUserRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, user: User) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (id, password_hash, role, active) "
                    "VALUES (%s, %s, %s, %s)",
                    (user.id, user.password_hash, user.role.value, user.active),
                )

    def get(self, user_id: str) -> User | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
        return self._to_user(row) if row else None

    def list(self) -> list[User]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
        return [self._to_user(row) for row in rows]

    def save(self, user: User) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET password_hash = %s, role = %s, active = %s "
                    "WHERE id = %s",
                    (user.password_hash, user.role.value, user.active, user.id),
                )

    @staticmethod
    def _to_user(row: dict) -> User:
        return User(
            id=row["id"],
            password_hash=row["password_hash"],
            role=Role.from_value(row["role"]),
            active=row["active"],
        )


class PostgresSessionRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, session: Session) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO sessions (token, user_id, expires_at, revoked) "
                    "VALUES (%s, %s, %s, %s)",
                    (session.token, session.user_id, session.expires_at, session.revoked),
                )

    def get(self, token: str) -> Session | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sessions WHERE token = %s", (token,))
                row = cursor.fetchone()
        return self._to_session(row) if row else None

    def save(self, session: Session) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE sessions SET revoked = %s WHERE token = %s",
                    (session.revoked, session.token),
                )

    def invalidate_all_for_user(self, user_id: str) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE sessions SET revoked = TRUE "
                    "WHERE user_id = %s AND revoked = FALSE",
                    (user_id,),
                )

    @staticmethod
    def _to_session(row: dict) -> Session:
        return Session(
            token=row["token"],
            user_id=row["user_id"],
            expires_at=row["expires_at"],
            revoked=row["revoked"],
        )


class PostgresAuditRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, event: AuditEvent) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO audit_events (actor, action, resource, occurred_at) "
                    "VALUES (%s, %s, %s, %s)",
                    (event.actor, event.action, event.resource, event.occurred_at),
                )

    def list(self) -> list[AuditEvent]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT actor, action, resource, occurred_at FROM audit_events"
                )
                rows = cursor.fetchall()
        return [
            AuditEvent(
                actor=row["actor"],
                action=row["action"],
                resource=row["resource"],
                occurred_at=row["occurred_at"],
            )
            for row in rows
        ]


class PostgresPeripheralTypeRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, definition: PeripheralType) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO peripheral_types (tipo, metadata) VALUES (%s, %s)",
                    (definition.tipo, Jsonb(definition.to_dict())),
                )

    def get(self, tipo: str) -> PeripheralType | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT metadata FROM peripheral_types WHERE tipo = %s",
                    (tipo.strip(),),
                )
                row = cursor.fetchone()
        return PeripheralType.from_dict(row["metadata"]) if row else None

    def list(self) -> list[PeripheralType]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT metadata FROM peripheral_types ORDER BY tipo"
                )
                rows = cursor.fetchall()
        return [PeripheralType.from_dict(row["metadata"]) for row in rows]

    def save(self, definition: PeripheralType) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE peripheral_types SET metadata = %s WHERE tipo = %s",
                    (Jsonb(definition.to_dict()), definition.tipo),
                )


class PostgresDeviceRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, device: Device) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO devices (id, nombre, tipo, perfil_hardware, "
                    "ubicacion, habilitado, adaptador, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        device.id,
                        device.nombre,
                        device.tipo,
                        device.perfil_hardware,
                        device.ubicacion,
                        device.habilitado,
                        device.adaptador,
                        device.estado.value,
                    ),
                )

    def get(self, device_id: str) -> Device | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
                row = cursor.fetchone()
        return self._to_device(row) if row else None

    def list(self) -> list[Device]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM devices ORDER BY id")
                rows = cursor.fetchall()
        return [self._to_device(row) for row in rows]

    def save(self, device: Device) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE devices SET nombre = %s, tipo = %s, perfil_hardware = %s, "
                    "ubicacion = %s, habilitado = %s, adaptador = %s, estado = %s "
                    "WHERE id = %s",
                    (
                        device.nombre,
                        device.tipo,
                        device.perfil_hardware,
                        device.ubicacion,
                        device.habilitado,
                        device.adaptador,
                        device.estado.value,
                        device.id,
                    ),
                )

    @staticmethod
    def _to_device(row: dict) -> Device:
        return Device(
            id=row["id"],
            nombre=row["nombre"],
            tipo=row["tipo"],
            perfil_hardware=row["perfil_hardware"],
            adaptador=row["adaptador"],
            ubicacion=row["ubicacion"],
            habilitado=row["habilitado"],
            estado=ConnectionState(row["estado"]),
        )


class PostgresDeviceStateEventRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, event: DeviceStateEvent) -> None:
        with psycopg.connect(self._dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO device_state_events "
                    "(device_id, estado_anterior, estado_nuevo, ocurrido_en) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        event.device_id,
                        event.estado_anterior.value,
                        event.estado_nuevo.value,
                        event.ocurrido_en,
                    ),
                )

    def list_for_device(self, device_id: str) -> list[DeviceStateEvent]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT device_id, estado_anterior, estado_nuevo, ocurrido_en "
                    "FROM device_state_events WHERE device_id = %s "
                    "ORDER BY ocurrido_en, id",
                    (device_id,),
                )
                rows = cursor.fetchall()
        return [
            DeviceStateEvent(
                device_id=row["device_id"],
                estado_anterior=ConnectionState(row["estado_anterior"]),
                estado_nuevo=ConnectionState(row["estado_nuevo"]),
                ocurrido_en=row["ocurrido_en"],
            )
            for row in rows
        ]
