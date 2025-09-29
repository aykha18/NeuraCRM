"""Add payment models for Stripe integration

Revision ID: add_payment_models
Revises: add_callrecord_only
Create Date: 2024-12-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_payment_models'
down_revision = 'add_callrecord_only'
branch_labels = None
depends_on = None


def upgrade():
    # Create payment_methods table
    op.create_table('payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stripe_payment_method_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('last4', sa.String(), nullable=True),
        sa.Column('exp_month', sa.Integer(), nullable=True),
        sa.Column('exp_year', sa.Integer(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_method_id')
    )
    
    # Create stripe_subscription_plans table
    op.create_table('stripe_subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stripe_price_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('interval', sa.String(), nullable=False),
        sa.Column('interval_count', sa.Integer(), nullable=True),
        sa.Column('trial_period_days', sa.Integer(), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_price_id')
    )
    
    # Create stripe_subscriptions table
    op.create_table('stripe_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('payment_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['stripe_subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    
    # Create stripe_payments table
    op.create_table('stripe_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('payment_method_id', sa.Integer(), nullable=True),
        sa.Column('failure_reason', sa.String(), nullable=True),
        sa.Column('payment_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['stripe_subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_intent_id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('stripe_payments')
    op.drop_table('stripe_subscriptions')
    op.drop_table('stripe_subscription_plans')
    op.drop_table('payment_methods')
