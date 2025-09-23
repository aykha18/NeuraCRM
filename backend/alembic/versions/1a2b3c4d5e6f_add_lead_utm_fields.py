"""add lead utm fields

Revision ID: 1a2b3c4d5e6f
Revises: 474aa80a0e1b
Create Date: 2025-09-23 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '474aa80a0e1b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('leads') as batch_op:
        batch_op.add_column(sa.Column('utm_source', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('utm_medium', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('utm_campaign', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('utm_term', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('utm_content', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('referrer_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('landing_page_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('gclid', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('fbclid', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('leads') as batch_op:
        batch_op.drop_column('fbclid')
        batch_op.drop_column('gclid')
        batch_op.drop_column('landing_page_url')
        batch_op.drop_column('referrer_url')
        batch_op.drop_column('utm_content')
        batch_op.drop_column('utm_term')
        batch_op.drop_column('utm_campaign')
        batch_op.drop_column('utm_medium')
        batch_op.drop_column('utm_source')


