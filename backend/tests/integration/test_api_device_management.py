from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.domain.value_objects.connection_state import ConnectionState
from src.infrastructure.bootstrap.app import create_app
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_device_harness


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class DeviceManagementApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = build_device_harness()
        self.client = TestClient(
            create_app(
                service=self.h.auth.service,
                devices=self.h.service,
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

    def _registrar(self, device_id: str = "disp-1"):
        return self.client.post(
            "/api/v1/devices",
            headers=auth(self.admin),
            json={
                "id": device_id,
                "nombre": "LED de banco",
                "tipo": "LED",
                "perfil_hardware": "perfil-banco",
                "ubicacion": "Laboratorio",
            },
        )

    def test_registro_duplicado_y_listado(self) -> None:
        creado = self._registrar()
        self.assertEqual(creado.status_code, 201)
        self.assertEqual(creado.json()["estado"], "desconocido")

        duplicado = self._registrar()
        self.assertEqual(duplicado.status_code, 409)
        self.assertIn("ya existe", duplicado.json()["detail"])

        listado = self.client.get("/api/v1/devices", headers=auth(self.admin))
        self.assertEqual(listado.status_code, 200)
        self.assertEqual([item["id"] for item in listado.json()], ["disp-1"])

    def test_estado_y_eventos_con_adaptador_simulado(self) -> None:
        self._registrar()
        self.h.simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)

        consulta = self.client.get(
            "/api/v1/devices/disp-1", headers=auth(self.admin)
        )
        eventos = self.client.get(
            "/api/v1/devices/disp-1/events", headers=auth(self.admin)
        )

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["estado"], "conectado")
        self.assertEqual(eventos.status_code, 200)
        self.assertEqual(len(eventos.json()), 1)
        self.assertEqual(eventos.json()[0]["estado_anterior"], "desconocido")
        self.assertEqual(eventos.json()[0]["estado_nuevo"], "conectado")

    def test_roles_y_sesion(self) -> None:
        self._registrar()
        docente = self._crear_usuario("docente", "docente")
        estudiante = self._crear_usuario("estudiante", "estudiante")

        for token in (docente, estudiante):
            with self.subTest(token=token):
                self.assertEqual(
                    self.client.get(
                        "/api/v1/devices", headers=auth(token)
                    ).status_code,
                    200,
                )
                self.assertEqual(
                    self.client.post(
                        "/api/v1/devices",
                        headers=auth(token),
                        json={
                            "id": "otro",
                            "nombre": "LED",
                            "tipo": "LED",
                            "perfil_hardware": "perfil",
                        },
                    ).status_code,
                    403,
                )
                self.assertEqual(
                    self.client.patch(
                        "/api/v1/devices/disp-1",
                        headers=auth(token),
                        json={"nombre": "Cambio"},
                    ).status_code,
                    403,
                )
                self.assertEqual(
                    self.client.post(
                        "/api/v1/devices/disp-1/deactivate", headers=auth(token)
                    ).status_code,
                    403,
                )

        self.assertEqual(self.client.get("/api/v1/devices").status_code, 401)

    def test_identificador_inmutable_y_desactivacion(self) -> None:
        self._registrar()

        cambio_id = self.client.patch(
            "/api/v1/devices/disp-1",
            headers=auth(self.admin),
            json={"id": "otro"},
        )
        self.assertEqual(cambio_id.status_code, 400)
        self.assertIn("no puede modificarse", cambio_id.json()["detail"])

        desactivado = self.client.post(
            "/api/v1/devices/disp-1/deactivate", headers=auth(self.admin)
        )
        self.assertEqual(desactivado.status_code, 200)
        self.assertFalse(desactivado.json()["habilitado"])

        consulta = self.client.get(
            "/api/v1/devices/disp-1", headers=auth(self.admin)
        )
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["id"], "disp-1")

    def test_documentacion_de_rutas(self) -> None:
        with open("docs/device-management.md", encoding="utf-8") as handle:
            documentacion = handle.read()

        rutas = (
            "GET /api/v1/devices",
            "GET /api/v1/devices/{id}",
            "POST /api/v1/devices",
            "PATCH /api/v1/devices/{id}",
            "POST /api/v1/devices/{id}/deactivate",
            "GET /api/v1/devices/{id}/events",
        )
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                self.assertIn(ruta, documentacion)

        for campo in ("id", "nombre", "tipo", "perfil_hardware", "ubicacion", "habilitado", "adaptador", "estado"):
            with self.subTest(campo=campo):
                self.assertIn(campo, documentacion)


if __name__ == "__main__":
    unittest.main()
