from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.adapters.outbound.persistence.in_memory import (
    InMemoryDeviceRepository,
    InMemoryDeviceStateEventRepository,
)
from src.adapters.outbound.persistence.postgres import SCHEMA_DEVICE_MANAGEMENT
from src.domain.entities.device import Device
from src.domain.entities.device_state_event import DeviceStateEvent
from src.domain.value_objects.connection_state import ConnectionState


class DeviceRepositoryTests(unittest.TestCase):
    def _dispositivo(self) -> Device:
        return Device(
            id="disp-1",
            nombre="LED",
            tipo="LED",
            perfil_hardware="perfil",
            adaptador="simulado",
        )

    def test_repositorio_en_memoria_guarda_actualiza_y_lista(self) -> None:
        repository = InMemoryDeviceRepository()
        device = self._dispositivo()
        repository.add(device)

        self.assertEqual(repository.get("disp-1"), device)
        self.assertEqual(repository.list(), [device])

        actualizado = Device(
            id="disp-1",
            nombre="LED principal",
            tipo="LED",
            perfil_hardware="perfil",
            adaptador="simulado",
            ubicacion="Aula 204",
        )
        repository.save(actualizado)

        self.assertEqual(repository.get("disp-1").nombre, "LED principal")
        self.assertEqual(repository.get("disp-1").ubicacion, "Aula 204")
        self.assertEqual(len(repository.list()), 1)

        with self.assertRaises(ValueError):
            repository.add(actualizado)

    def test_eventos_se_listan_por_dispositivo(self) -> None:
        repository = InMemoryDeviceStateEventRepository()
        ahora = DeviceStateEvent(
            device_id="disp-1",
            estado_anterior=ConnectionState.DESCONOCIDO,
            estado_nuevo=ConnectionState.CONECTADO,
            ocurrido_en=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        repository.add(ahora)

        self.assertEqual(repository.list_for_device("disp-1"), [ahora])
        self.assertEqual(repository.list_for_device("otro"), [])

    def test_esquema_postgres_de_dispositivos_no_fija_transporte(self) -> None:
        self.assertIn("CREATE TABLE IF NOT EXISTS devices", SCHEMA_DEVICE_MANAGEMENT)
        self.assertIn(
            "CREATE TABLE IF NOT EXISTS device_state_events", SCHEMA_DEVICE_MANAGEMENT
        )
        for prohibido in ("mqtt", "topic", "broker", "qos", "websocket"):
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, SCHEMA_DEVICE_MANAGEMENT.lower())


if __name__ == "__main__":
    unittest.main()
