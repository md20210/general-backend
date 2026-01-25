"""Make michael.dabrock@gmx.es admin

Revision ID: 20260125_make_michael_admin
Revises: 20260125_add_email_verification
Create Date: 2026-01-25 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260125_make_michael_admin'
down_revision = '20260125_add_email_verification'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make michael.dabrock@gmx.es an admin
    op.execute("""
        UPDATE users
        SET is_superuser = true, is_active = true, is_verified = true
        WHERE email = 'michael.dabrock@gmx.es';
    """)


def downgrade() -> None:
    # Revert admin status
    op.execute("""
        UPDATE users
        SET is_superuser = false
        WHERE email = 'michael.dabrock@gmx.es';
    """)
