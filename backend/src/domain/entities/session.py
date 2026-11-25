from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class Session:
    token: str
    user_id: str
    expires_at: datetime
    revoked: bool = False

    def is_valid(self, now: datetime) -> bool:
        return not self.revoked and self.expires_at > now

    def revoke(self) -> "Session":
        return replace(self, revoked=True)
