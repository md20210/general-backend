"""Add folder tracking attributes and ensure folders table exists

Revision ID: 20260119_folder_tracking
Revises: 20260119_folder_attrs
Create Date: 2026-01-19 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '20260119_folder_tracking'  # Shortened to fit VARCHAR(32)
down_revision = '20260119_folder_attrs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, check if application_folders table exists, if not create it
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'application_folders' not in inspector.get_table_names():
        # Create application_folders table
        op.create_table(
            'application_folders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('application_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('parent_id', sa.Integer(), nullable=True),
            sa.Column('path', sa.String(length=2000), nullable=False),
            sa.Column('level', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['parent_id'], ['application_folders.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_application_folders_id', 'application_folders', ['id'])
        op.create_index('ix_application_folders_application_id', 'application_folders', ['application_id'])
        op.create_index('ix_application_folders_parent_id', 'application_folders', ['parent_id'])
        op.create_index('ix_application_folders_path', 'application_folders', ['path'])

        # Add folder_id to application_documents if it doesn't exist
        op.add_column('application_documents', sa.Column('folder_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_application_documents_folder_id', 'application_documents', 'application_folders', ['folder_id'], ['id'], ondelete='CASCADE')
        op.create_index('ix_application_documents_folder_id', 'application_documents', ['folder_id'])

        # Add indexed field to application_documents if it doesn't exist
        op.add_column('application_documents', sa.Column('indexed', sa.Boolean(), nullable=True, server_default='false'))
        op.create_index('ix_application_documents_indexed', 'application_documents', ['indexed'])

    # Now add the new tracking attributes to application_folders (check if they don't exist first)
    existing_columns = [col['name'] for col in inspector.get_columns('application_folders')]

    if 'is_bewerbung' not in existing_columns:
        op.add_column('application_folders', sa.Column('is_bewerbung', sa.Boolean(), nullable=True, server_default='false'))

    if 'status' not in existing_columns:
        op.add_column('application_folders', sa.Column('status', sa.String(length=100), nullable=True))

    if 'gehaltsangabe' not in existing_columns:
        op.add_column('application_folders', sa.Column('gehaltsangabe', sa.Float(), nullable=True))

    if 'gehaltsvorgabe' not in existing_columns:
        op.add_column('application_folders', sa.Column('gehaltsvorgabe', sa.Float(), nullable=True))

    if 'gehalt_schaetzung' not in existing_columns:
        op.add_column('application_folders', sa.Column('gehalt_schaetzung', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove the tracking attributes
    op.drop_column('application_folders', 'gehalt_schaetzung')
    op.drop_column('application_folders', 'gehaltsvorgabe')
    op.drop_column('application_folders', 'gehaltsangabe')
    op.drop_column('application_folders', 'status')
    op.drop_column('application_folders', 'is_bewerbung')
