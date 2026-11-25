from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.role import Role


@dataclass(frozen=True)
class UserView:
    """Representación pública de un usuario; nunca incluye credenciales."""

    id: str
    role: Role
    active: bool


@dataclass(frozen=True)
class User:
    id: str
    password_hash: str
    role: Role
    active: bool = True

    def public(self) -> UserView:
        return UserView(id=self.id, role=self.role, active=self.active)
