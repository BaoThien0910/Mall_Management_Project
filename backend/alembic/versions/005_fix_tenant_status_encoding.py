"""fix status Ð (U+00D0) -> Đ (U+0110) for Vietnamese labels

Revision ID: 005
Revises: 004
Create Date: 2026-05-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.enums import TenantStatus

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bad_occupied = "\u00d0" + TenantStatus.OCCUPIED.value[1:]
    bad_maint = "\u00d0" + TenantStatus.MAINTENANCE.value[1:]
    op.execute(
        sa.text("UPDATE tenants SET status = :fixed WHERE status = :bad").bindparams(
            fixed=TenantStatus.OCCUPIED.value,
            bad=bad_occupied,
        )
    )
    op.execute(
        sa.text("UPDATE tenants SET status = :fixed WHERE status = :bad").bindparams(
            fixed=TenantStatus.MAINTENANCE.value,
            bad=bad_maint,
        )
    )


def downgrade() -> None:
    pass
