from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DeviceCreateRequest(BaseModel):
    id: str
    nombre: str
    tipo: str
    perfil_hardware: str
    ubicacion: str | None = None
    adaptador: str | None = None


class DeviceConfigRequest(BaseModel):
    id: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    perfil_hardware: str | None = None
    ubicacion: str | None = None
    habilitado: bool | None = None
    adaptador: str | None = None


class DeviceResponse(BaseModel):
    id: str
    nombre: str
    tipo: str
    perfil_hardware: str
    ubicacion: str | None = None
    habilitado: bool
    adaptador: str
    estado: str


class DeviceStateEventResponse(BaseModel):
    device_id: str
    estado_anterior: str
    estado_nuevo: str
    ocurrido_en: datetime
