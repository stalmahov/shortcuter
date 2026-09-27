"""Интеграционные тесты своих ссылок (ЛР7, п.2): HTTP + живая БД.

Модуль: app/routers/my.py. ТЗ 4.1.1 (list/delete/alias), контракт openapi
(list_my_links, delete_my_link, set_link_alias).
"""

import pytest

from .conftest import make_user, sql_exec, sql_scalar


@pytest.fixture()
def owned(client):
    """Юзер + его ссылка. Возвращает (headers, link_id)."""
    h = make_user(client)
    sql_exec(
        "INSERT INTO links (code, url, owner_id) VALUES ('mine01', 'https://m.e', 1)"
    )
    link_id = sql_scalar("SELECT id FROM links WHERE code = 'mine01'")
    return h, link_id


def test_list_requires_token(client):
    assert client.get("/api/my/links").status_code == 401


def test_list_bad_token_401(client):
    r = client.get("/api/my/links", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401
    assert set(r.json()) == {"error"}


def test_list_empty(client):
    assert client.get("/api/my/links", headers=make_user(client)).json() == {"links": []}


def test_list_only_mine(client, owned):
    h, _ = owned
    make_user(client, "b@c.d")
    sql_exec("INSERT INTO links (code, url, owner_id) VALUES ('other1', 'https://o.t', 2)")
    r = client.get("/api/my/links", headers=h)
    assert [x["code"] for x in r.json()["links"]] == ["mine01"]


def test_list_short_url_format(client, owned):
    h, _ = owned
    link = client.get("/api/my/links", headers=h).json()["links"][0]
    assert link["short_url"] == "http://localhost:8000/mine01"
    assert link["owner_id"] == 1


def test_delete_own_204(client, owned):
    h, link_id = owned
    r = client.delete(f"/api/my/links/{link_id}", headers=h)
    assert r.status_code == 204
    assert r.text == ""
    assert client.delete(f"/api/my/links/{link_id}", headers=h).status_code == 404


def test_delete_foreign_404(client, owned):
    h, _ = owned
    make_user(client, "b@c.d")
    sql_exec("INSERT INTO links (code, url, owner_id) VALUES ('other1', 'https://o.t', 2)")
    other_id = sql_scalar("SELECT id FROM links WHERE code = 'other1'")
    r = client.delete(f"/api/my/links/{other_id}", headers=h)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "LINK_NOT_FOUND"


def test_alias_200(client, owned):
    h, link_id = owned
    r = client.put(f"/api/my/links/{link_id}/alias", json={"alias": "moy-kursach"}, headers=h)
    assert r.status_code == 200
    assert r.json()["code"] == "moy-kursach"
    assert r.json()["short_url"] == "http://localhost:8000/moy-kursach"


def test_alias_foreign_404(client, owned):
    h, _ = owned
    make_user(client, "b@c.d")
    sql_exec("INSERT INTO links (code, url, owner_id) VALUES ('other1', 'https://o.t', 2)")
    other_id = sql_scalar("SELECT id FROM links WHERE code = 'other1'")
    assert client.put(f"/api/my/links/{other_id}/alias", json={"alias": "chuzhaya"}, headers=h).status_code == 404


@pytest.mark.parametrize("bad", ["API", "ADMIN", "STATIC", "auth"])
def test_alias_reserved_400(client, owned, bad):
    h, link_id = owned
    r = client.put(f"/api/my/links/{link_id}/alias", json={"alias": bad}, headers=h)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "RESERVED_ALIAS"


def test_alias_dot_400(client, owned):
    # Точка не проходит pattern — 400 раньше reserved-проверки, код общий.
    # По спеке сравнение reserved идёт через lower(), но до него не доходит.
    h, link_id = owned
    r = client.put(f"/api/my/links/{link_id}/alias", json={"alias": "favicon.ico"}, headers=h)
    assert r.status_code == 400
    assert set(r.json()) == {"error"}


def test_alias_too_short_400(client, owned):
    h, link_id = owned
    assert client.put(f"/api/my/links/{link_id}/alias", json={"alias": "xx"}, headers=h).status_code == 400


def test_alias_taken_409(client, owned):
    h, link_id = owned
    sql_exec("INSERT INTO links (code, url, owner_id) VALUES ('taken1', 'https://t.t', 1)")
    r = client.put(f"/api/my/links/{link_id}/alias", json={"alias": "taken1"}, headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ALIAS_TAKEN"


def test_blocked_user_403(client, owned):
    h, _ = owned
    sql_exec("UPDATE users SET is_blocked = TRUE WHERE id = 1")
    r = client.get("/api/my/links", headers=h)
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "USER_BLOCKED"
