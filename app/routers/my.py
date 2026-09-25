"""Зона пользователя: свои ссылки (Иван). Пока заглушки."""

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from ..schemas import Link
from .public import mock_link

router = APIRouter()


@router.get("/api/my/links")
def list_my_links():
    # TODO: owner из токена, сортировка created_at DESC, 401/403.
    return {"links": [mock_link("aB3x9Q", owner=42)]}


@router.delete("/api/my/links/{link_id}", status_code=204)
def delete_my_link(link_id: int):
    # TODO: проверка владельца, чужая/нет → 404. Тела у 204 нет.
    return Response(status_code=204)


class AliasRequest(BaseModel):
    alias: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")


@router.put("/api/my/links/{link_id}/alias", response_model=Link)
def set_alias(link_id: int, payload: AliasRequest):
    # TODO: reserved-имена → 400, UNIQUE → 409, чужая → 404, 401/403.
    return mock_link(payload.alias, owner=42)
