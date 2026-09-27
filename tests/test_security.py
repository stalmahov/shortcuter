"""Юнит-тесты security.py (ЛР7, п.2): без БД и HTTP, только логика.

Модуль: app/core/security.py. Покрывает выдачу/проверку JWT и хеш паролей.
"""

from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest

from app.core.config import JWT_ALGORITHM, JWT_SECRET, JWT_TTL_SECONDS
from app.core.security import AuthError, create_token, get_user_id, hash_password, verify_password


def test_token_roundtrip():
    assert get_user_id(create_token(42)) == 42


def test_token_lifetime_is_24h():
    payload = pyjwt.decode(
        create_token(1), JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False}
    )
    assert (payload["exp"] - payload["iat"]) == JWT_TTL_SECONDS == 86400


def test_expired_token_rejected():
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    token = pyjwt.encode(
        {"sub": "1", "iat": past, "exp": past}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    with pytest.raises(AuthError):
        get_user_id(token)


def test_wrong_secret_rejected():
    token = pyjwt.encode({"sub": "1"}, "чужой-секрет", algorithm=JWT_ALGORITHM)
    with pytest.raises(AuthError):
        get_user_id(token)


def test_token_without_sub_rejected():
    token = pyjwt.encode({"iat": 1}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    with pytest.raises(AuthError):
        get_user_id(token)


def test_garbage_rejected():
    with pytest.raises(AuthError):
        get_user_id("мусор")


def test_bcrypt_roundtrip():
    ph = hash_password("12345678")
    assert ph != "12345678"  # храним хеш, не пароль
    assert verify_password("12345678", ph) is True
    assert verify_password("wrongpass", ph) is False
