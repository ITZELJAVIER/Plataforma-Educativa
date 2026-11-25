from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response

from src.adapters.inbound.rest.schemas import (
    CreateUserRequest,
    LoginRequest,
    RolesRequest,
    TokenResponse,
    UserResponse,
)
from src.application.errors import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from src.application.use_cases.user_auth import UserAuthService
from src.domain.entities.user import User, UserView

GENERIC_AUTH_ERROR = "Credenciales no válidas."

router = APIRouter(tags=["user-auth"])


@dataclass(frozen=True)
class Authenticated:
    token: str
    user: User


def get_service(request: Request) -> UserAuthService:
    return request.app.state.user_auth


def _token_from_header(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=GENERIC_AUTH_ERROR)
    return authorization.split(" ", 1)[1]


def get_authenticated(
    authorization: str | None = Header(default=None),
    service: UserAuthService = Depends(get_service),
) -> Authenticated:
    token = _token_from_header(authorization)
    try:
        user = service.current_user(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return Authenticated(token=token, user=user)


def _http_error(exc: ApplicationError) -> HTTPException:
    if isinstance(exc, AuthenticationError):
        return HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, AuthorizationError):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="Error interno.")


def _response(view: UserView) -> UserResponse:
    return UserResponse(id=view.id, role=view.role.value, active=view.active)


@router.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    service: UserAuthService = Depends(get_service),
) -> TokenResponse:
    try:
        token = service.login(payload.id, payload.password)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return TokenResponse(token=token)


@router.post("/auth/logout", status_code=204)
def logout(
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> Response:
    try:
        service.logout(auth.token)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return Response(status_code=204)


@router.get("/users/me", response_model=UserResponse)
def read_current_user(
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.get_user(auth.token, auth.user.id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> list[UserResponse]:
    try:
        views = service.list_users(auth.token)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return [_response(view) for view in views]


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    payload: CreateUserRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.create_user(
            auth.token, payload.id, payload.password, payload.roles
        )
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(
    user_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.get_user(auth.token, user_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def change_role(
    user_id: str,
    payload: RolesRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.change_role(auth.token, user_id, payload.roles)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.deactivate_user(auth.token, user_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.post("/users/{user_id}/reactivate", response_model=UserResponse)
def reactivate_user(
    user_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: UserAuthService = Depends(get_service),
) -> UserResponse:
    try:
        view = service.reactivate_user(auth.token, user_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)
