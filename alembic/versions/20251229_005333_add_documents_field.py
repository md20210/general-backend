"""add documents field for PDF storage

Revision ID: add_documents_field  
Revises:
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'add_documents_field'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add documents JSONB field to job_applications table
    op.add_column('job_applications', 
        sa.Column('documents', JSONB, nullable=False, server_default='{}'))


def downgrade() -> None:
    op.drop_column('job_applications', 'documents')
