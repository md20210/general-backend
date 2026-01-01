"""add documents field for PDF storage

Revision ID: add_documents_field
Revises:
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'add_docs_field_001'  # Shortened to fit VARCHAR(32)
down_revision = 'job_assistant_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add documents JSONB field to job_applications table (skip if exists)
    bind = op.get_bind()
    inspector = inspect(bind)

    # Check if column already exists
    columns = [col['name'] for col in inspector.get_columns('job_applications')]
    if 'documents' not in columns:
        op.add_column('job_applications',
            sa.Column('documents', JSONB, nullable=False, server_default='{}'))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col['name'] for col in inspector.get_columns('job_applications')]
    if 'documents' in columns:
        op.drop_column('job_applications', 'documents')
