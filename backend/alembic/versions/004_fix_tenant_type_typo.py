"""fix typo tenant_type Van phòng -> Văn phòng

Revision ID: 004
Revises: 003
Create Date: 2026-05-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE tenants SET tenant_type = N'Văn phòng' "
            "WHERE tenant_type = N'Van phòng'"
        )
    )


def downgrade() -> None:
    # Do not re-introduce typo into data.
    pass
