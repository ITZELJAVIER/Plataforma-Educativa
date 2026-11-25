from __future__ import annotations

from enum import Enum


class ConnectionState(str, Enum):
    """Estados de conexión definidos por `device-management`."""

    CONECTADO = "conectado"
    DESCONECTADO = "desconectado"
    DESCONOCIDO = "desconocido"
