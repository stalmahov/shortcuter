"""Общее для тестов ЛР7: клиент + чистая БД + помощники.

Временно собираем приложение из готовых роутеров (auth, my): public.py Стёпы
 ने импортируется (см. ревью PR #8). Как только он починит импорты —
переключить client на app.main (TODO #4, #5).
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://shortcuter:shortcuter@localhost:5433/shortcuter",
)

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.errors import error, validation_handler
from app.core.security import AuthError, UserBlocked
from app.db import get_engine
from app.routers import auth, my


def build_app() -> FastAPI:
    app = FastAPI(title="Shortcuter API (tests)")

    app.add_exception_handler(RequestValidationError, validation_handler)

    @app.exception_handler(AuthError)
    async def auth_handler(request, exc):
        return error("UNAUTHORIZED", "Нет или невалидный токен", 401)

    @app.exception_handler(UserBlocked)
    async def blocked_handler(request, exc):
        return error("USER_BLOCKED", "Пользователь заблокирован", 403)

    app.include_router(auth.router)
    app.include_router(my.router)
    return app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(build_app(), follow_redirects=False)


@pytest.fixture(autouse=True)
def clean_db():
    """Каждый тест стартует с пустых users/links (тесты самодостаточны)."""
    with get_engine().begin() as c:
        c.execute(text("TRUNCATE users, links RESTART IDENTITY CASCADE"))
    yield


def make_user(client: TestClient, email: str = "a@b.c", pw: str = "12345678") -> dict:
    """Регистрация + вход. Возвращает заголовок Authorization."""
    assert client.post("/api/auth/register", json={"email": email, "password": pw}).status_code == 201
    r = client.post("/api/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def sql_exec(statement: str, **params):
    """INSERT/UPDATE/DELETE/TRUNCATE."""
    with get_engine().begin() as c:
        c.execute(text(statement), params)


def sql_scalar(statement: str, **params):
    """Одиночное значение SELECT (чтение внутри открытого соединения)."""
    with get_engine().connect() as c:
        return c.execute(text(statement), params).scalar()
