from __future__ import annotations

from typing import Protocol

from src.domain.entities.audit_event import AuditEvent


class AuditRepository(Protocol):
    def add(self, event: AuditEvent) -> None: ...

    def list(self) -> list[AuditEvent]: ...
