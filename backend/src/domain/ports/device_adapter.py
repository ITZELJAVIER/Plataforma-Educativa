from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.connection_state import ConnectionState


class DeviceAdapter(Protocol):
    """Puerto de comunicación con dispositivos.

    El dominio solo consulta estados neutrales. No conoce MQTT, broker, tópicos,
    QoS, retención, TLS ni los campos concretos del Envelope EP1.
    """

    @property
    def name(self) -> str: ...

    def connection_state(self, device_id: str) -> ConnectionState | None: ...
