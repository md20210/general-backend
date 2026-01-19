"""Add application tracker tables

Revision ID: 20260117_add_app
Revises: 20260111_merge_heads
Create Date: 2026-01-17 18:00:00

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID

revision = '20260117_add_app'
down_revision = '20260111_merge_heads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check which tables already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create applications table if it doesn't exist
    if 'applications' not in existing_tables:
        op.create_table(
            'applications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', UUID(as_uuid=True), nullable=False),
            sa.Column('company_name', sa.String(length=255), nullable=False),
            sa.Column('position', sa.String(length=255), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
            sa.Column('upload_path', sa.String(length=500), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_applications_id', 'applications', ['id'])
        op.create_index('ix_applications_user_id', 'applications', ['user_id'])
        op.create_index('ix_applications_company_name', 'applications', ['company_name'])
        op.create_index('ix_applications_status', 'applications', ['status'])

    # Create application_documents table if it doesn't exist
    if 'application_documents' not in existing_tables:
        op.create_table(
            'application_documents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('application_id', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(length=500), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=True),
            sa.Column('doc_type', sa.String(length=50), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('embedding', Vector(384), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_application_documents_id', 'application_documents', ['id'])
        op.create_index('ix_application_documents_application_id', 'application_documents', ['application_id'])

    # Create application_status_history table if it doesn't exist
    if 'application_status_history' not in existing_tables:
        op.create_table(
            'application_status_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('application_id', sa.Integer(), nullable=False),
            sa.Column('old_status', sa.String(length=50), nullable=True),
            sa.Column('new_status', sa.String(length=50), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_application_status_history_id', 'application_status_history', ['id'])
        op.create_index('ix_application_status_history_application_id', 'application_status_history', ['application_id'])

    # Create application_chat_messages table if it doesn't exist
    if 'application_chat_messages' not in existing_tables:
        op.create_table(
            'application_chat_messages',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', UUID(as_uuid=True), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('embedding', Vector(384), nullable=True),
            sa.Column('message_metadata', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_application_chat_messages_id', 'application_chat_messages', ['id'])
        op.create_index('ix_application_chat_messages_user_id', 'application_chat_messages', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_application_chat_messages_user_id', table_name='application_chat_messages')
    op.drop_index('ix_application_chat_messages_id', table_name='application_chat_messages')
    op.drop_table('application_chat_messages')

    op.drop_index('ix_application_status_history_application_id', table_name='application_status_history')
    op.drop_index('ix_application_status_history_id', table_name='application_status_history')
    op.drop_table('application_status_history')

    op.drop_index('ix_application_documents_application_id', table_name='application_documents')
    op.drop_index('ix_application_documents_id', table_name='application_documents')
    op.drop_table('application_documents')

    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_company_name', table_name='applications')
    op.drop_index('ix_applications_user_id', table_name='applications')
    op.drop_index('ix_applications_id', table_name='applications')
    op.drop_table('applications')
