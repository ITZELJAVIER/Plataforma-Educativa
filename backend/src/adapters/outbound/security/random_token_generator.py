from __future__ import annotations

import secrets


class RandomTokenGenerator:
    def generate(self) -> str:
        return secrets.token_urlsafe(32)
