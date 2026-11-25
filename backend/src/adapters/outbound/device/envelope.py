from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.connection_state import ConnectionState


@dataclass(frozen=True)
class SenalPrueba:
    """Señal interna de pruebas. No representa campos del Envelope EP1."""

    dispositivo_id: str
    estado: ConnectionState


@dataclass(frozen=True)
class SobreOpaco:
    """Contenedor opaco intercambiado por el transporte falso.

    No define, valida ni fija los campos concretos del Envelope EP1. Es solo el
    límite opaco autorizado para las pruebas de `6.3` y `6.4`.
    """

    contenido: object
