from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import re
import string
import secrets
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.core.config import BASE_URL

from app.core.errors import error
from app.schemas import Link
from app.db import get_engine
from app.core.security import get_user_id

MOCK_URL = "https://example.com/long"
def mock_link(code: str, url: str = MOCK_URL, owner: int | None = None) -> dict:
    return {
        "id": 1,
        "code": code,
        "url": url,
        "short_url": f"{BASE_URL}/{code}",
        "owner_id": owner,
        "created_at": None,
    }

router = APIRouter()
security = HTTPBearer(auto_error=False)

def generate_random_string(length):
    # string.ascii_letters содержит 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # string.digits содержит '0123456789'
    letters_and_digits = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(letters_and_digits) for i in range(length))


class CreateLinkRequest(BaseModel):
    url: str
    code: str | None = None


@router.post("/api/links", status_code=201, response_model=Link)
def create_link(payload: CreateLinkRequest,
                credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        
    owner_id = None
    
    if credentials:
        try:
            owner_id = get_user_id(credentials.credentials)
        except Exception:
            owner_id = None
    
    if not payload.url.startswith(("http://", "https://")):
        return error("BAD_URL", "Ссылка должна начинаться на http:// или https://",400)
    alias = None
    if owner_id != None and payload.code:
        if not re.match(r'^[A-Za-z0-9_-]{3,32}$', payload.code):
            return error("BAD_CODE", "Алиас должен состоять из 3-32 латинских букв, цифр или дефисов", 400)
        alias = payload.code
    if alias == None:
        alias = generate_random_string(6)
    with get_engine().begin() as connection:
        # Пользователь авторизованный
        if owner_id:
            try:
                result = connection.execute(
                    text("""
                        INSERT INTO links (code, url, owner_id)
                        VALUES (:code, :url, :owner_id)
                        RETURNING id, code, url, owner_id, created_at;
                    """),
                    {'code': alias, 'url': payload.url, 'owner_id': owner_id}
                )
                row = result.one()
                
                return Link(
                    id=row.id,
                    code=row.code,
                    url=row.url,
                    short_url=f"{BASE_URL}/{row.code}",
                    owner_id=row.owner_id,
                    created_at=str(row.created_at) if row.created_at else None
                )
            except IntegrityError:
                return error("CODE_ALREADY_EXISTS", "Такой алиас уже занят", 409)
        # Пользователь не авторизованный
        else:
            for attempt in range(5):
                current_alias = generate_random_string(6)
                try:
                    result = connection.execute(
                        text("""
                            INSERT INTO links (code, url, owner_id)
                            VALUES (:code, :url, NULL)
                            RETURNING id, code, url, owner_id, created_at;
                        """),
                        {'code': current_alias, 'url': payload.url}
                    )
                    row = result.one()
                    
                    return Link(
                        id=row.id,
                        code=row.code,
                        url=row.url,
                        short_url=f"{BASE_URL}/{row.code}",
                        owner_id=None,
                        created_at=str(row.created_at) if row.created_at else None
                    )
                except IntegrityError:
                    continue
            
            # 5 коллизий подряд
            return error("LINK_CREATION_FAILED","Не удалось создать ссылку из-за высокой нагрузки",500)


@router.get("/{code}")
def resolve_code(code: str):
    with get_engine().connect() as connection:
        result = connection.execute(text("SELECT url FROM links WHERE code = :code"),
                           {'code': code}
                           )
        row = result.fetchone()
        if row is None:
            return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
        return RedirectResponse(url=row.url, status_code=301)
