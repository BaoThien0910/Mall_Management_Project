# File: alembic/versions/20260524_add_meter_calculated_amounts.py
"""add calculated meter reading amounts

Revision ID: 20260524_add_meter_calculated_amounts
Revises: <PUT_PREVIOUS_REVISION_ID_HERE>
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "meter_calculated_amounts"
down_revision = "67d26745babc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "SODIEN_TIEUTHU",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "SONUOC_TIEUTHU",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "DONGIA_DIEN",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="3500",
        ),
    )
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "DONGIA_NUOC",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="2200",
        ),
    )
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "TIENDIEN",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "CHISODIENNUOC",
        sa.Column(
            "TIENNUOC",
            sa.DECIMAL(18, 2),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_check_constraint(
        "CK_CHISODIENNUOC_SODIEN_TIEUTHU",
        "CHISODIENNUOC",
        "SODIEN_TIEUTHU >= 0",
    )
    op.create_check_constraint(
        "CK_CHISODIENNUOC_SONUOC_TIEUTHU",
        "CHISODIENNUOC",
        "SONUOC_TIEUTHU >= 0",
    )
    op.create_check_constraint(
        "CK_CHISODIENNUOC_DONGIA_DIEN",
        "CHISODIENNUOC",
        "DONGIA_DIEN > 0",
    )
    op.create_check_constraint(
        "CK_CHISODIENNUOC_DONGIA_NUOC",
        "CHISODIENNUOC",
        "DONGIA_NUOC > 0",
    )
    op.create_check_constraint(
        "CK_CHISODIENNUOC_TIENDIEN",
        "CHISODIENNUOC",
        "TIENDIEN >= 0",
    )
    op.create_check_constraint(
        "CK_CHISODIENNUOC_TIENNUOC",
        "CHISODIENNUOC",
        "TIENNUOC >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "CK_CHISODIENNUOC_TIENNUOC",
        "CHISODIENNUOC",
        type_="check",
    )
    op.drop_constraint(
        "CK_CHISODIENNUOC_TIENDIEN",
        "CHISODIENNUOC",
        type_="check",
    )
    op.drop_constraint(
        "CK_CHISODIENNUOC_DONGIA_NUOC",
        "CHISODIENNUOC",
        type_="check",
    )
    op.drop_constraint(
        "CK_CHISODIENNUOC_DONGIA_DIEN",
        "CHISODIENNUOC",
        type_="check",
    )
    op.drop_constraint(
        "CK_CHISODIENNUOC_SONUOC_TIEUTHU",
        "CHISODIENNUOC",
        type_="check",
    )
    op.drop_constraint(
        "CK_CHISODIENNUOC_SODIEN_TIEUTHU",
        "CHISODIENNUOC",
        type_="check",
    )

    op.drop_column("CHISODIENNUOC", "TIENNUOC")
    op.drop_column("CHISODIENNUOC", "TIENDIEN")
    op.drop_column("CHISODIENNUOC", "DONGIA_NUOC")
    op.drop_column("CHISODIENNUOC", "DONGIA_DIEN")
    op.drop_column("CHISODIENNUOC", "SONUOC_TIEUTHU")
    op.drop_column("CHISODIENNUOC", "SODIEN_TIEUTHU")
