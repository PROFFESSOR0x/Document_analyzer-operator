"""Add application settings and audit log tables.

Revision ID: 20260101_000200_add_settings
Revises: 20260101_000100_add_llm_providers
Create Date: 2026-01-01 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260101_000200_add_settings'
down_revision: Union[str, None] = '20260101_000100_add_llm_providers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create application_settings and setting_audit_logs tables."""
    
    # Create application_settings table
    op.create_table(
        'application_settings',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(20), nullable=False, default='string'),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_secret', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_editable', sa.Boolean(), nullable=False, default=True),
        sa.Column('validation_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('updated_by_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_application_settings_key', 'application_settings', ['key'], unique=True)
    op.create_index('ix_application_settings_category', 'application_settings', ['category'])
    
    # Create setting_audit_logs table
    op.create_table(
        'setting_audit_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('setting_id', sa.String(36), nullable=False),
        sa.Column('changed_by_id', sa.String(36), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['setting_id'], ['application_settings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_setting_audit_logs_setting_id', 'setting_audit_logs', ['setting_id'])
    
    # Seed default settings
    seed_default_settings()


def downgrade() -> None:
    """Drop application_settings and setting_audit_logs tables."""
    op.drop_table('setting_audit_logs')
    op.drop_table('application_settings')


def seed_default_settings() -> None:
    """Seed default application settings."""
    from datetime import datetime, timezone
    from uuid import uuid4
    
    # Connect to the database
    connection = op.get_bind()
    
    default_settings = [
        # LLM Settings
        {
            'id': str(uuid4()),
            'key': 'llm.default_provider',
            'value': 'openai',
            'value_type': 'string',
            'category': 'llm',
            'description': 'Default LLM provider to use',
            'is_secret': False,
            'is_editable': True,
            'default_value': 'openai',
        },
        {
            'id': str(uuid4()),
            'key': 'llm.openai_api_key',
            'value': None,
            'value_type': 'secret',
            'category': 'llm',
            'description': 'OpenAI API key',
            'is_secret': True,
            'is_editable': True,
            'default_value': None,
        },
        {
            'id': str(uuid4()),
            'key': 'llm.openai_base_url',
            'value': 'https://api.openai.com/v1',
            'value_type': 'string',
            'category': 'llm',
            'description': 'OpenAI API base URL',
            'is_secret': False,
            'is_editable': True,
            'default_value': 'https://api.openai.com/v1',
        },
        {
            'id': str(uuid4()),
            'key': 'llm.anthropic_api_key',
            'value': None,
            'value_type': 'secret',
            'category': 'llm',
            'description': 'Anthropic API key',
            'is_secret': True,
            'is_editable': True,
            'default_value': None,
        },
        {
            'id': str(uuid4()),
            'key': 'llm.groq_api_key',
            'value': None,
            'value_type': 'secret',
            'category': 'llm',
            'description': 'Groq API key',
            'is_secret': True,
            'is_editable': True,
            'default_value': None,
        },
        {
            'id': str(uuid4()),
            'key': 'llm.temperature',
            'value': '0.7',
            'value_type': 'float',
            'category': 'llm',
            'description': 'Default temperature for LLM responses',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'number', 'minimum': 0, 'maximum': 2},
            'default_value': '0.7',
        },
        {
            'id': str(uuid4()),
            'key': 'llm.max_tokens',
            'value': '4096',
            'value_type': 'integer',
            'category': 'llm',
            'description': 'Default max tokens for LLM responses',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'integer', 'minimum': 1, 'maximum': 128000},
            'default_value': '4096',
        },
        # Database Settings
        {
            'id': str(uuid4()),
            'key': 'database.pool_size',
            'value': '10',
            'value_type': 'integer',
            'category': 'database',
            'description': 'Database connection pool size',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'integer', 'minimum': 1, 'maximum': 100},
            'default_value': '10',
        },
        {
            'id': str(uuid4()),
            'key': 'database.pool_timeout',
            'value': '30',
            'value_type': 'integer',
            'category': 'database',
            'description': 'Database pool timeout in seconds',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'integer', 'minimum': 1, 'maximum': 300},
            'default_value': '30',
        },
        {
            'id': str(uuid4()),
            'key': 'database.echo_sql',
            'value': 'false',
            'value_type': 'boolean',
            'category': 'database',
            'description': 'Echo SQL queries to logs',
            'is_secret': False,
            'is_editable': True,
            'default_value': 'false',
        },
        # Redis Settings
        {
            'id': str(uuid4()),
            'key': 'redis.db',
            'value': '0',
            'value_type': 'integer',
            'category': 'redis',
            'description': 'Redis database number',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'integer', 'minimum': 0, 'maximum': 15},
            'default_value': '0',
        },
        {
            'id': str(uuid4()),
            'key': 'redis.ttl',
            'value': '3600',
            'value_type': 'integer',
            'category': 'redis',
            'description': 'Default TTL for Redis sessions in seconds',
            'is_secret': False,
            'is_editable': True,
            'default_value': '3600',
        },
        # Security Settings
        {
            'id': str(uuid4()),
            'key': 'security.jwt_expiry_minutes',
            'value': '30',
            'value_type': 'integer',
            'category': 'security',
            'description': 'JWT token expiry in minutes',
            'is_secret': False,
            'is_editable': True,
            'default_value': '30',
        },
        {
            'id': str(uuid4()),
            'key': 'security.max_login_attempts',
            'value': '5',
            'value_type': 'integer',
            'category': 'security',
            'description': 'Maximum login attempts before lockout',
            'is_secret': False,
            'is_editable': True,
            'default_value': '5',
        },
        {
            'id': str(uuid4()),
            'key': 'security.session_timeout_minutes',
            'value': '60',
            'value_type': 'integer',
            'category': 'security',
            'description': 'Session timeout in minutes',
            'is_secret': False,
            'is_editable': True,
            'default_value': '60',
        },
        {
            'id': str(uuid4()),
            'key': 'security.cors_origins',
            'value': '["http://localhost:3000", "http://localhost:8080"]',
            'value_type': 'json',
            'category': 'security',
            'description': 'Allowed CORS origins',
            'is_secret': False,
            'is_editable': True,
            'default_value': '["http://localhost:3000", "http://localhost:8080"]',
        },
        # Application Settings
        {
            'id': str(uuid4()),
            'key': 'app.debug',
            'value': 'false',
            'value_type': 'boolean',
            'category': 'application',
            'description': 'Debug mode flag',
            'is_secret': False,
            'is_editable': True,
            'default_value': 'false',
        },
        {
            'id': str(uuid4()),
            'key': 'app.log_level',
            'value': 'INFO',
            'value_type': 'string',
            'category': 'application',
            'description': 'Logging level (DEBUG, INFO, WARNING, ERROR)',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'string', 'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR']},
            'default_value': 'INFO',
        },
        {
            'id': str(uuid4()),
            'key': 'app.workers',
            'value': '1',
            'value_type': 'integer',
            'category': 'application',
            'description': 'Number of worker processes',
            'is_secret': False,
            'is_editable': True,
            'default_value': '1',
        },
        {
            'id': str(uuid4()),
            'key': 'app.max_upload_size_mb',
            'value': '10',
            'value_type': 'integer',
            'category': 'application',
            'description': 'Maximum upload file size in MB',
            'is_secret': False,
            'is_editable': True,
            'default_value': '10',
        },
        # UI Settings
        {
            'id': str(uuid4()),
            'key': 'ui.theme',
            'value': 'system',
            'value_type': 'string',
            'category': 'ui',
            'description': 'Default UI theme (light, dark, system)',
            'is_secret': False,
            'is_editable': True,
            'validation_schema': {'type': 'string', 'enum': ['light', 'dark', 'system']},
            'default_value': 'system',
        },
        {
            'id': str(uuid4()),
            'key': 'ui.page_size',
            'value': '20',
            'value_type': 'integer',
            'category': 'ui',
            'description': 'Default page size for lists',
            'is_secret': False,
            'is_editable': True,
            'default_value': '20',
        },
        {
            'id': str(uuid4()),
            'key': 'ui.enable_websocket',
            'value': 'true',
            'value_type': 'boolean',
            'category': 'ui',
            'description': 'Enable WebSocket real-time updates',
            'is_secret': False,
            'is_editable': True,
            'default_value': 'true',
        },
    ]
    
    now = datetime.now(timezone.utc).isoformat()
    
    for setting in default_settings:
        connection.execute(
            sa.text("""
                INSERT INTO application_settings 
                (id, key, value, value_type, category, description, is_secret, is_editable, 
                 validation_schema, default_value, created_at, updated_at, is_deleted)
                VALUES 
                (:id, :key, :value, :value_type, :category, :description, :is_secret, :is_editable,
                 :validation_schema, :default_value, :created_at, :updated_at, :is_deleted)
            """),
            {
                **setting,
                'validation_schema': sa.func.to_jsonb(setting['validation_schema']) if setting.get('validation_schema') else None,
                'created_at': now,
                'updated_at': now,
                'is_deleted': False,
            }
        )
