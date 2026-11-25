from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.application.errors import ConflictError, ValidationError
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.audit_event import AuditEvent
from src.domain.entities.device import Device, DeviceView, InvalidDeviceError
from src.domain.entities.device_state_event import DeviceStateEvent
from src.domain.ports.audit_repository import AuditRepository
from src.domain.ports.clock import Clock
from src.domain.ports.device_adapter import DeviceAdapter
from src.domain.ports.device_repository import DeviceRepository
from src.domain.ports.device_state_event_repository import DeviceStateEventRepository
from src.domain.value_objects.connection_state import ConnectionState


@dataclass(frozen=True)
class DeviceInput:
    id: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    perfil_hardware: str | None = None
    ubicacion: str | None = None
    adaptador: str | None = None


@dataclass(frozen=True)
class DeviceConfigInput:
    id: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    perfil_hardware: str | None = None
    ubicacion: str | None = None
    habilitado: bool | None = None
    adaptador: str | None = None


@dataclass(frozen=True)
class DeviceManagementService:
    """Registro, configuración y estado observable de dispositivos."""

    devices: DeviceRepository
    events: DeviceStateEventRepository
    adapters: Mapping[str, DeviceAdapter]
    auth: UserAuthService
    audit: AuditRepository
    clock: Clock
    default_adapter: str = "simulado"

    def register_device(self, token: str, data: DeviceInput) -> DeviceView:
        actor = self.auth.require_admin(token)
        adaptador = self._adapter_name(data.adaptador or self.default_adapter)
        try:
            device = Device(
                id=_texto(data.id, "El identificador"),
                nombre=_texto(data.nombre, "El nombre"),
                tipo=_texto(data.tipo, "El tipo"),
                perfil_hardware=_texto(data.perfil_hardware, "El perfil de hardware"),
                adaptador=adaptador,
                ubicacion=data.ubicacion,
            )
        except InvalidDeviceError as exc:
            raise ValidationError(str(exc)) from exc

        if self.devices.get(device.id) is not None:
            raise ConflictError("El identificador del dispositivo ya existe.")

        self.devices.add(device)
        self._record(actor.id, "registro_dispositivo", device.id)
        return device.public()

    def list_devices(self, token: str) -> list[DeviceView]:
        self.auth.current_user(token)
        return [self._sync(device).public() for device in self.devices.list()]

    def get_device(self, token: str, device_id: str) -> DeviceView:
        self.auth.current_user(token)
        return self._sync(self._require_device(device_id)).public()

    def list_events(self, token: str, device_id: str) -> list[DeviceStateEvent]:
        self.auth.current_user(token)
        self._require_device(device_id)
        return self.events.list_for_device(device_id)

    def update_configuration(
        self, token: str, device_id: str, data: DeviceConfigInput
    ) -> DeviceView:
        actor = self.auth.require_admin(token)
        actual = self._require_device(device_id)

        if data.id is not None and data.id != actual.id:
            raise ValidationError("El identificador de un dispositivo no puede modificarse.")

        cambios: dict[str, object] = {}
        for campo in ("nombre", "tipo", "perfil_hardware", "ubicacion"):
            valor = getattr(data, campo)
            if valor is not None:
                cambios[campo] = _texto(valor, campo.replace("_", " ")) if campo != "ubicacion" else valor.strip() or None
        if data.habilitado is not None:
            cambios["habilitado"] = data.habilitado
        if data.adaptador is not None:
            cambios["adaptador"] = self._adapter_name(data.adaptador)

        try:
            actualizada = replace(actual, **cambios)
        except InvalidDeviceError as exc:
            raise ValidationError(str(exc)) from exc

        if actualizada.adaptador != actual.adaptador:
            actualizada = self._registrar_transicion(
                actualizada, ConnectionState.DESCONOCIDO
            )

        self.devices.save(actualizada)
        self._record(actor.id, "configuracion_dispositivo", device_id)
        return actualizada.public()

    def deactivate_device(self, token: str, device_id: str) -> DeviceView:
        actor = self.auth.require_admin(token)
        actual = self._require_device(device_id)
        actualizada = replace(actual, habilitado=False)

        if actual.estado is ConnectionState.CONECTADO:
            actualizada = self._registrar_transicion(
                actualizada, ConnectionState.DESCONECTADO
            )

        self.devices.save(actualizada)
        self._record(actor.id, "desactivacion_dispositivo", device_id)
        return actualizada.public()

    def _sync(self, device: Device) -> Device:
        """Deriva el estado observable del adaptador configurado."""
        if not device.habilitado:
            return device
        reportado = self._adapter_for(device).connection_state(device.id)
        nuevo = reportado if reportado is not None else ConnectionState.DESCONOCIDO
        if nuevo is device.estado:
            return device
        return self._registrar_transicion(device, nuevo)

    def _registrar_transicion(self, device: Device, nuevo: ConnectionState) -> Device:
        if nuevo is device.estado:
            return device
        self.events.add(
            DeviceStateEvent(
                device_id=device.id,
                estado_anterior=device.estado,
                estado_nuevo=nuevo,
                ocurrido_en=self.clock.now(),
            )
        )
        actualizada = replace(device, estado=nuevo)
        self.devices.save(actualizada)
        return actualizada

    def _require_device(self, device_id: str) -> Device:
        device = self.devices.get(device_id)
        if device is None:
            raise ValidationError("El dispositivo no existe.")
        return device

    def _adapter_for(self, device: Device) -> DeviceAdapter:
        adapter = self.adapters.get(device.adaptador)
        if adapter is None:
            raise ValidationError("El adaptador configurado no está disponible.")
        return adapter

    def _adapter_name(self, valor: str) -> str:
        nombre = _texto(valor, "El adaptador")
        if nombre not in self.adapters:
            raise ValidationError("El adaptador configurado no está disponible.")
        return nombre

    def _record(self, actor: str, action: str, device_id: str) -> None:
        self.audit.add(
            AuditEvent(
                actor=actor,
                action=action,
                resource=f"dispositivo:{device_id}",
                occurred_at=self.clock.now(),
            )
        )


def _texto(valor: object, etiqueta: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValidationError(f"{etiqueta} es obligatorio.")
    return valor.strip()
