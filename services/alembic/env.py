"""Запуск миграций на базе, указанной в окружении."""

import os

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.models import Base


def run_migrations():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        if not os.environ.get("PGSERVICE"):
            raise RuntimeError("Set DATABASE_URL or PGSERVICE before running Alembic")
        database_url = "postgresql+psycopg://"

    if context.is_offline_mode():
        raise RuntimeError("Run Alembic against PostgreSQL; SQL files are in services/migrations")

    engine = create_engine(database_url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.exec_driver_sql("SELECT pg_advisory_xact_lock(812345, 1)")
        connection.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS shortcuter_migrations")
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            version_table_schema="shortcuter_migrations",
        )
        context.run_migrations()
    engine.dispose()


run_migrations()
