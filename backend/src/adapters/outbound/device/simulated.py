from __future__ import annotations

from dataclasses import dataclass, field

from src.adapters.outbound.device.envelope import SenalPrueba, SobreOpaco
from src.adapters.outbound.device.transport import TransporteFalso
from src.domain.value_objects.connection_state import ConnectionState


@dataclass
class SimulatedDeviceAdapter:
    """Primer adaptador del puerto: sin hardware FPGA.

    Emite mensajes conformes al contenedor opaco autorizado y expone el mismo
    contrato que el adaptador real.
    """

    transporte: TransporteFalso
    name: str = "simulado"
    _estados: dict[str, ConnectionState] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._estados = {}

    def emitir_estado(self, device_id: str, estado: ConnectionState) -> None:
        """Registra localmente y publica un sobre opaco para el transporte falso."""
        self._estados[device_id] = estado
        self.transporte.publicar(
            SobreOpaco(SenalPrueba(dispositivo_id=device_id, estado=estado))
        )

    def connection_state(self, device_id: str) -> ConnectionState | None:
        return self._estados.get(device_id)
