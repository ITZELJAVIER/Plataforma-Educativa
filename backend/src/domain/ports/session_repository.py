from __future__ import annotations

from typing import Protocol

from src.domain.entities.session import Session


class SessionRepository(Protocol):
    def add(self, session: Session) -> None: ...

    def get(self, token: str) -> Session | None: ...

    def save(self, session: Session) -> None: ...

    def invalidate_all_for_user(self, user_id: str) -> None: ...
