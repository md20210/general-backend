"""Add lifechronicle_entries table

Revision ID: a1b2c3d4
Revises:
Create Date: 2025-12-26 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lifechronicle_entries table
    op.create_table(
        'lifechronicle_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('refined_text', sa.Text(), nullable=True),
        sa.Column('photo_urls', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_refined', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('ix_lifechronicle_entries_user_id', 'lifechronicle_entries', ['user_id'])
    op.create_index('ix_lifechronicle_entries_date', 'lifechronicle_entries', ['date'])
    op.create_index('ix_lifechronicle_entries_created_at', 'lifechronicle_entries', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_lifechronicle_entries_created_at', table_name='lifechronicle_entries')
    op.drop_index('ix_lifechronicle_entries_date', table_name='lifechronicle_entries')
    op.drop_index('ix_lifechronicle_entries_user_id', table_name='lifechronicle_entries')

    # Drop table
    op.drop_table('lifechronicle_entries')
