# File: alembic/script.py.mako
"""create initial tables

Revision ID: 67d26745babc
Revises: 
Create Date: 2026-05-19 12:53:32.875735
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


# revision identifiers, used by Alembic.
revision: str = '67d26745babc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Áp dụng thay đổi schema."""
    pass


def downgrade() -> None:
    """Hoàn tác thay đổi schema."""
    pass