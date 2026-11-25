"""Пользователи и ссылки в административной панели."""

import logging

from fastapi import APIRouter, Depends, Response
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import case, delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.errors import error
from ..core.security import AuthError, get_current_user
from ..db import get_engine
from ..models import LinkRecord, UserRecord
from ..schemas import User

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)


class AdminRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def handle(request):
            try:
                return await handler(request)
            except SQLAlchemyError:
                logger.exception("Database error in admin request")
                return error("INTERNAL_ERROR", "Ошибка базы данных", 500)

        return handle


router = APIRouter(route_class=AdminRoute)


def admin_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise AuthError("нет токена")
    return get_current_user(credentials)


def user_dto(row: UserRecord) -> dict:
    return {
        "id": row.id,
        "email": row.email,
        "role": row.role,
        "is_blocked": row.is_blocked,
        "created_at": row.created_at.isoformat(),
        "blocked_at": row.blocked_at.isoformat() if row.blocked_at else None,
    }


@router.get("/api/admin/users")
def list_users(user: dict = Depends(admin_user)):
    if user["role"] != "admin":
        return error("FORBIDDEN", "Нет прав администратора", 403)
    with Session(get_engine()) as session:
        users = session.scalars(select(UserRecord).order_by(UserRecord.id))
        return {"users": [user_dto(row) for row in users]}


class AdminUser(User):
    blocked_at: str | None = None


class BlockRequest(BaseModel):
    is_blocked: bool


@router.post("/api/admin/users/{user_id}/block", response_model=AdminUser)
def set_blocked(user_id: int, payload: BlockRequest, user: dict = Depends(admin_user)):
    if user["role"] != "admin":
        return error("FORBIDDEN", "Нет прав администратора", 403)
    if user_id == user["id"] and payload.is_blocked:
        return error("SELF_BLOCK", "Нельзя заблокировать себя", 400)

    blocked_at = None
    if payload.is_blocked:
        blocked_at = case(
            (UserRecord.is_blocked.is_(True), UserRecord.blocked_at),
            else_=func.now(),
        )
    statement = (
        update(UserRecord)
        .where(UserRecord.id == user_id)
        .values(is_blocked=payload.is_blocked, blocked_at=blocked_at)
        .returning(UserRecord)
    )
    with Session(get_engine()) as session, session.begin():
        row = session.scalars(statement).one_or_none()
        if row is None:
            return error("USER_NOT_FOUND", "Пользователь не найден", 404)
        return user_dto(row)


class AdminLink(BaseModel):
    id: int
    code: str
    url: str
    owner_id: int | None


@router.get("/api/admin/links")
def list_links(user: dict = Depends(admin_user)):
    if user["role"] != "admin":
        return error("FORBIDDEN", "Нет прав администратора", 403)
    statement = select(
        LinkRecord.id, LinkRecord.code, LinkRecord.url, LinkRecord.owner_id
    ).order_by(LinkRecord.id)
    with Session(get_engine()) as session:
        return {"links": [AdminLink(**row) for row in session.execute(statement).mappings()]}


@router.delete("/api/admin/links/{link_id}", status_code=204)
def delete_link(link_id: int, user: dict = Depends(admin_user)):
    if user["role"] != "admin":
        return error("FORBIDDEN", "Нет прав администратора", 403)
    statement = delete(LinkRecord).where(LinkRecord.id == link_id).returning(LinkRecord.id)
    with Session(get_engine()) as session, session.begin():
        deleted_id = session.scalar(statement)
    if deleted_id is None:
        return error("LINK_NOT_FOUND", "Ссылка не найдена", 404)
    return Response(status_code=204)
