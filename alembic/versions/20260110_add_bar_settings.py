"""Add bar settings table

Revision ID: 20260110_bar_settings
Revises: 20260110_update_bar
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '20260110_bar_settings'
down_revision = '20260110_update_bar'
branch_labels = None
depends_on = None


def upgrade():
    """Create bar_settings table for admin configuration."""
    op.create_table(
        'bar_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('llm_provider', sa.String(50), default='ollama'),
        sa.Column('grok_api_key', sa.String(500), nullable=True),
        sa.Column('ollama_model', sa.String(100), default='llama3.2:3b'),
        sa.Column('auto_speak_enabled', sa.Boolean(), default=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default settings
    op.execute("""
        INSERT INTO bar_settings (id, llm_provider, ollama_model, auto_speak_enabled, contact_email, created_at, updated_at)
        VALUES (1, 'ollama', 'llama3.2:3b', true, NULL, NOW(), NOW());
    """)


def downgrade():
    """Drop bar_settings table."""
    op.drop_table('bar_settings')
