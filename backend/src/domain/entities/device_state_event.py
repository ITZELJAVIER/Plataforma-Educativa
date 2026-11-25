from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.connection_state import ConnectionState


@dataclass(frozen=True)
class DeviceStateEvent:
    """Cambio de estado de conexión con instante del servidor."""

    device_id: str
    estado_anterior: ConnectionState
    estado_nuevo: ConnectionState
    ocurrido_en: datetime
