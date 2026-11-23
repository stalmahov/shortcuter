import pytest
from fastapi.testclient import TestClient

from .conftest import make_user, sql_exec, sql_scalar


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


@pytest.fixture
def admin(client):
    headers = make_user(client, email="admin@example.com")
    sql_exec("UPDATE users SET role = 'admin' WHERE email = :email",
             email="admin@example.com")
    return headers


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/api/admin/users", None),
    ("POST", "/api/admin/users/2/block", {"is_blocked": True}),
])
@pytest.mark.parametrize("token", [None, "invalid"])
def test_admin_requires_token(client, method, path, body, token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.request(method, path, json=body, headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_regular_user_cannot_manage_users(client):
    headers = make_user(client)
    for response in [
        client.get("/api/admin/users", headers=headers),
        client.post("/api/admin/users/1/block", headers=headers,
                    json={"is_blocked": True}),
    ]:
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"
    assert sql_scalar("SELECT is_blocked FROM users WHERE id = 1") is False


def test_list_users(client, admin):
    make_user(client)
    response = client.get("/api/admin/users", headers=admin)
    assert response.status_code == 200
    users = response.json()["users"]
    assert [user["email"] for user in users] == ["admin@example.com", "a@b.c"]
    assert users[0]["role"] == "admin"
    assert all(user["created_at"] for user in users)
    assert all("password_hash" not in user for user in users)


def test_block_and_unblock_user(client, admin):
    headers = make_user(client)
    for _ in range(2):
        response = client.post("/api/admin/users/2/block", headers=admin,
                               json={"is_blocked": True})
        assert response.status_code == 200
        assert response.json()["email"] == "a@b.c"
        assert response.json()["is_blocked"] is True
        date = sql_scalar("SELECT blocked_at FROM users WHERE id = 2")
        if _ == 0:
            first_date = date
            assert first_date is not None
        else:
            assert date == first_date
    assert sql_scalar("SELECT is_blocked FROM users WHERE id = 2") is True
    assert client.get("/api/my/links", headers=headers).status_code == 403
    assert client.post("/api/auth/login", json={
        "email": "a@b.c", "password": "12345678"
    }).status_code == 403
    response = client.post("/api/admin/users/2/block", headers=admin,
                           json={"is_blocked": False})
    assert response.status_code == 200
    assert response.json()["is_blocked"] is False
    assert sql_scalar("SELECT is_blocked FROM users WHERE id = 2") is False
    assert sql_scalar("SELECT blocked_at FROM users WHERE id = 2") is None
    assert client.get("/api/my/links", headers=headers).status_code == 200
    assert client.post("/api/auth/login", json={
        "email": "a@b.c", "password": "12345678"
    }).status_code == 200


def test_admin_cannot_block_self(client, admin):
    response = client.post("/api/admin/users/1/block", headers=admin,
                           json={"is_blocked": True})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SELF_BLOCK"
    assert sql_scalar("SELECT is_blocked FROM users WHERE id = 1") is False


def test_missing_user(client, admin):
    response = client.post("/api/admin/users/999/block", headers=admin,
                           json={"is_blocked": True})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_blocked_admin_cannot_manage_users(client, admin):
    sql_exec("UPDATE users SET is_blocked = TRUE WHERE id = 1")
    assert client.get("/api/admin/users", headers=admin).status_code == 403
    response = client.post("/api/admin/users/1/block", headers=admin,
                           json={"is_blocked": False})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "USER_BLOCKED"


def test_block_requires_boolean(client, admin):
    response = client.post("/api/admin/users/1/block", headers=admin,
                           json={"is_blocked": "invalid"})
    assert response.status_code == 400


def test_admin_lists_and_deletes_guest_and_owned_links(client, admin):
    make_user(client)
    sql_exec(
        "INSERT INTO links (code, url, owner_id) VALUES "
        "('guest', 'https://example.com', NULL), ('owned', 'https://example.org', 2)"
    )
    response = client.get("/api/admin/links", headers=admin)
    assert response.status_code == 200
    links = response.json()["links"]
    assert [(link["code"], link["owner_id"]) for link in links] == [
        ("guest", None), ("owned", 2)
    ]
    for link in links:
        path = f"/api/admin/links/{link['id']}"
        assert client.delete(path, headers=admin).status_code == 204
        assert client.get(f"/{link['code']}").status_code == 404
        assert client.delete(path, headers=admin).status_code == 404


def test_regular_user_cannot_delete_link(client):
    headers = make_user(client)
    sql_exec("INSERT INTO links (code, url) VALUES ('guest', 'https://example.com')")
    assert client.get("/api/admin/links", headers=headers).status_code == 403
    assert client.delete("/api/admin/links/1").status_code == 401
    assert client.delete("/api/admin/links/1", headers=headers).status_code == 403
    assert client.get("/guest").status_code == 301


def test_admin_returns_json_when_database_is_unavailable(client, admin, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError
    from app.routers import admin as admin_router

    def unavailable():
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(admin_router, "get_engine", unavailable)
    response = client.get("/api/admin/users", headers=admin)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
