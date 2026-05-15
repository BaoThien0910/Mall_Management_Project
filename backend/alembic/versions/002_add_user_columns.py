"""add user columns to match ORM (full_name, phone, role, ...)

Revision ID: 002
Revises: 001
Create Date: 2026-05-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table: str, column: str) -> bool:
    insp = inspect(bind)
    cols = insp.get_columns(table)
    return any(c["name"].lower() == column.lower() for c in cols)


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_column(bind, "users", "full_name"):
        op.add_column(
            "users",
            sa.Column(
                "full_name",
                sa.String(255),
                nullable=False,
                server_default=sa.text("N''"),
            ),
        )
        op.alter_column(
            "users",
            "full_name",
            existing_type=sa.String(255),
            nullable=False,
            server_default=None,
        )

    if not _has_column(bind, "users", "phone"):
        op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

    if not _has_column(bind, "users", "role"):
        op.add_column(
            "users",
            sa.Column(
                "role",
                sa.String(20),
                nullable=False,
                server_default=sa.text("(N'staff')"),
            ),
        )
        op.alter_column(
            "users",
            "role",
            existing_type=sa.String(20),
            nullable=False,
            server_default=None,
        )

    if not _has_column(bind, "users", "department"):
        op.add_column("users", sa.Column("department", sa.String(255), nullable=True))

    if not _has_column(bind, "users", "tenant_id"):
        op.add_column("users", sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_users_tenant_id_tenants",
            "users",
            "tenants",
            ["tenant_id"],
            ["id"],
        )

    if not _has_column(bind, "users", "updated_at"):
        # Keep server default: SQLAlchemy omits this column on INSERT and relies on the DB.
        op.add_column(
            "users",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("(SYSUTCDATETIME())"),
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _has_column(bind, "users", "updated_at"):
        op.drop_column("users", "updated_at")

    if _has_column(bind, "users", "tenant_id"):
        op.drop_constraint("fk_users_tenant_id_tenants", "users", type_="foreignkey")
        op.drop_column("users", "tenant_id")

    if _has_column(bind, "users", "department"):
        op.drop_column("users", "department")

    if _has_column(bind, "users", "role"):
        op.drop_column("users", "role")

    if _has_column(bind, "users", "phone"):
        op.drop_column("users", "phone")

    if _has_column(bind, "users", "full_name"):
        op.drop_column("users", "full_name")
