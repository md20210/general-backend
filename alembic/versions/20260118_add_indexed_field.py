"""Add indexed field to application_documents

Revision ID: 20260118_indexed
Revises: 20260117_add_app
Create Date: 2026-01-18 08:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = '20260118_indexed'
down_revision = '20260117_add_app'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexed column to application_documents table
    op.add_column('application_documents',
        sa.Column('indexed', sa.Boolean(), nullable=False, server_default='false')
    )
    # Add index for faster querying
    op.create_index(
        'ix_application_documents_indexed',
        'application_documents',
        ['indexed']
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_application_documents_indexed', 'application_documents')
    # Remove column
    op.drop_column('application_documents', 'indexed')
