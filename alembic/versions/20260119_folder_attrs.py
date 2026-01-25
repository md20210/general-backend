"""Dummy migration to match database version

Revision ID: 20260119_folder_attrs
Revises: 20260117_add_app
Create Date: 2026-01-19 12:00:00

This is a dummy migration that matches the version in the database.
It does nothing but allows Alembic to recognize the version.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260119_folder_attrs'
down_revision = '20260117_add_app'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Do nothing - version already exists in database"""
    pass


def downgrade() -> None:
    """Do nothing"""
    pass
