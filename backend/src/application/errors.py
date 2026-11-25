from __future__ import annotations


class ApplicationError(Exception):
    """Error de caso de uso con mensaje seguro para el cliente."""


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass
