from __future__ import annotations

from src.adapters.outbound.device.envelope import SobreOpaco


class TransporteFalso:
    """Transporte en memoria para pruebas del puerto de dispositivo.

    No modela broker, tópicos, QoS, retención, autenticación ni TLS.
    """

    def __init__(self) -> None:
        self._mensajes: list[SobreOpaco] = []

    def publicar(self, sobre: SobreOpaco) -> None:
        self._mensajes.append(sobre)

    def drenar(self) -> list[SobreOpaco]:
        mensajes = list(self._mensajes)
        self._mensajes.clear()
        return mensajes
