from __future__ import annotations

import unittest

from src.domain.value_objects.role import InvalidRoleError, Role, exactly_one_role


class RoleAssignmentTests(unittest.TestCase):
    def test_acepta_cada_uno_de_los_tres_roles(self) -> None:
        for value, expected in (
            ("administrador", Role.ADMINISTRADOR),
            ("docente", Role.DOCENTE),
            ("estudiante", Role.ESTUDIANTE),
        ):
            with self.subTest(value=value):
                self.assertIs(exactly_one_role([value]), expected)

    def test_rechaza_usuario_sin_rol(self) -> None:
        with self.assertRaises(InvalidRoleError) as ctx:
            exactly_one_role([])
        self.assertIn("obligatorio", str(ctx.exception))

    def test_rechaza_mas_de_un_rol(self) -> None:
        with self.assertRaises(InvalidRoleError) as ctx:
            exactly_one_role(["docente", "estudiante"])
        self.assertIn("exactamente un rol", str(ctx.exception))

    def test_rechaza_rol_no_definido(self) -> None:
        with self.assertRaises(InvalidRoleError):
            exactly_one_role(["otro"])


if __name__ == "__main__":
    unittest.main()
