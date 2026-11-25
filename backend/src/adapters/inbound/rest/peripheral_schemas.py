from __future__ import annotations

from pydantic import BaseModel


class RangoRequest(BaseModel):
    minimo: float
    maximo: float


class PeripheralTypeCreateRequest(BaseModel):
    tipo: str | None = None
    canales: list[str] = []
    sentido: str | None = None
    unidad: str | None = None
    rango: RangoRequest | None = None
    resolucion: float | None = None
    frecuencia: float | None = None


class PeripheralMetadataUpdateRequest(BaseModel):
    canales: list[str] = []
    sentido: str | None = None
    unidad: str | None = None
    rango: RangoRequest | None = None
    resolucion: float | None = None
    frecuencia: float | None = None


class ValueRequest(BaseModel):
    valor: float


class RangoResponse(BaseModel):
    minimo: float
    maximo: float


class PeripheralTypeResponse(BaseModel):
    tipo: str
    canales: list[str]
    sentido: str | None = None
    unidad: str | None = None
    rango: RangoResponse | None = None
    resolucion: float | None = None
    frecuencia: float | None = None


class ValueValidationResponse(BaseModel):
    valido: bool
    tipo: str
