from __future__ import annotations

import unittest
from dataclasses import asdict

from src.application.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from src.domain.value_objects.role import Role
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_harness


class UserAuthServiceTests(unittest.TestCase):
    def test_inicio_de_sesion_correcto_registra_acceso(self) -> None:
        h = build_harness(tokens=["token-admin"])

        token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)

        self.assertEqual(token, "token-admin")
        self.assertIsNotNone(h.sessions.get(token))
        events = h.audit.list()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].action, "inicio_de_sesion")
        self.assertEqual(events[0].actor, ADMIN_ID)
        self.assertEqual(events[0].resource, f"usuario:{ADMIN_ID}")
        self.assertIsNotNone(events[0].occurred_at)

    def test_credenciales_invalidas_y_cuentada_desactivada_usan_mensaje_generico(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.create_user(admin_token, "usuario", "clave-usuario", ["estudiante"])
        h.service.deactivate_user(admin_token, "usuario")

        with self.assertRaises(AuthenticationError) as wrong_password:
            h.service.login(ADMIN_ID, "clave-incorrecta")
        with self.assertRaises(AuthenticationError) as unknown_user:
            h.service.login("no-existe", ADMIN_PASSWORD)
        with self.assertRaises(AuthenticationError) as inactive:
            h.service.login("usuario", "clave-usuario")

        self.assertEqual(
            str(wrong_password.exception), str(unknown_user.exception)
        )
        self.assertEqual(str(wrong_password.exception), str(inactive.exception))
        self.assertNotIn("existe", str(wrong_password.exception))

    def test_fallo_de_autenticacion_no_registra_la_contrasena(self) -> None:
        h = build_harness()
        presented = "secreto-presentado-solo-prueba"

        with self.assertRaises(AuthenticationError):
            h.service.login(ADMIN_ID, presented)

        self.assertNotIn(presented, repr(h.audit.list()))
        self.assertTrue(
            any(event.action == "fallo_autenticacion" for event in h.audit.list())
        )

    def test_cierre_de_sesion_invalida_la_credencial(self) -> None:
        h = build_harness(tokens=["token-admin"])

        token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.logout(token)

        with self.assertRaises(AuthenticationError):
            h.service.current_user(token)
        self.assertTrue(any(e.action == "cierre_de_sesion" for e in h.audit.list()))

    def test_sesion_expirada_es_rechazada(self) -> None:
        h = build_harness(ttl_seconds=10, tokens=["token-admin"])

        token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.clock.advance(11)

        with self.assertRaises(AuthenticationError):
            h.service.current_user(token)

    def test_desactivacion_invalida_sesiones_activas(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.create_user(admin_token, "usuario", "clave-usuario", ["docente"])
        user_token = h.service.login("usuario", "clave-usuario")

        h.service.deactivate_user(admin_token, "usuario")

        with self.assertRaises(AuthenticationError):
            h.service.current_user(user_token)
        with self.assertRaises(AuthenticationError):
            h.service.login("usuario", "clave-usuario")

        h.service.reactivate_user(admin_token, "usuario")
        self.assertIsNotNone(h.service.login("usuario", "clave-usuario"))

    def test_asignacion_unica_de_rol(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)

        with self.assertRaises(ValidationError) as empty:
            h.service.create_user(admin_token, "sin-rol", "clave", [])
        with self.assertRaises(ValidationError) as multiple:
            h.service.create_user(
                admin_token, "dos-roles", "clave", ["docente", "estudiante"]
            )

        self.assertIn("obligatorio", str(empty.exception))
        self.assertIn("exactamente un rol", str(multiple.exception))

    def test_cambio_de_rol_queda_auditado(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.create_user(admin_token, "usuario", "clave-usuario", ["estudiante"])

        view = h.service.change_role(admin_token, "usuario", ["docente"])

        self.assertIs(view.role, Role.DOCENTE)
        event = next(e for e in h.audit.list() if e.action == "cambio_de_rol")
        self.assertEqual(event.actor, ADMIN_ID)
        self.assertEqual(event.resource, "usuario:usuario")
        self.assertIsNotNone(event.occurred_at)

    def test_respuesta_publica_no_incluye_credenciales(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)

        view = h.service.create_user(admin_token, "usuario", "clave-secreta", ["docente"])
        stored = h.users.get("usuario")

        self.assertEqual(set(asdict(view)), {"id", "role", "active"})
        self.assertNotIn("clave-secreta", stored.password_hash)
        self.assertNotIn("clave-secreta", repr(view))

    def test_usuario_duplicado_se_rechaza(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.create_user(admin_token, "usuario", "clave", ["docente"])

        with self.assertRaises(ConflictError):
            h.service.create_user(admin_token, "usuario", "otra-clave", ["docente"])

    def test_matriz_de_permisos_por_rol(self) -> None:
        h = build_harness()
        admin_token = h.service.login(ADMIN_ID, ADMIN_PASSWORD)
        h.service.create_user(admin_token, "docente", "clave-docente", ["docente"])
        h.service.create_user(admin_token, "estudiante", "clave-estudiante", ["estudiante"])
        doc_token = h.service.login("docente", "clave-docente")
        student_token = h.service.login("estudiante", "clave-estudiante")

        self.assertEqual(len(h.service.list_users(admin_token)), 3)
        self.assertEqual(h.service.get_user(doc_token, "docente").id, "docente")
        self.assertEqual(h.service.get_user(student_token, "estudiante").id, "estudiante")

        for token in (doc_token, student_token):
            with self.subTest(token=token):
                with self.assertRaises(AuthorizationError):
                    h.service.list_users(token)
                with self.assertRaises(AuthorizationError):
                    h.service.create_user(token, "nuevo", "clave", ["docente"])
                with self.assertRaises(AuthorizationError):
                    h.service.change_role(token, "docente", ["estudiante"])
                with self.assertRaises(AuthorizationError):
                    h.service.deactivate_user(token, "docente")

        with self.assertRaises(AuthorizationError):
            h.service.get_user(doc_token, "estudiante")
        with self.assertRaises(AuthorizationError):
            h.service.get_user(student_token, "docente")


if __name__ == "__main__":
    unittest.main()
