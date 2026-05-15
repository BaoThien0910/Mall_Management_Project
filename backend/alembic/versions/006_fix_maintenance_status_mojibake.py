"""fix corrupted 'bảo' in maintenance status (b?o -> bảo)

Revision ID: 006
Revises: 005
Create Date: 2026-05-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.enums import TenantStatus

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    fixed = TenantStatus.MAINTENANCE.value
    # Same mojibake patterns handled in canonical_tenant_status_string
    bad_variants = [
        "\u00d0ang b?o trì",
        "\u0110ang b?o trì",
    ]
    for bad in bad_variants:
        op.execute(
            sa.text("UPDATE tenants SET status = :fixed WHERE status = :bad").bindparams(
                fixed=fixed,
                bad=bad,
            )
        )


def downgrade() -> None:
    pass
