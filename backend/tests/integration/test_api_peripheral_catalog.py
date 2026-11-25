from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.domain.value_objects.peripheral_metadata import BASE_PERIPHERAL_TYPES
from src.infrastructure.bootstrap.app import create_app
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_catalog_harness


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class PeripheralCatalogApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = build_catalog_harness(
            tokens=["admin-token", "docente-token", "estudiante-token"]
        )
        self.client = TestClient(
            create_app(
                service=self.harness.auth.service,
                catalog=self.harness.service,
            )
        )
        self.admin = self.client.post(
            "/api/v1/auth/login",
            json={"id": ADMIN_ID, "password": ADMIN_PASSWORD},
        ).json()["token"]

    def _crear_usuario(self, ident: str, rol: str) -> str:
        self.client.post(
            "/api/v1/users",
            headers=auth(self.admin),
            json={"id": ident, "password": "clave-solo-prueba", "roles": [rol]},
        )
        return self.client.post(
            "/api/v1/auth/login",
            json={"id": ident, "password": "clave-solo-prueba"},
        ).json()["token"]

    def test_catalogo_devuelve_siete_tipos_base(self) -> None:
        response = self.client.get(
            "/api/v1/peripherals/types", headers=auth(self.admin)
        )

        self.assertEqual(response.status_code, 200)
        tipos = {item["tipo"] for item in response.json()}
        self.assertEqual(tipos, set(BASE_PERIPHERAL_TYPES))
        self.assertTrue(all(item["frecuencia"] is None for item in response.json()))

    def test_admin_registra_tipo_nuevo_y_docente_solo_lee(self) -> None:
        docente = self._crear_usuario("docente", "docente")

        creado = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(self.admin),
            json={
                "tipo": "lector optico",
                "canales": ["CAN-1"],
                "sentido": "entrada",
                "unidad": "lux",
                "rango": {"minimo": 0, "maximo": 500},
                "resolucion": 5,
            },
        )
        self.assertEqual(creado.status_code, 201)
        self.assertEqual(creado.json()["tipo"], "lector optico")

        lectura = self.client.get(
            "/api/v1/peripherals/types", headers=auth(docente)
        )
        self.assertEqual(lectura.status_code, 200)
        self.assertIn("lector optico", {item["tipo"] for item in lectura.json()})

        intento = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(docente),
            json={"tipo": "no permitido", "sentido": "salida", "canales": ["A"]},
        )
        self.assertEqual(intento.status_code, 403)

    def test_registro_sin_tipo_y_sensor_incompleto_se_rechazan(self) -> None:
        sin_tipo = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(self.admin),
            json={"sentido": "entrada", "canales": ["A"]},
        )
        sensor = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(self.admin),
            json={"tipo": "sensor", "sentido": "entrada", "canales": ["A"]},
        )

        self.assertEqual(sin_tipo.status_code, 400)
        self.assertEqual(sin_tipo.json()["detail"], "El tipo es obligatorio.")
        self.assertEqual(sensor.status_code, 400)
        self.assertIn("unidad, rango y resolución", sensor.json()["detail"])

    def test_canales_duplicados_se_rechazan(self) -> None:
        response = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(self.admin),
            json={"tipo": "duplicado", "sentido": "entrada", "canales": ["A", "A"]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("únicos", response.json()["detail"])

    def test_validacion_de_valor_por_rango_y_resolucion(self) -> None:
        registrado = self.client.post(
            "/api/v1/peripherals/types",
            headers=auth(self.admin),
            json={
                "tipo": "sensor api",
                "canales": ["A"],
                "sentido": "entrada",
                "unidad": "voltios",
                "rango": {"minimo": 0, "maximo": 10},
                "resolucion": 2,
            },
        )
        self.assertEqual(registrado.status_code, 201)

        fuera = self.client.post(
            "/api/v1/peripherals/types/sensor%20api/validate-value",
            headers=auth(self.admin),
            json={"valor": 11},
        )
        resolucion = self.client.post(
            "/api/v1/peripherals/types/sensor%20api/validate-value",
            headers=auth(self.admin),
            json={"valor": 3},
        )
        correcto = self.client.post(
            "/api/v1/peripherals/types/sensor%20api/validate-value",
            headers=auth(self.admin),
            json={"valor": 4},
        )

        self.assertEqual(fuera.status_code, 400)
        self.assertIn("0", fuera.json()["detail"])
        self.assertIn("10", fuera.json()["detail"])
        self.assertEqual(resolucion.status_code, 400)
        self.assertIn("resolución admitida es 2", resolucion.json()["detail"])
        self.assertEqual(correcto.status_code, 200)
        self.assertTrue(correcto.json()["valido"])

    def test_sin_sesion_y_estudiante_no_pueden_modificar(self) -> None:
        sin_sesion = self.client.get("/api/v1/peripherals/types")
        estudiante = self._crear_usuario("estudiante", "estudiante")

        intento = self.client.patch(
            "/api/v1/peripherals/types/LED",
            headers=auth(estudiante),
            json={"sentido": "salida", "canales": ["A"]},
        )

        self.assertEqual(sin_sesion.status_code, 401)
        self.assertEqual(intento.status_code, 403)

    def test_administrador_modifica_metadatos(self) -> None:
        response = self.client.patch(
            "/api/v1/peripherals/types/LED",
            headers=auth(self.admin),
            json={"sentido": "salida", "canales": ["D0"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["canales"], ["D0"])
        self.assertEqual(response.json()["sentido"], "salida")
        self.assertIsNone(response.json()["frecuencia"])

    def test_tipo_inexistente_se_rechaza(self) -> None:
        response = self.client.get(
            "/api/v1/peripherals/types/no-existe", headers=auth(self.admin)
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("no existe", response.json()["detail"])

    def test_documentacion_de_rutas_y_metadatos(self) -> None:
        with open("docs/peripheral-catalog.md", encoding="utf-8") as handle:
            documentacion = handle.read()

        rutas = (
            "GET /api/v1/peripherals/types",
            "GET /api/v1/peripherals/types/{tipo}",
            "POST /api/v1/peripherals/types",
            "PATCH /api/v1/peripherals/types/{tipo}",
            "POST /api/v1/peripherals/types/{tipo}/validate-value",
        )
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                self.assertIn(ruta, documentacion)

        for tipo in BASE_PERIPHERAL_TYPES:
            with self.subTest(tipo=tipo):
                self.assertIn(f"`{tipo}`", documentacion)

        for campo in ("tipo", "canales", "sentido", "unidad", "rango", "resolucion", "frecuencia"):
            with self.subTest(campo=campo):
                self.assertIn(campo, documentacion)


if __name__ == "__main__":
    unittest.main()
