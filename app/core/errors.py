"""Единый формат ошибок (ТЗ 4.1.3): {"error": {"code", "message"}}."""

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"error": {"code": code, "message": message}}
    )


async def validation_handler(request, exc: RequestValidationError):
    # TODO: различать коды по эндпоинту (BAD_URL / BAD_ALIAS / WEAK_PASSWORD...).
    # Пока общий код — словарь в docs/api-contracts.md, разд. 6 дополним.
    return error("BAD_REQUEST", "Некорректный запрос", 400)
