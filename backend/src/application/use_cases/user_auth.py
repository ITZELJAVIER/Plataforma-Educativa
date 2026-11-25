from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import timedelta

from src.application.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from src.domain.entities.audit_event import AuditEvent
from src.domain.entities.session import Session
from src.domain.entities.user import User, UserView
from src.domain.ports.audit_repository import AuditRepository
from src.domain.ports.clock import Clock
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_generator import TokenGenerator
from src.domain.ports.user_repository import UserRepository
from src.domain.value_objects.role import InvalidRoleError, Role, exactly_one_role

GENERIC_AUTH_ERROR = "Credenciales no válidas."
FORBIDDEN_ERROR = "Operación no permitida para el rol del usuario."


@dataclass(frozen=True)
class UserAuthService:
    users: UserRepository
    sessions: SessionRepository
    audit: AuditRepository
    hasher: PasswordHasher
    tokens: TokenGenerator
    clock: Clock
    session_ttl_seconds: int

    def login(self, user_id: str, password: str) -> str:
        user = self.users.get(user_id)
        if (
            user is None
            or not user.active
            or not self.hasher.verify(password, user.password_hash)
        ):
            raise self._authentication_failure(user_id)

        token = self.tokens.generate()
        expires_at = self.clock.now() + timedelta(seconds=self.session_ttl_seconds)
        self.sessions.add(
            Session(token=token, user_id=user.id, expires_at=expires_at)
        )
        self._record(user.id, "inicio_de_sesion", f"usuario:{user.id}")
        return token

    def logout(self, token: str) -> None:
        session = self._require_session(token)
        self.sessions.save(session.revoke())
        self._record(session.user_id, "cierre_de_sesion", f"usuario:{session.user_id}")

    def current_user(self, token: str) -> User:
        session = self._require_session(token)
        user = self.users.get(session.user_id)
        if user is None or not user.active:
            raise self._authentication_failure(session.user_id)
        return user

    def require_admin(self, token: str) -> User:
        actor = self.current_user(token)
        self._require_admin(actor)
        return actor

    def create_user(
        self, actor_token: str, user_id: str, password: str, roles: list[str]
    ) -> UserView:
        actor = self.current_user(actor_token)
        self._require_admin(actor)
        role = self._parse_roles(roles)
        if self.users.get(user_id) is not None:
            raise ConflictError("El usuario ya existe.")

        user = User(
            id=user_id,
            password_hash=self.hasher.hash(password),
            role=role,
            active=True,
        )
        self.users.add(user)
        return user.public()

    def list_users(self, actor_token: str) -> list[UserView]:
        actor = self.current_user(actor_token)
        self._require_admin(actor)
        return [user.public() for user in self.users.list()]

    def get_user(self, actor_token: str, user_id: str) -> UserView:
        actor = self.current_user(actor_token)
        self._require_self_or_admin(actor, user_id)
        user = self._require_user(user_id)
        return user.public()

    def change_role(
        self, actor_token: str, user_id: str, roles: list[str]
    ) -> UserView:
        actor = self.current_user(actor_token)
        self._require_admin(actor)
        role = self._parse_roles(roles)
        user = self._require_user(user_id)
        updated = replace(user, role=role)
        self.users.save(updated)
        self._record(actor.id, "cambio_de_rol", f"usuario:{user_id}")
        return updated.public()

    def deactivate_user(self, actor_token: str, user_id: str) -> UserView:
        return self._change_active(actor_token, user_id, False, "desactivacion_usuario")

    def reactivate_user(self, actor_token: str, user_id: str) -> UserView:
        return self._change_active(actor_token, user_id, True, "reactivacion_usuario")

    def _change_active(
        self, actor_token: str, user_id: str, active: bool, action: str
    ) -> UserView:
        actor = self.current_user(actor_token)
        self._require_admin(actor)
        user = self._require_user(user_id)
        updated = replace(user, active=active)
        self.users.save(updated)
        if not active:
            self.sessions.invalidate_all_for_user(user_id)
        self._record(actor.id, action, f"usuario:{user_id}")
        return updated.public()

    def _require_session(self, token: str) -> Session:
        session = self.sessions.get(token)
        if session is None or not session.is_valid(self.clock.now()):
            raise self._authentication_failure("desconocido")
        return session

    def _require_user(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise ValidationError("El usuario no existe.")
        return user

    def _require_admin(self, actor: User) -> None:
        if actor.role is not Role.ADMINISTRADOR:
            raise AuthorizationError(FORBIDDEN_ERROR)

    def _require_self_or_admin(self, actor: User, user_id: str) -> None:
        if actor.role is Role.ADMINISTRADOR or actor.id == user_id:
            return
        raise AuthorizationError(FORBIDDEN_ERROR)

    def _parse_roles(self, roles: list[str]) -> Role:
        try:
            return exactly_one_role(roles)
        except InvalidRoleError as exc:
            raise ValidationError(str(exc)) from exc

    def _authentication_failure(self, actor: str) -> AuthenticationError:
        self._record(actor, "fallo_autenticacion", f"usuario:{actor}")
        return AuthenticationError(GENERIC_AUTH_ERROR)

    def _record(self, actor: str, action: str, resource: str) -> None:
        self.audit.add(
            AuditEvent(
                actor=actor,
                action=action,
                resource=resource,
                occurred_at=self.clock.now(),
            )
        )
