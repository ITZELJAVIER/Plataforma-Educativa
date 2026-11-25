from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


class PeripheralCatalogError(ValueError):
    """Error de dominio del catálogo de periféricos."""


class InvalidPeripheralMetadataError(PeripheralCatalogError):
    pass


class InvalidPeripheralValueError(PeripheralCatalogError):
    pass


BASE_PERIPHERAL_TYPES: tuple[str, ...] = (
    "LED",
    "pulsador",
    "entrada digital",
    "salida digital",
    "sensor",
    "motor con PWM",
    "pantalla",
)

SENSOR_TYPE = "sensor"


@dataclass(frozen=True)
class Rango:
    minimo: Decimal
    maximo: Decimal

    def __post_init__(self) -> None:
        if self.minimo > self.maximo:
            raise InvalidPeripheralMetadataError(
                "El mínimo del rango no puede ser mayor que el máximo."
            )

    def contiene(self, valor: Decimal) -> bool:
        return self.minimo <= valor <= self.maximo

    def mensaje(self) -> str:
        return f"El rango permitido es {self.minimo} a {self.maximo}."


def decimal_desde(valor: Any, nombre: str) -> Decimal | None:
    if valor is None:
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise InvalidPeripheralMetadataError(
            f"{nombre} debe ser un valor numérico."
        ) from exc
