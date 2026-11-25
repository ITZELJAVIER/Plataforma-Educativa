from __future__ import annotations

import unittest

from src.adapters.outbound.device.envelope import SobreOpaco
from src.adapters.outbound.device.mqtt import MqttDeviceAdapter
from src.adapters.outbound.device.simulated import SimulatedDeviceAdapter
from src.adapters.outbound.device.transport import TransporteFalso
from src.domain.value_objects.connection_state import ConnectionState


class TransporteEspia(TransporteFalso):
    def __init__(self) -> None:
        super().__init__()
        self.publicados: list[SobreOpaco] = []

    def publicar(self, sobre: SobreOpaco) -> None:
        self.publicados.append(sobre)
        super().publicar(sobre)


class DeviceAdapterTests(unittest.TestCase):
    def _contrato(self, adaptador: object, transporte: TransporteEspia) -> None:
        adaptador.emitir_estado("disp-1", ConnectionState.CONECTADO)  # type: ignore[attr-defined]
        self.assertEqual(
            adaptador.connection_state("disp-1"),  # type: ignore[attr-defined]
            ConnectionState.CONECTADO,
        )

        adaptador.emitir_estado("disp-1", ConnectionState.DESCONECTADO)  # type: ignore[attr-defined]
        self.assertEqual(
            adaptador.connection_state("disp-1"),  # type: ignore[attr-defined]
            ConnectionState.DESCONECTADO,
        )
        self.assertIsNone(
            adaptador.connection_state("sin-reporte")  # type: ignore[attr-defined]
        )

        sobre = transporte.publicados[0]
        self.assertIsInstance(sobre, SobreOpaco)
        self.assertNotIsInstance(sobre, dict)
        self.assertEqual(set(vars(sobre)), {"contenido"})

    def test_simulado_cumple_el_mismo_contrato_que_mqtt(self) -> None:
        for nombre, fabrica in (
            ("simulado", SimulatedDeviceAdapter),
            ("mqtt", MqttDeviceAdapter),
        ):
            with self.subTest(adaptador=nombre):
                transporte = TransporteEspia()
                adaptador = fabrica(transporte)
                self.assertEqual(adaptador.name, nombre)
                self._contrato(adaptador, transporte)

    def test_simulado_publica_y_mqtt_consume_sobre_opaco(self) -> None:
        transporte = TransporteFalso()
        simulado = SimulatedDeviceAdapter(transporte)
        mqtt = MqttDeviceAdapter(transporte)

        simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)

        self.assertEqual(mqtt.connection_state("disp-1"), ConnectionState.CONECTADO)


if __name__ == "__main__":
    unittest.main()
