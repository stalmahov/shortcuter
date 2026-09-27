"""Гостевая зона (Стёпа): создание ссылки, редирект. Пока заглушки."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ..core.errors import error
from ..schemas import Link
from db import get_engine

from sqlalchemy.orm import Session
from schemas import Link

router = APIRouter()

MOCK_URL = "https://example.com/long"


def mock_link(code: str, url: str = MOCK_URL, owner: int | None = None) -> dict:
    return {
        "id": 1,
        "code": code,
        "url": url,
        "short_url": f"http://localhost:8000/{code}",
        "owner_id": owner,
        "created_at": None,
    }


class CreateLinkRequest(BaseModel):
    url: str


@router.post("/api/links", status_code=201, response_model=Link)
def create_link(payload: CreateLinkRequest):
    
    get_engine().begin()
    # TODO: проверка http/https, генерация кода 6 символов, запись в БД,
    # owner_id из токена, если приложен.
    return mock_link("aB3x9Q", url=payload.url)


@router.get("/{code}")
def resolve_code(code: str):
    with get_engine().connect() as connection:
        result = connection.execute("SELECT url FROM links WHERE code = :code",
                           {'code': code}
                           )
        row = result.fetchone()
        if row is None:
            return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
        return RedirectResponse(url=row.url, status_code=301)
