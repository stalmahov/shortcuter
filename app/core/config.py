"""Настройки из окружения. Секретов в коде нет (ТЗ 4.1.5)."""

import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_TTL_SECONDS = 86400  # 24 часа

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # 5433: хостовый 5432 занят локальным postgres.exe (см. docker-compose.yml)
    "postgresql+psycopg://shortcuter:shortcuter@localhost:5433/shortcuter",
)

# База для short_url в ответах. Меняется per-окружение (прод-домен),
# поэтому short_url вычисляется, а не хранится в БД.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
