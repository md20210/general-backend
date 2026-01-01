"""Fix: Ensure cv_showcase enum value exists

Revision ID: fix_cv_showcase_002
Revises: add_cv_showcase_001
Create Date: 2026-01-01 16:30:00.000000

This migration ensures the cv_showcase enum value exists, even if the
previous migration failed to add it due to event loop conflicts.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_cv_showcase_002'
down_revision = 'add_cv_showcase_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add cv_showcase value to documenttype enum (safe to run multiple times)
    # This ensures the enum value exists even if previous migration failed
    op.execute("ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'cv_showcase'")


def downgrade():
    # Downgrading enums is complex and data-destructive, so we skip it
    pass
