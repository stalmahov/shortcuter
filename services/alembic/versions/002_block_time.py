"""Дата блокировки пользователя."""

from pathlib import Path

from alembic import op

revision = "002"
down_revision = "001"


def upgrade():
    sql = Path(__file__).resolve().parents[2] / "migrations/V002__record_block_time.sql"
    op.get_bind().exec_driver_sql(sql.read_text())


def downgrade():
    raise RuntimeError("Restore a verified backup to preserve existing block dates")
