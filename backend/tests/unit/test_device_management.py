from __future__ import annotations

import unittest

from src.application.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from src.application.use_cases.device_management import (
    DeviceConfigInput,
    DeviceInput,
)
from src.domain.value_objects.connection_state import ConnectionState
from src.domain.value_objects.role import Role
from src.domain.entities.user import User
from tests.helpers import ADMIN_ID, ADMIN_PASSWORD, build_device_harness


class DeviceManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = build_device_harness(tokens=["admin-token"])
        self.admin = self.h.auth.service.login(ADMIN_ID, ADMIN_PASSWORD)

    def _registrar(self, device_id: str = "disp-1") -> None:
        self.h.service.register_device(
            self.admin,
            DeviceInput(
                id=device_id,
                nombre="LED de banco",
                tipo="LED",
                perfil_hardware="perfil-banco",
                ubicacion="Laboratorio",
            ),
        )

    def _crear_usuario(self, ident: str, rol: Role) -> str:
        self.h.auth.users.add(
            User(
                id=ident,
                password_hash=self.h.auth.hasher.hash("clave-solo-prueba"),
                role=rol,
                active=True,
            )
        )
        return self.h.auth.service.login(ident, "clave-solo-prueba")

    def test_registro_valido_y_identificador_duplicado(self) -> None:
        vista = self.h.service.register_device(
            self.admin,
            DeviceInput(
                id="disp-1",
                nombre="LED de banco",
                tipo="LED",
                perfil_hardware="perfil-banco",
            ),
        )

        self.assertEqual(vista.id, "disp-1")
        self.assertEqual(vista.estado, ConnectionState.DESCONOCIDO)
        self.assertTrue(vista.habilitado)

        with self.assertRaises(ConflictError) as error:
            self._registrar("disp-1")
        self.assertIn("ya existe", str(error.exception))

    def test_identificador_inmutable(self) -> None:
        self._registrar()

        with self.assertRaises(ValidationError) as error:
            self.h.service.update_configuration(
                self.admin,
                "disp-1",
                DeviceConfigInput(id="otro", nombre="Otro nombre"),
            )

        self.assertIn("no puede modificarse", str(error.exception))
        self.assertEqual(self.h.service.get_device(self.admin, "disp-1").id, "disp-1")
        self.assertEqual(
            self.h.service.get_device(self.admin, "disp-1").nombre, "LED de banco"
        )

    def test_sin_reporte_el_estado_es_desconocido(self) -> None:
        self._registrar()

        vista = self.h.service.get_device(self.admin, "disp-1")

        self.assertEqual(vista.estado, ConnectionState.DESCONOCIDO)
        self.assertEqual(self.h.events.list_for_device("disp-1"), [])

    def test_estado_conectado_derivado_del_adaptador_y_evento(self) -> None:
        self._registrar()
        self.h.simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)

        vista = self.h.service.get_device(self.admin, "disp-1")
        eventos = self.h.events.list_for_device("disp-1")

        self.assertEqual(vista.estado, ConnectionState.CONECTADO)
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0].estado_anterior, ConnectionState.DESCONOCIDO)
        self.assertEqual(eventos[0].estado_nuevo, ConnectionState.CONECTADO)
        self.assertEqual(eventos[0].ocurrido_en, self.h.auth.clock.now())

    def test_transicion_a_desconectado_deja_dos_eventos(self) -> None:
        self._registrar()
        self.h.simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)
        self.h.service.get_device(self.admin, "disp-1")

        self.h.simulado.emitir_estado("disp-1", ConnectionState.DESCONECTADO)
        vista = self.h.service.get_device(self.admin, "disp-1")
        eventos = self.h.events.list_for_device("disp-1")

        self.assertEqual(vista.estado, ConnectionState.DESCONECTADO)
        self.assertEqual(
            [evento.estado_nuevo for evento in eventos],
            [ConnectionState.CONECTADO, ConnectionState.DESCONECTADO],
        )

    def test_configuracion_logica_se_persiste_y_queda_registrada(self) -> None:
        self._registrar()

        vista = self.h.service.update_configuration(
            self.admin,
            "disp-1",
            DeviceConfigInput(ubicacion="Aula 204", nombre="LED principal"),
        )

        self.assertEqual(vista.ubicacion, "Aula 204")
        self.assertEqual(vista.nombre, "LED principal")
        self.assertEqual(
            self.h.service.get_device(self.admin, "disp-1").ubicacion, "Aula 204"
        )
        self.assertTrue(
            any(
                evento.action == "configuracion_dispositivo"
                and evento.resource == "dispositivo:disp-1"
                for evento in self.h.auth.audit.list()
            )
        )

    def test_desactivacion_conserva_registro_y_no_usa_adaptador(self) -> None:
        self._registrar()
        self.h.simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)
        self.h.service.get_device(self.admin, "disp-1")

        desactivado = self.h.service.deactivate_device(self.admin, "disp-1")

        self.assertFalse(desactivado.habilitado)
        self.assertEqual(desactivado.estado, ConnectionState.DESCONECTADO)

        self.h.simulado.emitir_estado("disp-1", ConnectionState.CONECTADO)
        consulta = self.h.service.get_device(self.admin, "disp-1")
        self.assertEqual(consulta.estado, ConnectionState.DESCONECTADO)
        self.assertEqual(consulta.id, "disp-1")

    def test_roles_docente_y_estudiante_solo_consultan(self) -> None:
        self._registrar()
        docente = self._crear_usuario("docente", Role.DOCENTE)
        estudiante = self._crear_usuario("estudiante", Role.ESTUDIANTE)

        for token in (docente, estudiante):
            with self.subTest(token=token):
                self.assertEqual(len(self.h.service.list_devices(token)), 1)
                self.assertEqual(
                    self.h.service.get_device(token, "disp-1").id, "disp-1"
                )
                with self.assertRaises(AuthorizationError):
                    self.h.service.register_device(
                        token,
                        DeviceInput(
                            id="otro",
                            nombre="LED",
                            tipo="LED",
                            perfil_hardware="perfil",
                        ),
                    )
                with self.assertRaises(AuthorizationError):
                    self.h.service.update_configuration(
                        token, "disp-1", DeviceConfigInput(nombre="Cambio")
                    )
                with self.assertRaises(AuthorizationError):
                    self.h.service.deactivate_device(token, "disp-1")

    def test_cambio_de_adaptador_por_configuracion(self) -> None:
        self._registrar()

        actualizado = self.h.service.update_configuration(
            self.admin, "disp-1", DeviceConfigInput(adaptador="mqtt")
        )
        self.assertEqual(actualizado.adaptador, "mqtt")
        self.assertEqual(actualizado.estado, ConnectionState.DESCONOCIDO)

        self.h.mqtt.emitir_estado("disp-1", ConnectionState.CONECTADO)
        vista = self.h.service.get_device(self.admin, "disp-1")

        self.assertEqual(vista.estado, ConnectionState.CONECTADO)
        self.assertEqual(vista.adaptador, "mqtt")

    def test_adaptador_desconocido_y_sin_sesion_se_rechazan(self) -> None:
        with self.assertRaises(ValidationError):
            self.h.service.register_device(
                self.admin,
                DeviceInput(
                    id="disp-1",
                    nombre="LED",
                    tipo="LED",
                    perfil_hardware="perfil",
                    adaptador="no-existe",
                ),
            )

        with self.assertRaises(AuthenticationError):
            self.h.service.list_devices("token-inexistente")


if __name__ == "__main__":
    unittest.main()
