"""Заголовок ссылки."""

from pathlib import Path

from alembic import op

revision = "001"
down_revision = "000"


def upgrade():
    sql = Path(__file__).resolve().parents[2] / "migrations/V001__add_link_title.sql"
    op.get_bind().exec_driver_sql(sql.read_text())


def downgrade():
    raise RuntimeError("Restore a verified backup to preserve existing link titles")
