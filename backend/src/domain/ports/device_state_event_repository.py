from __future__ import annotations

from typing import Protocol

from src.domain.entities.device_state_event import DeviceStateEvent


class DeviceStateEventRepository(Protocol):
    def add(self, event: DeviceStateEvent) -> None: ...

    def list_for_device(self, device_id: str) -> list[DeviceStateEvent]: ...
