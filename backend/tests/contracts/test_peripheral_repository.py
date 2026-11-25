from __future__ import annotations

import unittest

from src.adapters.outbound.persistence.in_memory import InMemoryPeripheralTypeRepository
from src.adapters.outbound.persistence.postgres import SCHEMA_PERIPHERAL_CATALOG
from src.domain.entities.peripheral_type import PeripheralType
from src.domain.value_objects.peripheral_metadata import Rango
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_catalog_harness


class PeripheralRepositoryTests(unittest.TestCase):
    def test_repositorio_en_memoria_guarda_actualiza_y_lista(self) -> None:
        repository = InMemoryPeripheralTypeRepository()
        definition = PeripheralType(tipo="LED", canales=("D0",), sentido="salida")

        repository.add(definition)

        self.assertEqual(repository.get("LED"), definition)
        self.assertEqual(repository.list(), [definition])

        actualizada = PeripheralType(tipo="LED", canales=("D1",), sentido="salida")
        repository.save(actualizada)

        self.assertEqual(repository.get("LED").canales, ("D1",))
        self.assertEqual(len(repository.list()), 1)

        with self.assertRaises(ValueError):
            repository.add(actualizada)

    def test_json_de_metadatos_roundtrip(self) -> None:
        definition = PeripheralType(
            tipo="sensor",
            canales=("A",),
            sentido="entrada",
            unidad="grados",
            rango=Rango(minimo=0, maximo=100),
            resolucion=1,
            frecuencia=None,
        )

        recovered = PeripheralType.from_dict(definition.to_dict())

        self.assertEqual(recovered, definition)
        self.assertIsNone(recovered.frecuencia)

    def test_inicializacion_de_tipos_base_es_idempotente(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        h.service.initialize_base_types()
        tipos = h.service.list_types(token)

        self.assertEqual(len(tipos), 7)
        self.assertEqual(len({definition.tipo for definition in tipos}), 7)

    def test_esquema_postgres_del_catalogo_no_referencia_dispositivos(self) -> None:
        self.assertIn("CREATE TABLE IF NOT EXISTS peripheral_types", SCHEMA_PERIPHERAL_CATALOG)
        self.assertIn("metadata JSONB NOT NULL", SCHEMA_PERIPHERAL_CATALOG)
        self.assertNotIn("device", SCHEMA_PERIPHERAL_CATALOG.lower())
        self.assertNotIn("dispositivo", SCHEMA_PERIPHERAL_CATALOG.lower())


if __name__ == "__main__":
    unittest.main()
