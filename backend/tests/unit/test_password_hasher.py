from __future__ import annotations

import unittest

from src.adapters.outbound.security.pbkdf2_password_hasher import Pbkdf2PasswordHasher


class Pbkdf2PasswordHasherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hasher = Pbkdf2PasswordHasher()

    def test_hash_no_contiene_la_contrasena_en_claro(self) -> None:
        password = "clave-solo-prueba"
        stored = self.hasher.hash(password)

        self.assertNotEqual(stored, password)
        self.assertNotIn(password, stored)

    def test_sal_individual_por_cada_hash(self) -> None:
        first = self.hasher.hash("misma-clave")
        second = self.hasher.hash("misma-clave")

        self.assertNotEqual(first, second)
        self.assertTrue(self.hasher.verify("misma-clave", first))
        self.assertTrue(self.hasher.verify("misma-clave", second))

    def test_verificacion_rechaza_contrasena_incorrecta(self) -> None:
        stored = self.hasher.hash("clave-correcta")

        self.assertFalse(self.hasher.verify("clave-incorrecta", stored))
        self.assertFalse(self.hasher.verify("clave-correcta", "formato-invalido"))


if __name__ == "__main__":
    unittest.main()
