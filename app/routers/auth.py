"""Зона пользователя: вход (Иван)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ..core.errors import error
from ..core.security import create_token, hash_password, verify_password
from ..db import get_engine
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
    try:
        with get_engine().begin() as c:
            row = c.execute(
                text(
                    "INSERT INTO users (email, password_hash) "
                    "VALUES (:email, :ph) "
                    "RETURNING id, email, role, is_blocked"
                ),
                {"email": payload.email, "ph": hash_password(payload.password)},
            ).one()
    except IntegrityError:
        return error("EMAIL_TAKEN", "Такой email уже зарегистрирован", 409)
    return {
        "id": row.id,
        "email": row.email,
        "role": row.role,
        "is_blocked": row.is_blocked,
    }


@router.post("/api/auth/login", response_model=Token)
def login(payload: LoginRequest):
    with get_engine().connect() as c:
        row = c.execute(
            text("SELECT id, password_hash, is_blocked FROM users WHERE email = :email"),
            {"email": payload.email},
        ).fetchone()
    if row is None or not verify_password(payload.password, row.password_hash):
        return error("UNAUTHORIZED", "Неверный email или пароль", 401)
    if row.is_blocked:
        return error("USER_BLOCKED", "Пользователь заблокирован", 403)
    return {"token": create_token(row.id), "token_type": "Bearer", "expires_in": 86400}
