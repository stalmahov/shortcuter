"""Подключение к PostgreSQL и общий пул соединений."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from .core.config import DATABASE_URL


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)
