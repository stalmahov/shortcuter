"""Pydantic-схемы ответов — один в один по openapi.yaml (components.schemas)."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class Link(BaseModel):
    id: int
    code: str
    url: str
    short_url: str
    owner_id: int | None = None
    created_at: str | None = None


class User(BaseModel):
    id: int
    email: str
    role: str | None = None
    is_blocked: bool | None = None
    created_at: str | None = None


class Token(BaseModel):
    token: str
    token_type: str
    expires_in: int
