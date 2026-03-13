"""Initial schema creation.

Revision ID: 001
Revises: 
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('role', sa.String(20), nullable=False, default='user'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Create agent_types table
    op.create_table(
        'agent_types',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('default_config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agent_types_name', 'agent_types', ['name'], unique=True)
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('agent_type_id', sa.String(36), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='idle'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=dict),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('model', sa.String(50), nullable=False, default='gpt-4'),
        sa.Column('temperature', sa.Float(), nullable=False, default=0.7),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('version', sa.String(20), nullable=False, default='1.0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_type_id'], ['agent_types.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agents_name', 'agents', ['name'])
    op.create_index('ix_agents_owner_id', 'agents', ['owner_id'])
    op.create_index('ix_agents_agent_type_id', 'agents', ['agent_type_id'])
    
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('type', sa.String(20), nullable=False, default='personal'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=dict),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False, default=1),
        sa.Column('storage_used', sa.Integer(), nullable=False, default=0),
        sa.Column('storage_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workspaces_name', 'workspaces', ['name'])
    op.create_index('ix_workspaces_owner_id', 'workspaces', ['owner_id'])
    
    # Create knowledge_entities table
    op.create_table(
        'knowledge_entities',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('parent_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('entity_type', sa.String(30), nullable=False, default='document'),
        sa.Column('source', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=list),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=dict),
        sa.Column('embedding', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('version', sa.String(20), nullable=False, default='1.0.0'),
        sa.Column('is_indexed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['knowledge_entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_knowledge_entities_workspace_id', 'knowledge_entities', ['workspace_id'])
    op.create_index('ix_knowledge_entities_parent_id', 'knowledge_entities', ['parent_id'])
    op.create_index('ix_knowledge_entities_entity_type', 'knowledge_entities', ['entity_type'])
    op.create_index('ix_knowledge_entities_workspace_type', 'knowledge_entities', ['workspace_id', 'entity_type'])
    op.create_index('ix_knowledge_entities_tags', 'knowledge_entities', ['tags'], postgresql_using='gin')
    
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('definition', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=dict),
        sa.Column('trigger_type', sa.String(20), nullable=False, default='manual'),
        sa.Column('trigger_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('version', sa.String(20), nullable=False, default='1.0.0'),
        sa.Column('execution_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflows_name', 'workflows', ['name'])
    op.create_index('ix_workflows_owner_id', 'workflows', ['owner_id'])
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('priority', sa.String(20), nullable=False, default='medium'),
        sa.Column('agent_id', sa.String(36), nullable=True),
        sa.Column('workflow_id', sa.String(36), nullable=True),
        sa.Column('parent_task_id', sa.String(36), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False, default=0),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_agent_id', 'tasks', ['agent_id'])
    op.create_index('ix_tasks_workflow_id', 'tasks', ['workflow_id'])
    op.create_index('ix_tasks_parent_task_id', 'tasks', ['parent_task_id'])
    
    # Create validation_results table
    op.create_table(
        'validation_results',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('task_id', sa.String(36), nullable=False),
        sa.Column('validator_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('severity', sa.String(20), nullable=False, default='info'),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rule_id', sa.String(50), nullable=True),
        sa.Column('rule_name', sa.String(100), nullable=True),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_validation_results_task_id', 'validation_results', ['task_id'])
    op.create_index('ix_validation_results_status', 'validation_results', ['status'])
    op.create_index('ix_validation_results_severity', 'validation_results', ['severity'])
    op.create_index('ix_validation_results_category', 'validation_results', ['category'])
    op.create_index('ix_validation_results_rule_id', 'validation_results', ['rule_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('validation_results')
    op.drop_table('tasks')
    op.drop_table('workflows')
    op.drop_table('knowledge_entities')
    op.drop_table('workspaces')
    op.drop_table('agents')
    op.drop_table('agent_types')
    op.drop_table('users')
