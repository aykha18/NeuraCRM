"""add_ai_summary_fields_only

Revision ID: bb6b98b2a151
Revises: 0411a2a17f98
Create Date: 2025-10-02 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb6b98b2a151'
down_revision: Union[str, Sequence[str], None] = '0411a2a17f98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add AI summary fields to support_tickets table
    op.add_column('support_tickets', sa.Column('ai_summary', sa.Text(), nullable=True))
    op.add_column('support_tickets', sa.Column('ai_summary_generated_at', sa.DateTime(), nullable=True))
    op.add_column('support_tickets', sa.Column('ai_summary_model', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove AI summary fields from support_tickets table
    op.drop_column('support_tickets', 'ai_summary_model')
    op.drop_column('support_tickets', 'ai_summary_generated_at')
    op.drop_column('support_tickets', 'ai_summary')