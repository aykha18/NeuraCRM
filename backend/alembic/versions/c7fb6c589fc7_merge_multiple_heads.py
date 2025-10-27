"""Merge multiple heads

Revision ID: c7fb6c589fc7
Revises: aa6b98b2a150, bb6b98b2a151
Create Date: 2025-10-25 11:01:30.825631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7fb6c589fc7'
down_revision: Union[str, Sequence[str], None] = ('aa6b98b2a150', 'bb6b98b2a151')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
