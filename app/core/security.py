"""JWT: выдача и проверка. Реализация — следующим шагом (зона Ивана)."""

from .config import JWT_ALGORITHM, JWT_SECRET, JWT_TTL_SECONDS


def create_token(user_id: int) -> str:
    # TODO: PyJWT, HS256, claims sub=user_id + exp=+24h.
    raise NotImplementedError


def get_user_id(token: str) -> int:
    # TODO: проверка подписи и срока; is_blocked проверяется в БД отдельно.
    raise NotImplementedError
