from __future__ import annotations

from enum import Enum


class InvalidRoleError(ValueError):
    """El rol no cumple la asignación única definida en `user-auth`."""


class Role(str, Enum):
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"

    @classmethod
    def from_value(cls, value: str) -> "Role":
        try:
            return cls(value)
        except ValueError as exc:
            raise InvalidRoleError(f"Rol no soportado: {value}") from exc


def exactly_one_role(values: list[str]) -> Role:
    """Devuelve el rol cuando la lista contiene exactamente uno de los tres definidos."""
    if not values:
        raise InvalidRoleError("El rol es obligatorio")
    if len(values) != 1:
        raise InvalidRoleError("Debe asignarse exactamente un rol")
    return Role.from_value(values[0])
