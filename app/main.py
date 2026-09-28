from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .core.errors import error, validation_handler
from .core.security import AuthError, UserBlocked
from .routers import admin, auth, my, public

app = FastAPI(title="Shortcuter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["*"] для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Любая ошибка валидации тела → 400 в едином формате (ТЗ 4.1.3),
# а не 422 от FastAPI. См. core/errors.py.
app.add_exception_handler(RequestValidationError, validation_handler)


@app.exception_handler(AuthError)
async def auth_handler(request, exc):
    return error("UNAUTHORIZED", "Нет или невалидный токен", 401)


@app.exception_handler(UserBlocked)
async def blocked_handler(request, exc):
    return error("USER_BLOCKED", "Пользователь заблокирован", 403)


@app.get("/health")
def health():
    # Вне спеки: технический эндпоинт для docker/healthcheck и TeamCity.
    # Объявлен ДО роутеров: иначе GET /{code} перехватит /health.
    return {"status": "ok"}


app.include_router(public.router)
app.include_router(auth.router)
app.include_router(my.router)
app.include_router(admin.router)
