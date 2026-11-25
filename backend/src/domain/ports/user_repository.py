from __future__ import annotations

from typing import Protocol

from src.domain.entities.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: str) -> User | None: ...

    def list(self) -> list[User]: ...

    def save(self, user: User) -> None: ...
