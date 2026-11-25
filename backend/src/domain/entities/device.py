from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.connection_state import ConnectionState


class InvalidDeviceError(ValueError):
    """Los datos declarados de una instancia de dispositivo no son válidos."""


@dataclass(frozen=True)
class DeviceView:
    """Representación pública de un dispositivo; no expone secretos del enlace."""

    id: str
    nombre: str
    tipo: str
    perfil_hardware: str
    ubicacion: str | None
    habilitado: bool
    adaptador: str
    estado: ConnectionState


@dataclass(frozen=True)
class Device:
    """Instancia registrada y supervisable, independiente del catálogo de tipos."""

    id: str
    nombre: str
    tipo: str
    perfil_hardware: str
    adaptador: str
    ubicacion: str | None = None
    habilitado: bool = True
    estado: ConnectionState = ConnectionState.DESCONOCIDO

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _texto_obligatorio(self.id, "El identificador"))
        object.__setattr__(self, "nombre", _texto_obligatorio(self.nombre, "El nombre"))
        object.__setattr__(self, "tipo", _texto_obligatorio(self.tipo, "El tipo"))
        object.__setattr__(
            self,
            "perfil_hardware",
            _texto_obligatorio(self.perfil_hardware, "El perfil de hardware"),
        )
        object.__setattr__(self, "adaptador", _texto_obligatorio(self.adaptador, "El adaptador"))
        if isinstance(self.ubicacion, str) and self.ubicacion.strip():
            object.__setattr__(self, "ubicacion", self.ubicacion.strip())
        else:
            object.__setattr__(self, "ubicacion", None)

    def public(self) -> DeviceView:
        return DeviceView(
            id=self.id,
            nombre=self.nombre,
            tipo=self.tipo,
            perfil_hardware=self.perfil_hardware,
            ubicacion=self.ubicacion,
            habilitado=self.habilitado,
            adaptador=self.adaptador,
            estado=self.estado,
        )


def _texto_obligatorio(valor: object, etiqueta: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise InvalidDeviceError(f"{etiqueta} es obligatorio.")
    return valor.strip()
