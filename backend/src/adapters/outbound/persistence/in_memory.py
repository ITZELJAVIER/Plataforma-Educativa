from __future__ import annotations

from dataclasses import replace

from src.domain.entities.audit_event import AuditEvent
from src.domain.entities.device import Device
from src.domain.entities.device_state_event import DeviceStateEvent
from src.domain.entities.peripheral_type import PeripheralType
from src.domain.entities.session import Session
from src.domain.entities.user import User


class InMemoryUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self._users = {user.id: user for user in users or []}

    def add(self, user: User) -> None:
        if user.id in self._users:
            raise ValueError("El usuario ya existe.")
        self._users[user.id] = user

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def list(self) -> list[User]:
        return list(self._users.values())

    def save(self, user: User) -> None:
        self._users[user.id] = user


class InMemorySessionRepository:
    def __init__(self, sessions: list[Session] | None = None) -> None:
        self._sessions = {session.token: session for session in sessions or []}

    def add(self, session: Session) -> None:
        self._sessions[session.token] = session

    def get(self, token: str) -> Session | None:
        return self._sessions.get(token)

    def save(self, session: Session) -> None:
        self._sessions[session.token] = session

    def invalidate_all_for_user(self, user_id: str) -> None:
        for token, session in list(self._sessions.items()):
            if session.user_id == user_id and not session.revoked:
                self._sessions[token] = replace(session, revoked=True)


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def add(self, event: AuditEvent) -> None:
        self._events.append(event)

    def list(self) -> list[AuditEvent]:
        return list(self._events)


class InMemoryPeripheralTypeRepository:
    def __init__(self, definitions: list[PeripheralType] | None = None) -> None:
        self._types = {definition.tipo: definition for definition in definitions or []}

    def add(self, definition: PeripheralType) -> None:
        if definition.tipo in self._types:
            raise ValueError("El tipo de periférico ya existe.")
        self._types[definition.tipo] = definition

    def get(self, tipo: str) -> PeripheralType | None:
        return self._types.get(tipo.strip())

    def list(self) -> list[PeripheralType]:
        return list(self._types.values())

    def save(self, definition: PeripheralType) -> None:
        self._types[definition.tipo] = definition


class InMemoryDeviceRepository:
    def __init__(self, devices: list[Device] | None = None) -> None:
        self._devices = {device.id: device for device in devices or []}

    def add(self, device: Device) -> None:
        if device.id in self._devices:
            raise ValueError("El dispositivo ya existe.")
        self._devices[device.id] = device

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def list(self) -> list[Device]:
        return list(self._devices.values())

    def save(self, device: Device) -> None:
        self._devices[device.id] = device


class InMemoryDeviceStateEventRepository:
    def __init__(self, events: list[DeviceStateEvent] | None = None) -> None:
        self._events = list(events or [])

    def add(self, event: DeviceStateEvent) -> None:
        self._events.append(event)

    def list_for_device(self, device_id: str) -> list[DeviceStateEvent]:
        return [event for event in self._events if event.device_id == device_id]
