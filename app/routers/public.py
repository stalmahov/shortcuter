"""Гостевая зона (Стёпа): создание ссылки, редирект. Пока заглушки."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ..core.errors import error
from ..schemas import Link

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
    # TODO: проверка http/https, генерация кода 6 символов, запись в БД,
    # owner_id из токена, если приложен.
    return mock_link("aB3x9Q", url=payload.url)


@router.get("/{code}")
def resolve_code(code: str):
    # TODO: SELECT url FROM links WHERE code = ? (параметром, не склейкой).
    if code == "aB3x9Q":
        return RedirectResponse(url=MOCK_URL, status_code=301)
    return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
