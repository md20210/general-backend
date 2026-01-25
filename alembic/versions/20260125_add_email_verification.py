"""Add email verification tokens table

Revision ID: 20260125_add_email_verification
Revises: 20260125_add_mvp_tax_spain_auth
Create Date: 2026-01-25 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '20260125_add_email_verification'
down_revision = '20260125_add_mvp_tax_spain_auth'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'email_verification_tokens' not in existing_tables:
        op.create_table(
            'email_verification_tokens',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('token', sa.String(255), nullable=False, unique=True, index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('used', sa.String(10), server_default='Nein'),
        )


def downgrade():
    op.drop_table('email_verification_tokens')
