from __future__ import annotations

from dataclasses import dataclass, field

from src.adapters.outbound.device.envelope import SenalPrueba, SobreOpaco
from src.adapters.outbound.device.transport import TransporteFalso
from src.domain.value_objects.connection_state import ConnectionState


@dataclass
class MqttDeviceAdapter:
    """Adaptador MQTT detrás del puerto de dispositivo.

    En esta etapa se programa contra el transporte falso autorizado. No fija
    producto broker, tópicos, QoS, retención, autenticación ni TLS; su
    verificación real contra un broker queda para las tareas `8.5` y `9.1`.
    """

    transporte: TransporteFalso
    name: str = "mqtt"
    _estados: dict[str, ConnectionState] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._estados = {}

    def emitir_estado(self, device_id: str, estado: ConnectionState) -> None:
        self.transporte.publicar(
            SobreOpaco(SenalPrueba(dispositivo_id=device_id, estado=estado))
        )

    def connection_state(self, device_id: str) -> ConnectionState | None:
        self._consumir()
        return self._estados.get(device_id)

    def _consumir(self) -> None:
        for sobre in self.transporte.drenar():
            contenido = sobre.contenido
            if isinstance(contenido, SenalPrueba):
                self._estados[contenido.dispositivo_id] = contenido.estado
