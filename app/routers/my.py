"""Зона пользователя: свои ссылки (Иван)."""

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ..core.config import BASE_URL
from ..core.errors import error
from ..core.security import get_current_user
from ..db import get_engine
from ..schemas import Link

router = APIRouter()

# Спека, разд. 2: сравнение через lower(), т.к. not.enum регистрозависим.
RESERVED = {"api", "admin", "auth", "my", "static", "favicon.ico"}


def link_dto(row) -> dict:
    return {
        "id": row.id,
        "code": row.code,
        "url": row.url,
        "short_url": f"{BASE_URL}/{row.code}",
        "owner_id": row.owner_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/api/my/links")
def list_my_links(user: dict = Depends(get_current_user)):
    with get_engine().connect() as c:
        rows = c.execute(
            text(
                "SELECT id, code, url, owner_id, created_at FROM links "
                "WHERE owner_id = :o ORDER BY created_at DESC"
            ),
            {"o": user["id"]},
        ).all()
    return {"links": [link_dto(r) for r in rows]}


@router.delete("/api/my/links/{link_id}", status_code=204)
def delete_my_link(link_id: int, user: dict = Depends(get_current_user)):
    with get_engine().begin() as c:
        n = c.execute(
            text("DELETE FROM links WHERE id = :id AND owner_id = :o"),
            {"id": link_id, "o": user["id"]},
        ).rowcount
    if n == 0:
        # Чужая или отсутствующая — 404, существование чужих не раскрываем.
        return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
    return Response(status_code=204)


class AliasRequest(BaseModel):
    alias: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")


@router.put("/api/my/links/{link_id}/alias", response_model=Link)
def set_alias(
    link_id: int, payload: AliasRequest, user: dict = Depends(get_current_user)
):
    if payload.alias.lower() in RESERVED:
        return error("RESERVED_ALIAS", "Это имя зарезервировано", 400)
    try:
        with get_engine().begin() as c:
            row = c.execute(
                text(
                    "UPDATE links SET code = :code "
                    "WHERE id = :id AND owner_id = :o "
                    "RETURNING id, code, url, owner_id, created_at"
                ),
                {"code": payload.alias, "id": link_id, "o": user["id"]},
            ).fetchone()
    except IntegrityError:
        return error("ALIAS_TAKEN", "Такой алиас уже занят", 409)
    if row is None:
        return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
    return link_dto(row)
