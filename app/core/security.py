"""JWT: выдача и проверка (HS256, 24 часа, секрет только из env). Зона Ивана."""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text

from .config import JWT_ALGORITHM, JWT_SECRET, JWT_TTL_SECONDS


class AuthError(Exception):
    """Нет/битый/протухший токен, нет пользователя → 401 (handler в main.py)."""


class UserBlocked(Exception):
    """Пользователь заблокирован → 403 (handler в main.py)."""


bearer = HTTPBearer()


def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=JWT_TTL_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError):
        raise AuthError("невалидный токен")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    """Зависимость для защищённых ручек: user_id + роль + блокировка."""
    from ..db import get_engine  # локально: reraise без циклов импорта

    user_id = get_user_id(creds.credentials)
    with get_engine().connect() as c:
        row = c.execute(
            text("SELECT id, role, is_blocked FROM users WHERE id = :id"),
            {"id": user_id},
        ).fetchone()
    if row is None:
        raise AuthError("пользователь не существует")
    if row.is_blocked:
        raise UserBlocked()
    return {"id": row.id, "role": row.role, "is_blocked": row.is_blocked}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
