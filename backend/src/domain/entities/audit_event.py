from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    resource: str
    occurred_at: datetime
