"""merge heads utm finance

Revision ID: 7f8e9d0c1b2a
Revises: df66d17ea018, 1a2b3c4d5e6f
Create Date: 2025-09-23 00:05:00.000000
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = '7f8e9d0c1b2a'
down_revision = ('df66d17ea018', '1a2b3c4d5e6f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a merge migration; no operations are required.
    pass


def downgrade() -> None:
    # This is a merge migration; no operations are required.
    pass


