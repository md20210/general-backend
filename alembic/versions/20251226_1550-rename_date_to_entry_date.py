"""Rename date column to entry_date to avoid Pydantic recursion bug

Revision ID: b5c6d7e8f9g0
Revises: a1b2c3d4
Create Date: 2025-12-26 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c6d7e8f9g0'
down_revision: Union[str, None] = 'a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename date column to entry_date."""
    # Check if the table exists and has the 'date' column
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'lifechronicle_entries' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('lifechronicle_entries')]

        # Only rename if 'date' exists and 'entry_date' doesn't
        if 'date' in existing_columns and 'entry_date' not in existing_columns:
            op.alter_column('lifechronicle_entries', 'date', new_column_name='entry_date')


def downgrade() -> None:
    """Revert entry_date column back to date."""
    # Rename back to original
    op.alter_column('lifechronicle_entries', 'entry_date', new_column_name='date')
