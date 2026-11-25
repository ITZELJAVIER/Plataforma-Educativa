from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.infrastructure.bootstrap.app import create_app
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_harness


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class UserAuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = build_harness()
        self.client = TestClient(create_app(service=self.harness.service))

    def test_login_y_lectura_del_usuario_actual(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        token = response.json()["token"]

        me = self.client.get("/api/v1/users/me", headers=auth(token))
        self.assertEqual(me.status_code, 200)
        body = me.json()
        self.assertEqual(body["id"], ADMIN_ID)
        self.assertEqual(body["role"], "administrador")
        self.assertTrue(body["active"])
        self.assertNotIn("password", body)
        self.assertNotIn("password_hash", body)
        self.assertNotIn(ADMIN_PASSWORD, me.text)

    def test_rechazo_generico_de_credenciales_invalidas_y_cuenta_desactivada(self) -> None:
        admin_token = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        ).json()["token"]
        self.client.post(
            "/api/v1/users",
            headers=auth(admin_token),
            json={"id": "usuario", "password": "clave-usuario", "roles": ["estudiante"]},
        )
        self.client.post("/api/v1/users/usuario/deactivate", headers=auth(admin_token))

        invalid = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": "incorrecta"}
        )
        unknown = self.client.post(
            "/api/v1/auth/login", json={"id": "no-existe", "password": ADMIN_PASSWORD}
        )
        inactive = self.client.post(
            "/api/v1/auth/login", json={"id": "usuario", "password": "clave-usuario"}
        )

        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(invalid.json()["detail"], unknown.json()["detail"])
        self.assertEqual(invalid.json()["detail"], inactive.json()["detail"])
        self.assertNotIn(ADMIN_PASSWORD, invalid.text + unknown.text + inactive.text)

    def test_recursos_protegidos_rechazan_peticion_sin_sesion(self) -> None:
        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, 401)
        self.assertIn("Credenciales", response.json()["detail"])

    def test_administrador_crea_y_lista_usuarios_pero_estudiante_no(self) -> None:
        admin_token = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        ).json()["token"]

        created = self.client.post(
            "/api/v1/users",
            headers=auth(admin_token),
            json={"id": "estudiante", "password": "clave-est", "roles": ["estudiante"]},
        )
        self.assertEqual(created.status_code, 201)

        listed = self.client.get("/api/v1/users", headers=auth(admin_token))
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 2)

        student_token = self.client.post(
            "/api/v1/auth/login", json={"id": "estudiante", "password": "clave-est"}
        ).json()["token"]
        forbidden_create = self.client.post(
            "/api/v1/users",
            headers=auth(student_token),
            json={"id": "otro", "password": "clave", "roles": ["docente"]},
        )
        forbidden_list = self.client.get("/api/v1/users", headers=auth(student_token))

        self.assertEqual(forbidden_create.status_code, 403)
        self.assertEqual(forbidden_list.status_code, 403)

    def test_creacion_sin_rol_y_con_dos_roles_se_rechaza(self) -> None:
        admin_token = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        ).json()["token"]

        empty = self.client.post(
            "/api/v1/users",
            headers=auth(admin_token),
            json={"id": "sin-rol", "password": "clave", "roles": []},
        )
        multiple = self.client.post(
            "/api/v1/users",
            headers=auth(admin_token),
            json={"id": "dos-roles", "password": "clave", "roles": ["docente", "estudiante"]},
        )

        self.assertEqual(empty.status_code, 400)
        self.assertIn("obligatorio", empty.json()["detail"])
        self.assertEqual(multiple.status_code, 400)

    def test_logout_invalida_la_credencial(self) -> None:
        token = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        ).json()["token"]

        logout = self.client.post("/api/v1/auth/logout", headers=auth(token))
        self.assertEqual(logout.status_code, 204)

        me = self.client.get("/api/v1/users/me", headers=auth(token))
        self.assertEqual(me.status_code, 401)

    def test_cambio_de_rol_y_desactivacion_estan_auditados(self) -> None:
        admin_token = self.client.post(
            "/api/v1/auth/login", json={"id": ADMIN_ID, "password": ADMIN_PASSWORD}
        ).json()["token"]
        self.client.post(
            "/api/v1/users",
            headers=auth(admin_token),
            json={"id": "usuario", "password": "clave-usuario", "roles": ["estudiante"]},
        )

        changed = self.client.patch(
            "/api/v1/users/usuario/role",
            headers=auth(admin_token),
            json={"roles": ["docente"]},
        )
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.json()["role"], "docente")

        user_token = self.client.post(
            "/api/v1/auth/login", json={"id": "usuario", "password": "clave-usuario"}
        ).json()["token"]
        deactivated = self.client.post(
            "/api/v1/users/usuario/deactivate", headers=auth(admin_token)
        )
        self.assertEqual(deactivated.status_code, 200)
        self.assertFalse(deactivated.json()["active"])

        me = self.client.get("/api/v1/users/me", headers=auth(user_token))
        self.assertEqual(me.status_code, 401)

        actions = [event.action for event in self.harness.audit.list()]
        self.assertIn("cambio_de_rol", actions)
        self.assertIn("desactivacion_usuario", actions)
        self.assertIn("fallo_autenticacion", actions)

    def test_documentacion_de_rutas_coincide_con_el_router(self) -> None:
        with open("docs/user-auth.md", encoding="utf-8") as handle:
            documentation = handle.read()

        expected = (
            "POST /api/v1/auth/login",
            "POST /api/v1/auth/logout",
            "GET /api/v1/users/me",
            "GET /api/v1/users",
            "POST /api/v1/users",
            "GET /api/v1/users/{user_id}",
            "PATCH /api/v1/users/{user_id}/role",
            "POST /api/v1/users/{user_id}/deactivate",
            "POST /api/v1/users/{user_id}/reactivate",
        )
        for route in expected:
            with self.subTest(route=route):
                self.assertIn(route, documentation)


if __name__ == "__main__":
    unittest.main()
