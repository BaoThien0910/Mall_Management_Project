"""restore DEFAULT on users.updated_at (002 dropped it by mistake)

Revision ID: 003
Revises: 002
Create Date: 2026-05-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table: str, column: str) -> bool:
    insp = inspect(bind)
    cols = insp.get_columns(table)
    return any(c["name"].lower() == column.lower() for c in cols)


def upgrade() -> None:
    bind = op.get_bind()
    if not _has_column(bind, "users", "updated_at"):
        return
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("(SYSUTCDATETIME())"),
    )


def downgrade() -> None:
    # Leave DB default in place; dropping it breaks INSERTs again.
    pass
