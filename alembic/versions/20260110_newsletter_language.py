"""Add language column to bar_newsletter

Revision ID: 20260110_newsletter_language
Revises: 20260110_barnews_multilingual
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260110_newsletter_language'
down_revision = '20260110_barnews_multilingual'
branch_labels = None
depends_on = None


def upgrade():
    # Add language column to bar_newsletter table
    op.add_column('bar_newsletter', sa.Column('language', sa.String(length=5), nullable=True, server_default='ca'))


def downgrade():
    # Remove language column from bar_newsletter table
    op.drop_column('bar_newsletter', 'language')
