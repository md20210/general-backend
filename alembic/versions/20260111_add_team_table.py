"""Add team table for bar team members

Revision ID: team_001
Revises: bar_multilingual_001
Create Date: 2026-01-11 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'team_001'
down_revision = 'bar_multilingual_001'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'bar_team' not in inspector.get_table_names():
        # Create bar_team table
        op.create_table(
            'bar_team',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=True),
            sa.Column('description', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('image', sa.Text(), nullable=True),
            sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_bar_team_id'), 'bar_team', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_bar_team_id'), table_name='bar_team')
    op.drop_table('bar_team')
