from __future__ import annotations

import json
import logging
import unittest
import uuid

from fastapi.testclient import TestClient

from src.infrastructure.bootstrap.app import create_app
from src.infrastructure.logging.config import JsonFormatter
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_harness


class CapturadorJson(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.eventos: list[dict[str, object]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.eventos.append(json.loads(JsonFormatter().format(record)))


class ApiErrorLoggingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = build_harness()
        self.client = TestClient(
            create_app(service=self.harness.service),
            raise_server_exceptions=False,
        )
        self.capturador = CapturadorJson()
        self.raiz = logging.getLogger()
        self.nivel_anterior = self.raiz.level
        self.raiz.setLevel(logging.DEBUG)
        self.raiz.addHandler(self.capturador)

    def tearDown(self) -> None:
        self.raiz.removeHandler(self.capturador)
        self.raiz.setLevel(self.nivel_anterior)
        self.client.close()

    def _eventos(self, mensaje: str) -> list[dict[str, object]]:
        return [evento for evento in self.capturador.eventos if evento["message"] == mensaje]

    def test_error_http_produce_un_registro_y_respuesta_segura(self) -> None:
        respuesta = self.client.get("/api/v1/users/me")

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json(), {"detail": "Credenciales no válidas."})
        self.assertNotIn("Traceback", respuesta.text)

        eventos = self._eventos("http_error")
        self.assertEqual(len(eventos), 1)
        contexto = eventos[0]["context"]
        self.assertEqual(contexto["status_code"], 401)
        self.assertEqual(contexto["method"], "GET")
        self.assertEqual(contexto["path"], "/api/v1/users/me")
        self.assertEqual(contexto["exception_type"], "HTTPException")
        self.assertIsNotNone(contexto["request_id"])
        self.assertNotIn("Traceback", json.dumps(eventos))

    def test_login_fallido_no_registra_la_contrasena(self) -> None:
        secreto = "clave-super-secreta-no-registrar"

        respuesta = self.client.post(
            "/api/v1/auth/login",
            json={"id": "admin-prueba", "password": secreto},
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(len(self._eventos("http_error")), 1)
        self.assertNotIn(secreto, respuesta.text)
        self.assertNotIn(secreto, json.dumps(self.capturador.eventos))

    def test_error_validacion_no_registra_valores_del_payload(self) -> None:
        respuesta = self.client.post(
            "/api/v1/auth/login",
            json={"id": "admin-prueba", "password": 123456789},
        )

        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(len(self._eventos("request_validation_error")), 1)
        self.assertNotIn("123456789", json.dumps(self.capturador.eventos))
        self.assertEqual(
            respuesta.json()["detail"][0]["type"], "string_type"
        )

    def test_excepcion_no_controlada_produce_un_registro_y_respuesta_por_defecto(
        self,
    ) -> None:
        secreto = "secreto-interno-no-registrar"

        async def explotar() -> None:
            raise RuntimeError(secreto)

        self.client.app.add_api_route("/_prueba/error", explotar, methods=["GET"])
        respuesta = self.client.get("/_prueba/error")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(respuesta.text, "Internal Server Error")
        self.assertNotIn("Traceback", respuesta.text)

        eventos = self._eventos("unhandled_exception")
        self.assertEqual(len(eventos), 1)
        contexto = eventos[0]["context"]
        self.assertEqual(contexto["status_code"], 500)
        self.assertEqual(contexto["exception_type"], "RuntimeError")
        self.assertNotIn(secreto, json.dumps(self.capturador.eventos))

    def test_respuesta_correcta_registra_solo_un_evento_de_peticion(self) -> None:
        token = self.client.post(
            "/api/v1/auth/login",
            json={"id": ADMIN_ID, "password": ADMIN_PASSWORD},
        ).json()["token"]
        self.capturador.eventos.clear()

        respuesta = self.client.get(
            "/api/v1/peripherals/types",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(self._eventos("request_completed")), 1)
        self.assertEqual(self._eventos("http_error"), [])

    def test_i1_error_controlado_sin_duplicados(self) -> None:
        respuesta = self.client.get("/api/v1/users/me")

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(len(self._eventos("http_error")), 1)
        self.assertEqual(self._eventos("unhandled_exception"), [])
        self.assertEqual(self._eventos("request_completed"), [])

    def test_i2_request_id_invalido_se_sustituye_y_se_devuelve(self) -> None:
        token = self.client.post(
            "/api/v1/auth/login",
            json={"id": ADMIN_ID, "password": ADMIN_PASSWORD},
        ).json()["token"]
        self.capturador.eventos.clear()

        respuesta = self.client.get(
            "/api/v1/peripherals/types",
            headers={
                "Authorization": f"Bearer {token}",
                "x-request-id": "id con espacio",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        eventos = self._eventos("request_completed")
        self.assertEqual(len(eventos), 1)
        request_id = eventos[0]["context"]["request_id"]
        self.assertNotEqual(request_id, "id con espacio")
        uuid.UUID(request_id)
        self.assertEqual(respuesta.headers["x-request-id"], request_id)

    def test_i2b_request_id_valido_se_conserva(self) -> None:
        token = self.client.post(
            "/api/v1/auth/login",
            json={"id": ADMIN_ID, "password": ADMIN_PASSWORD},
        ).json()["token"]
        self.capturador.eventos.clear()

        respuesta = self.client.get(
            "/api/v1/peripherals/types",
            headers={
                "Authorization": f"Bearer {token}",
                "x-request-id": "abc-123.XYZ",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        eventos = self._eventos("request_completed")
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["context"]["request_id"], "abc-123.XYZ")
        self.assertEqual(respuesta.headers["x-request-id"], "abc-123.XYZ")

    def test_i3_500_un_evento_traceback_seguro_y_sin_request_completed(self) -> None:
        secreto = "secreto-interno-500"

        async def explotar() -> None:
            raise RuntimeError(secreto)

        self.client.app.add_api_route(
            "/_prueba/error_trace", explotar, methods=["GET"]
        )
        respuesta = self.client.get("/_prueba/error_trace")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(respuesta.text, "Internal Server Error")
        self.assertEqual(len(self._eventos("unhandled_exception")), 1)
        self.assertEqual(self._eventos("request_completed"), [])
        self.assertNotIn(secreto, json.dumps(self.capturador.eventos))
        traza = self._eventos("unhandled_exception")[0].get("traceback")
        self.assertIsNotNone(traza)
        self.assertEqual(traza["tipo"], "RuntimeError")
        self.assertTrue(traza["frames"])

    def test_cors1_preflight_incluye_x_request_id(self) -> None:
        respuesta = self.client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": (
                    "authorization, content-type, x-request-id"
                ),
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        permitidos = {
            h.strip().lower()
            for h in respuesta.headers["access-control-allow-headers"].split(",")
        }
        self.assertTrue(
            {"authorization", "content-type", "x-request-id"} <= permitidos
        )
        self.assertEqual(
            respuesta.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )
        self.assertEqual(
            respuesta.headers["access-control-allow-methods"], "GET, POST, PATCH"
        )
        self.assertEqual(respuesta.headers["access-control-max-age"], "600")
        self.assertNotIn("access-control-allow-credentials", respuesta.headers)
        self.assertIn("x-request-id", respuesta.headers)

    def test_cors2_respuesta_real_expone_x_request_id(self) -> None:
        token = self.client.post(
            "/api/v1/auth/login",
            json={"id": ADMIN_ID, "password": ADMIN_PASSWORD},
        ).json()["token"]
        self.capturador.eventos.clear()

        respuesta = self.client.get(
            "/api/v1/peripherals/types",
            headers={
                "Authorization": f"Bearer {token}",
                "Origin": "http://localhost:5173",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.headers["access-control-expose-headers"], "X-Request-ID"
        )
        self.assertEqual(
            respuesta.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )
        self.assertEqual(respuesta.headers["content-type"], "application/json")
        self.assertIn("content-length", respuesta.headers)
        eventos = self._eventos("request_completed")
        self.assertEqual(len(eventos), 1)
        self.assertEqual(
            respuesta.headers["x-request-id"], eventos[0]["context"]["request_id"]
        )

    def test_cors3_respuesta_de_error_conserva_cuerpo_y_exposicion(self) -> None:
        respuesta = self.client.get(
            "/api/v1/users/me", headers={"Origin": "http://localhost:5173"}
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json(), {"detail": "Credenciales no válidas."})
        self.assertEqual(
            respuesta.headers["access-control-expose-headers"], "X-Request-ID"
        )
        self.assertEqual(len(self._eventos("http_error")), 1)


if __name__ == "__main__":
    unittest.main()
