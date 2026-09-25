"""Зона админа (Саня). Пока заглушки."""

from fastapi import APIRouter
from pydantic import BaseModel

from ..schemas import User

router = APIRouter()


@router.get("/api/admin/users")
def list_users():
    # TODO: проверка role=admin → 403.
    return {"users": []}


class BlockRequest(BaseModel):
    is_blocked: bool


@router.post("/api/admin/users/{user_id}/block", response_model=User)
def set_blocked(user_id: int, payload: BlockRequest):
    # TODO: role=admin → 403, себя → 400 SELF_BLOCK, нет пользователя → 404.
    return {
        "id": user_id,
        "email": "user@example.com",
        "role": "user",
        "is_blocked": payload.is_blocked,
    }
