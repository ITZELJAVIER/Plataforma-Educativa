from __future__ import annotations

import hashlib
import hmac
import os

_ALGORITHM = "sha256"
_ITERATIONS = 200_000
_SALT_BYTES = 16
_PREFIX = f"pbkdf2_{_ALGORITHM}"


class Pbkdf2PasswordHasher:
    """Hash con sal individual usando solo la biblioteca estándar."""

    def hash(self, password: str) -> str:
        salt = os.urandom(_SALT_BYTES)
        derived = hashlib.pbkdf2_hmac(
            _ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS
        )
        return f"{_PREFIX}${_ITERATIONS}${salt.hex()}${derived.hex()}"

    def verify(self, password: str, stored_hash: str) -> bool:
        try:
            prefix, iterations, salt_hex, expected_hex = stored_hash.split("$")
            if prefix != _PREFIX:
                return False
            derived = hashlib.pbkdf2_hmac(
                _ALGORITHM,
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
            return hmac.compare_digest(derived.hex(), expected_hex)
        except (ValueError, TypeError):
            return False
