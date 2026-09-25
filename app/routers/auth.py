"""Зона пользователя: вход (Иван). Пока заглушки."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..schemas import Token, User

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/api/auth/register", status_code=201, response_model=User)
def register(payload: RegisterRequest):
    # TODO: хеш bcrypt, UNIQUE(email) → 409 EMAIL_TAKEN.
    return {"id": 42, "email": payload.email}


@router.post("/api/auth/login", response_model=Token)
def login(payload: LoginRequest):
    # TODO: проверка пары → 401, is_blocked → 403, выдача JWT (core/security.py).
    return {"token": "stub-token", "token_type": "Bearer", "expires_in": 86400}
