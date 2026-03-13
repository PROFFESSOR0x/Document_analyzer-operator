"""Add LLM provider and usage log tables.

Revision ID: 20260101_000100
Revises: 20260101_000000
Create Date: 2026-01-01 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260101_000100'
down_revision: Union[str, None] = '20260101_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create LLM providers table
    op.create_table(
        'llm_providers',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider_type', sa.String(50), nullable=False),
        sa.Column('base_url', sa.Text(), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_llm_providers_name'), 'llm_providers', ['name'], unique=True)
    op.create_index(op.f('ix_llm_providers_provider_type'), 'llm_providers', ['provider_type'], unique=False)
    op.create_index(op.f('ix_llm_providers_is_active'), 'llm_providers', ['is_active'], unique=False)
    op.create_index(op.f('ix_llm_providers_is_default'), 'llm_providers', ['is_default'], unique=False)

    # Create LLM usage logs table
    op.create_table(
        'llm_usage_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('provider_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('agent_id', sa.String(36), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False, default=0),
        sa.Column('tokens_output', sa.Integer(), nullable=False, default=0),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['llm_providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_llm_usage_logs_provider_id'), 'llm_usage_logs', ['provider_id'], unique=False)
    op.create_index(op.f('ix_llm_usage_logs_user_id'), 'llm_usage_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_llm_usage_logs_agent_id'), 'llm_usage_logs', ['agent_id'], unique=False)
    op.create_index(op.f('ix_llm_usage_logs_created_at'), 'llm_usage_logs', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(op.f('ix_llm_usage_logs_created_at'), table_name='llm_usage_logs')
    op.drop_index(op.f('ix_llm_usage_logs_agent_id'), table_name='llm_usage_logs')
    op.drop_index(op.f('ix_llm_usage_logs_user_id'), table_name='llm_usage_logs')
    op.drop_index(op.f('ix_llm_usage_logs_provider_id'), table_name='llm_usage_logs')
    op.drop_table('llm_usage_logs')
    
    op.drop_index(op.f('ix_llm_providers_is_default'), table_name='llm_providers')
    op.drop_index(op.f('ix_llm_providers_is_active'), table_name='llm_providers')
    op.drop_index(op.f('ix_llm_providers_provider_type'), table_name='llm_providers')
    op.drop_index(op.f('ix_llm_providers_name'), table_name='llm_providers')
    op.drop_table('llm_providers')
