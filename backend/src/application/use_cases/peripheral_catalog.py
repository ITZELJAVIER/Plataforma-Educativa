from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from src.application.errors import ConflictError, ValidationError
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.peripheral_type import PeripheralType
from src.domain.ports.peripheral_type_repository import PeripheralTypeRepository
from src.domain.value_objects.peripheral_metadata import (
    BASE_PERIPHERAL_TYPES,
    InvalidPeripheralValueError,
    PeripheralCatalogError,
)


@dataclass(frozen=True)
class PeripheralTypeInput:
    tipo: str | None = None
    canales: list[str] | None = None
    sentido: str | None = None
    unidad: str | None = None
    rango: Mapping[str, Any] | None = None
    resolucion: Any = None
    frecuencia: Any = None


@dataclass(frozen=True)
class PeripheralCatalogService:
    types: PeripheralTypeRepository
    auth: UserAuthService

    def initialize_base_types(self) -> None:
        for tipo in BASE_PERIPHERAL_TYPES:
            if self.types.get(tipo) is None:
                self.types.add(PeripheralType(tipo=tipo))

    def list_types(self, token: str) -> list[PeripheralType]:
        self.auth.current_user(token)
        return self.types.list()

    def get_type(self, token: str, tipo: str) -> PeripheralType:
        self.auth.current_user(token)
        return self._require_type(tipo)

    def register_type(self, token: str, data: PeripheralTypeInput) -> PeripheralType:
        self.auth.require_admin(token)
        definition = self._build_definition(data)
        existing = self.types.get(definition.tipo)
        if existing is not None:
            if existing.sentido is not None:
                raise ConflictError("El tipo de periférico ya existe.")
            self.types.save(definition)
            return definition
        self.types.add(definition)
        return definition

    def update_type(
        self, token: str, tipo: str, data: PeripheralTypeInput
    ) -> PeripheralType:
        self.auth.require_admin(token)
        existing = self._require_type(tipo)
        definition = self._build_definition(
            PeripheralTypeInput(
                tipo=existing.tipo,
                canales=data.canales,
                sentido=data.sentido,
                unidad=data.unidad,
                rango=data.rango,
                resolucion=data.resolucion,
                frecuencia=data.frecuencia,
            )
        )
        self.types.save(definition)
        return definition

    def validate_value(self, token: str, tipo: str, valor: Any) -> PeripheralType:
        self.auth.current_user(token)
        definition = self._require_type(tipo)
        try:
            numero = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("El valor debe ser numérico.") from exc
        try:
            definition.validar_valor(numero)
        except InvalidPeripheralValueError as exc:
            raise ValidationError(str(exc)) from exc
        return definition

    def _require_type(self, tipo: str) -> PeripheralType:
        definition = self.types.get(tipo)
        if definition is None:
            raise ValidationError("El tipo de periférico no existe.")
        return definition

    def _build_definition(self, data: PeripheralTypeInput) -> PeripheralType:
        try:
            definition = PeripheralType.from_values(
                tipo=data.tipo,
                canales=data.canales,
                sentido=data.sentido,
                unidad=data.unidad,
                rango=data.rango,
                resolucion=data.resolucion,
                frecuencia=data.frecuencia,
            )
            definition.validate_definition()
            return definition
        except PeripheralCatalogError as exc:
            raise ValidationError(str(exc)) from exc
