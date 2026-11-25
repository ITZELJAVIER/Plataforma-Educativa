from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from src.domain.value_objects.peripheral_metadata import (
    InvalidPeripheralMetadataError,
    InvalidPeripheralValueError,
    Rango,
    SENSOR_TYPE,
    decimal_desde,
)


@dataclass(frozen=True)
class PeripheralType:
    """Definición de catálogo; no conoce dispositivos concretos."""

    tipo: str
    canales: tuple[str, ...] = ()
    sentido: str | None = None
    unidad: str | None = None
    rango: Rango | None = None
    resolucion: Decimal | None = None
    frecuencia: Decimal | None = None

    def __post_init__(self) -> None:
        tipo = self.tipo.strip() if isinstance(self.tipo, str) else ""
        if not tipo:
            raise InvalidPeripheralMetadataError("El tipo es obligatorio.")

        canales = tuple(
            canal.strip() for canal in self.canales if isinstance(canal, str) and canal.strip()
        )
        if len(set(canales)) != len(canales):
            raise InvalidPeripheralMetadataError(
                "Los canales deben ser únicos dentro del periférico."
            )

        object.__setattr__(self, "tipo", tipo)
        object.__setattr__(self, "canales", canales)
        object.__setattr__(
            self,
            "sentido",
            self.sentido.strip() if isinstance(self.sentido, str) and self.sentido.strip() else None,
        )
        object.__setattr__(
            self,
            "unidad",
            self.unidad.strip() if isinstance(self.unidad, str) and self.unidad.strip() else None,
        )

    @classmethod
    def from_values(
        cls,
        *,
        tipo: str | None,
        canales: list[str] | None = None,
        sentido: str | None = None,
        unidad: str | None = None,
        rango: Mapping[str, Any] | Rango | None = None,
        resolucion: Any = None,
        frecuencia: Any = None,
    ) -> "PeripheralType":
        rango_obj: Rango | None = None
        if isinstance(rango, Rango):
            rango_obj = rango
        elif rango is not None:
            if not isinstance(rango, Mapping) or "minimo" not in rango or "maximo" not in rango:
                raise InvalidPeripheralMetadataError(
                    "El rango debe declarar mínimo y máximo."
                )
            minimo = decimal_desde(rango["minimo"], "El mínimo del rango")
            maximo = decimal_desde(rango["maximo"], "El máximo del rango")
            if minimo is None or maximo is None:
                raise InvalidPeripheralMetadataError(
                    "El rango debe declarar mínimo y máximo."
                )
            rango_obj = Rango(minimo=minimo, maximo=maximo)

        return cls(
            tipo=tipo or "",
            canales=tuple(canales or ()),
            sentido=sentido,
            unidad=unidad,
            rango=rango_obj,
            resolucion=decimal_desde(resolucion, "La resolución"),
            frecuencia=decimal_desde(frecuencia, "La frecuencia"),
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PeripheralType":
        return cls.from_values(
            tipo=data.get("tipo"),
            canales=data.get("canales"),
            sentido=data.get("sentido"),
            unidad=data.get("unidad"),
            rango=data.get("rango"),
            resolucion=data.get("resolucion"),
            frecuencia=data.get("frecuencia"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tipo": self.tipo,
            "canales": list(self.canales),
            "sentido": self.sentido,
            "unidad": self.unidad,
            "rango": (
                None
                if self.rango is None
                else {"minimo": float(self.rango.minimo), "maximo": float(self.rango.maximo)}
            ),
            "resolucion": None if self.resolucion is None else float(self.resolucion),
            "frecuencia": None if self.frecuencia is None else float(self.frecuencia),
        }

    def validate_definition(self) -> None:
        """Valida la definición completa registrada por un administrador."""
        if self.sentido is None:
            raise InvalidPeripheralMetadataError("El sentido de operación es obligatorio.")
        if self.tipo == SENSOR_TYPE and (
            self.unidad is None or self.rango is None or self.resolucion is None
        ):
            raise InvalidPeripheralMetadataError(
                "Un sensor requiere unidad, rango y resolución."
            )
        if self.resolucion is not None and self.resolucion <= 0:
            raise InvalidPeripheralMetadataError(
                "La resolución debe ser mayor que cero."
            )

    def validar_valor(self, valor: Decimal) -> None:
        if self.rango is not None and not self.rango.contiene(valor):
            raise InvalidPeripheralValueError(
                f"Valor fuera de rango. {self.rango.mensaje()}"
            )
        if self.resolucion is not None:
            if self.resolucion <= 0:
                raise InvalidPeripheralValueError(
                    "La resolución declarada debe ser mayor que cero."
                )
            if valor % self.resolucion != 0:
                raise InvalidPeripheralValueError(
                    "Valor incompatible con la resolución. "
                    f"La resolución admitida es {self.resolucion}."
                )
