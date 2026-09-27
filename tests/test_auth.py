"""Интеграционные тесты входа (ЛР7, п.2): HTTP + живая БД.

Модуль: app/routers/auth.py. ТЗ 4.1.1 (register/login), контракт openapi
(register_user, login_user): коды, тела, формат ошибок.
"""

from .conftest import make_user, sql_exec, sql_scalar


def test_register_201(client):
    r = client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@b.c"
    assert "id" in r.json()


def test_register_duplicate_409(client):
    client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    r = client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    assert r.status_code == 409
    assert r.json() == {"error": {"code": "EMAIL_TAKEN", "message": "Такой email уже зарегистрирован"}}


def test_register_weak_password_400(client):
    r = client.post("/api/auth/register", json={"email": "a@b.c", "password": "123"})
    assert r.status_code == 400
    assert set(r.json()) == {"error"}


def test_login_200_and_token(client):
    client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    r = client.post("/api/auth/login", json={"email": "a@b.c", "password": "12345678"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "Bearer"
    assert r.json()["expires_in"] == 86400


def test_login_wrong_password_401(client):
    client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    r = client.post("/api/auth/login", json={"email": "a@b.c", "password": "wrongpass"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_unknown_user_401(client):
    r = client.post("/api/auth/login", json={"email": "nobody@x.y", "password": "12345678"})
    assert r.status_code == 401


def test_login_blocked_403(client):
    make_user(client)
    sql_exec("UPDATE users SET is_blocked = TRUE WHERE email = 'a@b.c'")
    r = client.post("/api/auth/login", json={"email": "a@b.c", "password": "12345678"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "USER_BLOCKED"


def test_password_stored_hashed(client):
    client.post("/api/auth/register", json={"email": "a@b.c", "password": "12345678"})
    stored = sql_scalar("SELECT password_hash FROM users WHERE email = 'a@b.c'")
    assert stored != "12345678"
    assert stored.startswith("$2b$")  # bcrypt
