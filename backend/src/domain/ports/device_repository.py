from __future__ import annotations

from typing import Protocol

from src.domain.entities.device import Device


class DeviceRepository(Protocol):
    def add(self, device: Device) -> None: ...

    def get(self, device_id: str) -> Device | None: ...

    def list(self) -> list[Device]: ...

    def save(self, device: Device) -> None: ...
