"""Merge parallel migration heads

Revision ID: 20260111_merge_heads
Revises: team_001, add_cv_showcase_001
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260111_merge_heads'
down_revision = ('team_001', 'add_cv_showcase_001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge migration - no schema changes needed
    pass


def downgrade() -> None:
    # Merge migration - no schema changes needed
    pass
