"""Add cv_showcase to documenttype enum

Revision ID: add_cv_showcase_001
Revises: 20251231_add_interview_success_field
Create Date: 2025-12-31 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_cv_showcase_001'
down_revision = 'elasticsearch_003'
branch_labels = None
depends_on = None


def upgrade():
    # Add new value to documenttype enum
    # PostgreSQL requires special handling for enum values
    op.execute("ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'cv_showcase'")


def downgrade():
    # Downgrading enums is complex in PostgreSQL and requires:
    # 1. Creating a new enum without the value
    # 2. Converting the column to the new type
    # 3. Dropping the old enum
    # Since this is complex and data-destructive, we'll skip it
    # In production, you should not downgrade this migration
    pass
