"""Add tax case tables

Revision ID: 20260124_add_tax_case_tables
Revises: 20260119_folder_tracking
Create Date: 2026-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '20260124_add_tax_case_tables'
down_revision = '20260119_folder_tracking'  # Updated to use new revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables already exist before creating
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create tax_cases table only if it doesn't exist
    if 'tax_cases' not in existing_tables:
        op.create_table(
            'tax_cases',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False, index=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='created', index=True),
            sa.Column('validated', sa.Boolean(), nullable=False, server_default='false', index=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # Create tax_case_folders table only if it doesn't exist
    if 'tax_case_folders' not in existing_tables:
        op.create_table(
            'tax_case_folders',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('tax_case_id', sa.Integer(), sa.ForeignKey('tax_cases.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('parent_id', sa.Integer(), sa.ForeignKey('tax_case_folders.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('path', sa.String(2000), nullable=False, index=True),
            sa.Column('level', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # Create tax_case_documents table only if it doesn't exist
    if 'tax_case_documents' not in existing_tables:
        op.create_table(
            'tax_case_documents',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('tax_case_id', sa.Integer(), sa.ForeignKey('tax_cases.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('folder_id', sa.Integer(), sa.ForeignKey('tax_case_folders.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('doc_type', sa.String(50), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('validated', sa.Boolean(), nullable=False, server_default='false', index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # Create tax_case_extracted_data table only if it doesn't exist
    if 'tax_case_extracted_data' not in existing_tables:
        op.create_table(
            'tax_case_extracted_data',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('tax_case_id', sa.Integer(), sa.ForeignKey('tax_cases.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('document_id', sa.Integer(), sa.ForeignKey('tax_case_documents.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('field_name', sa.String(255), nullable=False, index=True),
            sa.Column('field_value', sa.Text(), nullable=False),
            sa.Column('field_type', sa.String(50), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=True),
            sa.Column('confirmed', sa.Boolean(), nullable=False, server_default='false', index=True),
            sa.Column('edited', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('original_value', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )


def downgrade():
    op.drop_table('tax_case_extracted_data')
    op.drop_table('tax_case_documents')
    op.drop_table('tax_case_folders')
    op.drop_table('tax_cases')
