from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: str
    password: str


class TokenResponse(BaseModel):
    token: str


class CreateUserRequest(BaseModel):
    id: str
    password: str
    roles: list[str]


class RolesRequest(BaseModel):
    roles: list[str]


class UserResponse(BaseModel):
    id: str
    role: str
    active: bool
