from __future__ import annotations

from typing import Protocol

from src.domain.entities.peripheral_type import PeripheralType


class PeripheralTypeRepository(Protocol):
    def add(self, definition: PeripheralType) -> None: ...

    def get(self, tipo: str) -> PeripheralType | None: ...

    def list(self) -> list[PeripheralType]: ...

    def save(self, definition: PeripheralType) -> None: ...
