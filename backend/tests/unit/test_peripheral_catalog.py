from __future__ import annotations

import unittest
from dataclasses import asdict

from src.application.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from src.application.use_cases.peripheral_catalog import PeripheralTypeInput
from src.domain.value_objects.peripheral_metadata import BASE_PERIPHERAL_TYPES
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_catalog_harness


class PeripheralCatalogTests(unittest.TestCase):
    def test_catalogo_inicial_incluye_siete_tipos_base(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        tipos = {definition.tipo for definition in h.service.list_types(token)}

        self.assertEqual(tipos, set(BASE_PERIPHERAL_TYPES))
        self.assertEqual(len(BASE_PERIPHERAL_TYPES), 7)

    def test_registro_sin_tipo_se_rechaza(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        with self.assertRaises(ValidationError) as ctx:
            h.service.register_type(
                token,
                PeripheralTypeInput(sentido="lectura", canales=["A"]),
            )

        self.assertEqual(str(ctx.exception), "El tipo es obligatorio.")

    def test_sensor_requiere_unidad_rango_y_resolucion(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        with self.assertRaises(ValidationError) as ctx:
            h.service.register_type(
                token,
                PeripheralTypeInput(
                    tipo="sensor", sentido="entrada", canales=["A"]
                ),
            )

        self.assertIn("unidad, rango y resolución", str(ctx.exception))

        completa = h.service.register_type(
            token,
            PeripheralTypeInput(
                tipo="sensor",
                sentido="entrada",
                canales=["A"],
                unidad="grados Celsius",
                rango={"minimo": 0, "maximo": 100},
                resolucion=1,
            ),
        )
        self.assertEqual(completa.unidad, "grados Celsius")

    def test_canales_duplicados_se_rechazan(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        with self.assertRaises(ValidationError) as ctx:
            h.service.register_type(
                token,
                PeripheralTypeInput(
                    tipo="entrada multiple",
                    sentido="entrada",
                    canales=["A", "A"],
                ),
            )

        self.assertIn("únicos", str(ctx.exception))

    def test_valor_fuera_de_rango_informa_rango_permitido(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.register_type(
            token,
            PeripheralTypeInput(
                tipo="sensor rango",
                sentido="entrada",
                canales=["A"],
                unidad="voltios",
                rango={"minimo": 0, "maximo": 10},
                resolucion=1,
            ),
        )

        with self.assertRaises(ValidationError) as ctx:
            h.service.validate_value(token, "sensor rango", 11)

        self.assertIn("0", str(ctx.exception))
        self.assertIn("10", str(ctx.exception))

    def test_valor_no_multiplo_de_la_resolucion_informa_resolucion(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.register_type(
            token,
            PeripheralTypeInput(
                tipo="motor paso",
                sentido="salida",
                canales=["PWM"],
                rango={"minimo": 0, "maximo": 10},
                resolucion=2,
            ),
        )

        with self.assertRaises(ValidationError) as ctx:
            h.service.validate_value(token, "motor paso", 3)

        self.assertIn("resolución admitida es 2", str(ctx.exception))
        h.service.validate_value(token, "motor paso", 4)

    def test_no_se_asigna_frecuencia_predeterminada(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        led = h.service.get_type(token, "LED")

        self.assertIsNone(led.frecuencia)

        registrado = h.service.register_type(
            token,
            PeripheralTypeInput(tipo="sin frecuencia", sentido="salida", canales=["A"]),
        )
        self.assertIsNone(registrado.frecuencia)

    def test_frecuencia_solo_se_guarda_si_se_declara(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        registrado = h.service.register_type(
            token,
            PeripheralTypeInput(
                tipo="con frecuencia",
                sentido="entrada",
                canales=["A"],
                frecuencia=100,
            ),
        )

        self.assertEqual(registrado.frecuencia, 100)

    def test_tipo_nuevo_se_registra_por_metadatos(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

        nuevo = h.service.register_type(
            token,
            PeripheralTypeInput(
                tipo="lector optico",
                canales=["CAN-1", "CAN-2"],
                sentido="entrada",
                unidad="lux",
                rango={"minimo": 0, "maximo": 500},
                resolucion=5,
            ),
        )

        listados = {definition.tipo for definition in h.service.list_types(token)}
        self.assertIn("lector optico", listados)
        self.assertEqual(nuevo.unidad, "lux")
        self.assertEqual(nuevo.canales, ("CAN-1", "CAN-2"))

    def test_definicion_no_depende_de_dispositivos(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        definition = h.service.register_type(
            token,
            PeripheralTypeInput(tipo="definicion comun", sentido="salida", canales=["A"]),
        )

        campos = set(asdict(definition))
        self.assertFalse(any("dispositivo" in campo or "device" in campo for campo in campos))
        self.assertEqual(len(h.service.list_types(token)), 8)

    def test_tipo_duplicado_se_rechaza(self) -> None:
        h = build_catalog_harness()
        token = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        datos = PeripheralTypeInput(tipo="duplicado", sentido="salida", canales=["A"])
        h.service.register_type(token, datos)

        with self.assertRaises(ConflictError):
            h.service.register_type(token, datos)

    def test_administrador_modifica_y_los_tres_roles_consultan(self) -> None:
        h = build_catalog_harness(tokens=["admin-token", "doc-token", "student-token"])
        admin = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.auth.service.create_user(admin, "docente", "clave-docente", ["docente"])
        h.auth.service.create_user(admin, "estudiante", "clave-est", ["estudiante"])
        docente = h.auth.service.login("docente", "clave-docente")
        estudiante = h.auth.service.login("estudiante", "clave-est")

        for token in (admin, docente, estudiante):
            with self.subTest(token=token):
                self.assertEqual(len(h.service.list_types(token)), 7)

        with self.assertRaises(AuthorizationError):
            h.service.register_type(
                docente,
                PeripheralTypeInput(tipo="no permitido", sentido="salida", canales=["A"]),
            )
        with self.assertRaises(AuthorizationError):
            h.service.update_type(
                estudiante,
                "LED",
                PeripheralTypeInput(sentido="entrada", canales=["A"]),
            )

        actualizado = h.service.update_type(
            admin,
            "LED",
            PeripheralTypeInput(sentido="salida", canales=["D0"]),
        )
        self.assertEqual(actualizado.canales, ("D0",))

    def test_validacion_de_valor_esta_disponible_para_docente(self) -> None:
        h = build_catalog_harness(tokens=["admin-token", "doc-token"])
        admin = h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.auth.service.create_user(admin, "docente", "clave-docente", ["docente"])
        docente = h.auth.service.login("docente", "clave-docente")
        h.service.register_type(
            admin,
            PeripheralTypeInput(
                tipo="sensor docente",
                sentido="entrada",
                canales=["A"],
                unidad="m",
                rango={"minimo": 0, "maximo": 10},
                resolucion=2,
            ),
        )

        self.assertEqual(h.service.validate_value(docente, "sensor docente", 4).tipo, "sensor docente")

    def test_peticion_sin_sesion_valida_se_rechaza(self) -> None:
        h = build_catalog_harness()

        with self.assertRaises(AuthenticationError):
            h.service.list_types("token-inexistente")


if __name__ == "__main__":
    unittest.main()
