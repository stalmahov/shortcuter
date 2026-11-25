"""Исходная схема до первой миграции ЛР8."""

from pathlib import Path

from alembic import op

revision = "000"
down_revision = None


def upgrade():
    connection = op.get_bind()
    sql = Path(__file__).with_name("baseline.sql").read_text()
    connection.exec_driver_sql(sql)


def downgrade():
    raise RuntimeError("Restore a verified backup to roll back the initial schema")
