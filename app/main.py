from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .core.errors import validation_handler
from .routers import admin, auth, my, public

app = FastAPI(title="Shortcuter API", version="1.0.0")

# Любая ошибка валидации тела → 400 в едином формате (ТЗ 4.1.3),
# а не 422 от FastAPI. См. core/errors.py.
app.add_exception_handler(RequestValidationError, validation_handler)


@app.get("/health")
def health():
    # Вне спеки: технический эндпоинт для docker/healthcheck и TeamCity.
    # Объявлен ДО роутеров: иначе GET /{code} перехватит /health.
    return {"status": "ok"}


app.include_router(public.router)
app.include_router(auth.router)
app.include_router(my.router)
app.include_router(admin.router)
