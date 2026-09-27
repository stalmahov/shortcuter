"""Подключение к Postgres. Реальное использование — со следующим шагом.

Владелец слоя: Саня (ORM-модели, миграции Alembic к ЛР8).
"""

from .config import DATABASE_URL


def get_engine():
    # Локальный импорт: без настроенной БД модуль не тянет драйвер.
    from sqlalchemy import create_engine

    return create_engine(DATABASE_URL)
