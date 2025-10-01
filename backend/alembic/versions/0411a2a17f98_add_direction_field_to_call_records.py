"""add_direction_field_to_call_records

Revision ID: 0411a2a17f98
Revises: add_payment_models
Create Date: 2025-10-02 01:39:08.130469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0411a2a17f98'
down_revision: Union[str, Sequence[str], None] = 'add_payment_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add direction field to call_records table
    op.add_column('call_records', sa.Column('direction', sa.String(), nullable=False, server_default='outbound'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove direction field from call_records table
    op.drop_column('call_records', 'direction')
