from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import logging
import sys
import unittest
import uuid
from datetime import datetime

from fastapi import Request

from src.infrastructure.logging.config import (
    JsonFormatter,
    configure_logging,
    log_event,
    redact_sensitive,
)
from src.infrastructure.logging.request_logging import _resolve_request_id


class JsonFormatterTests(unittest.TestCase):
    def _record(
        self,
        *,
        level: int = logging.ERROR,
        message: str = "fallo de prueba",
        context: dict[str, object] | None = None,
    ) -> logging.LogRecord:
        record = logging.LogRecord(
            "modulo.prueba", level, __file__, 1, message, (), None
        )
        if context is not None:
            record.context = context
        return record

    def test_formato_json_valido_con_campos_requeridos(self) -> None:
        payload = json.loads(
            JsonFormatter().format(self._record(context={"status_code": 500}))
        )

        self.assertEqual(
            {"timestamp", "level", "logger", "message", "context"}, set(payload)
        )
        self.assertEqual(payload["level"], "ERROR")
        self.assertEqual(payload["logger"], "modulo.prueba")
        self.assertEqual(payload["message"], "fallo de prueba")
        self.assertEqual(payload["context"], {"status_code": 500})
        datetime.fromisoformat(payload["timestamp"])

    def test_redaccion_de_claves_y_valores_sensibles(self) -> None:
        mensaje = (
            "password=clave-secreta token=abc123 "
            "Bearer eyJhbGciOi "
            "postgresql://usuario:clave-bd@servidor/db"
        )

        resultado = redact_sensitive(mensaje)

        self.assertNotIn("clave-secreta", resultado)
        self.assertNotIn("abc123", resultado)
        self.assertNotIn("eyJhbGciOi", resultado)
        self.assertNotIn("clave-bd", resultado)
        self.assertIn("[REDACTED]", resultado)

    def test_contexto_sensible_tambien_se_redacta(self) -> None:
        payload = json.loads(
            JsonFormatter().format(
                self._record(
                    context={
                        "password": "clave-secreta",
                        "token": "abc123",
                        "status_code": 401,
                    }
                )
            )
        )

        self.assertEqual(payload["context"]["password"], "[REDACTED]")
        self.assertEqual(payload["context"]["token"], "[REDACTED]")
        self.assertEqual(payload["context"]["status_code"], 401)
        self.assertNotIn("clave-secreta", json.dumps(payload))


class ConfigureLoggingTests(unittest.TestCase):
    def test_configuracion_idempotente_y_salida_stdout(self) -> None:
        root = logging.getLogger()
        marker = "_plataforma_educativa_handler"

        configure_logging()
        primeros = [h for h in root.handlers if getattr(h, marker, False)]
        configure_logging()
        segundos = [h for h in root.handlers if getattr(h, marker, False)]

        self.assertEqual(len(primeros), 1)
        self.assertEqual(len(segundos), 1)
        self.assertIs(segundos[0].stream, sys.stdout)
        self.assertIsInstance(segundos[0].formatter, JsonFormatter)

    def test_log_evento_incluye_contexto(self) -> None:
        registros: list[logging.LogRecord] = []

        class Capturador(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                registros.append(record)

        logger = logging.getLogger("prueba.log_event")
        manejador = Capturador()
        logger.handlers = [manejador]
        logger.setLevel(logging.INFO)
        logger.propagate = False
        try:
            log_event(
                logging.INFO,
                "evento",
                logger_name="prueba.log_event",
                status_code=200,
            )
        finally:
            logger.handlers = []
            logger.propagate = True

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].context, {"status_code": 200})


class RedaccionReforzadaTests(unittest.TestCase):
    @staticmethod
    def _record(context=None, message="fallo", exc_info=None):
        record = logging.LogRecord(
            "prueba", logging.ERROR, __file__, 1, message, (), exc_info
        )
        record.context = context if context is not None else {}
        return record

    def test_u1_authorization_bearer_en_un_solo_mensaje(self) -> None:
        secreto = "eyJhbGciOiSECRETO"

        resultado = redact_sensitive(f"Authorization: Bearer {secreto}")

        self.assertNotIn(secreto, resultado)
        self.assertIn("[REDACTED]", resultado)

    def test_u2_token_con_prefijo_bearer(self) -> None:
        resultado = redact_sensitive(
            "token=Bearer abc123XYZ password: Bearer def456"
        )

        self.assertNotIn("abc123XYZ", resultado)
        self.assertNotIn("def456", resultado)

    def test_u3_contexto_anidado(self) -> None:
        contexto = {"outer": {"token": "s1", "items": [{"password": "s2"}]}}

        payload = json.loads(JsonFormatter().format(self._record(contexto)))

        self.assertEqual(payload["context"]["outer"]["token"], "[REDACTED]")
        self.assertEqual(
            payload["context"]["outer"]["items"][0]["password"], "[REDACTED]"
        )
        self.assertNotIn("s1", json.dumps(payload))
        self.assertNotIn("s2", json.dumps(payload))

    def test_u4_dataclass_sin_asdict_ni_deepcopy(self) -> None:
        @dataclasses.dataclass
        class Config:
            database_url: str

            def __deepcopy__(self, memo):
                raise AssertionError("__deepcopy__ no debe invocarse")

        contexto = {"settings": Config("postgresql://u:clave-bd@servidor/db")}

        payload = json.loads(JsonFormatter().format(self._record(contexto)))

        self.assertEqual(payload["context"]["settings"]["database_url"], "[REDACTED]")
        self.assertNotIn("clave-bd", json.dumps(payload))

    def test_u5_objeto_desconocido_no_invoca_dunders(self) -> None:
        class Traicionero:
            password = "secreto-interno"

            def __str__(self) -> str:
                raise AssertionError("__str__ no debe invocarse")

            def __repr__(self) -> str:
                raise AssertionError("__repr__ no debe invocarse")

            def __deepcopy__(self, memo):
                raise AssertionError("__deepcopy__ no debe invocarse")

        payload = json.loads(
            JsonFormatter().format(self._record({"objeto": Traicionero()}))
        )

        valor = payload["context"]["objeto"]
        self.assertEqual(valor["__tipo__"], "Traicionero")
        self.assertEqual(valor["__valor__"], "[OMITIDO]")
        self.assertNotIn("secreto-interno", json.dumps(payload))

    def test_u6_circular_y_profundidad(self) -> None:
        ciclo = {"token": "s"}
        ciclo["self"] = ciclo
        payload = json.loads(
            JsonFormatter().format(self._record({"ciclo": ciclo}))
        )
        self.assertEqual(payload["context"]["ciclo"]["self"], "[CIRCULAR]")

        profundo = {"n": 0}
        actual = profundo
        for _ in range(12):
            actual["n"] = {}
            actual = actual["n"]
        payload = json.loads(JsonFormatter().format(self._record(profundo)))
        self.assertEqual(json.dumps(payload).count("[PROFUNDIDAD_MAXIMA]"), 1)


class TracebackSeguroTests(unittest.TestCase):
    def test_u8_traceback_sin_str_de_excepcion(self) -> None:
        class ExcepcionTraicionera(Exception):
            def __str__(self) -> str:
                raise AssertionError("__str__ no debe invocarse")

        try:
            raise ExcepcionTraicionera("secreto-no-registrar")
        except ExcepcionTraicionera:
            info = sys.exc_info()

        record = logging.LogRecord(
            "prueba", logging.ERROR, __file__, 1, "fallo", (), info
        )
        record.context = {}

        payload = json.loads(JsonFormatter().format(record))

        self.assertIn("traceback", payload)
        self.assertEqual(payload["traceback"]["tipo"], "ExcepcionTraicionera")
        self.assertNotIn("secreto-no-registrar", json.dumps(payload))


class UvicornLoggerConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.marcador = "_plataforma_educativa_handler"
        self.raiz = logging.getLogger()
        self.previos = [
            h for h in self.raiz.handlers if getattr(h, self.marcador, False)
        ]
        for handler in self.previos:
            self.raiz.removeHandler(handler)

        self.uvicorn = logging.getLogger("uvicorn")
        self.error = logging.getLogger("uvicorn.error")
        self.access = logging.getLogger("uvicorn.access")
        self.estado = [
            (lg, list(lg.handlers), lg.propagate, lg.level)
            for lg in (self.uvicorn, self.error, self.access)
        ]

        self.sink_viejo = logging.StreamHandler(io.StringIO())
        self.uvicorn.handlers = [self.sink_viejo]
        self.uvicorn.propagate = False
        self.error.handlers = []
        self.error.propagate = True
        self.access.handlers = [logging.StreamHandler(io.StringIO())]
        self.access.propagate = False

    def tearDown(self) -> None:
        for logger, handlers, propagate, level in self.estado:
            logger.handlers = handlers
            logger.propagate = propagate
            logger.setLevel(level)
        for handler in list(self.raiz.handlers):
            if getattr(handler, self.marcador, False):
                self.raiz.removeHandler(handler)
        for handler in self.previos:
            self.raiz.addHandler(handler)
        self.sink_viejo.close()

    def test_u7_solo_uvicorn_y_sin_duplicados(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            configure_logging()

        marcados = [
            h for h in self.raiz.handlers if getattr(h, self.marcador, False)
        ]
        self.assertEqual(len(marcados), 1)
        self.assertEqual(self.uvicorn.handlers, marcados)
        self.assertFalse(self.uvicorn.propagate)
        self.assertEqual(self.error.handlers, [])
        self.assertTrue(self.error.propagate)
        self.assertIsNot(self.access.handlers[0], marcados[0])

        self.error.error("evento_unico")
        lineas = [linea for linea in buffer.getvalue().splitlines() if linea.strip()]
        self.assertEqual(len(lineas), 1)
        self.assertIn("evento_unico", lineas[0])
        self.assertEqual(self.sink_viejo.stream.getvalue(), "")


class RequestIdTests(unittest.TestCase):
    @staticmethod
    def _request(valor=None) -> Request:
        headers = [] if valor is None else [(b"x-request-id", valor.encode("utf-8"))]
        return Request(
            {"type": "http", "method": "GET", "path": "/", "headers": headers}
        )

    def test_u9_validacion_y_longitud(self) -> None:
        self.assertEqual(
            _resolve_request_id(self._request("abc-123.XYZ")), "abc-123.XYZ"
        )
        for invalido in ("con espacio", "a" * 65, "valor;otro", "salto\nlinea"):
            resultado = _resolve_request_id(self._request(invalido))
            self.assertNotEqual(resultado, invalido)
            uuid.UUID(resultado)
        uuid.UUID(_resolve_request_id(self._request()))


if __name__ == "__main__":
    unittest.main()
