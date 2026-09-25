"""Настройки из окружения. Секретов в коде нет (ТЗ 4.1.5)."""

import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_TTL_SECONDS = 86400  # 24 часа

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://shortcuter:shortcuter@localhost:5432/shortcuter",
)
