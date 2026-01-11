"""Convert cuisine, price_range, and rating to multilingual JSONB

Revision ID: bar_multilingual_001
Revises: elasticsearch_003
Create Date: 2026-01-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'bar_multilingual_001'
down_revision = 'elasticsearch_003'
branch_labels = None
depends_on = None


def upgrade():
    # First, get the current values from bar_info table
    bind = op.get_bind()

    # Create temporary columns for JSONB data
    op.add_column('bar_info', sa.Column('cuisine_temp', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('bar_info', sa.Column('price_range_temp', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('bar_info', sa.Column('rating_temp', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Migrate existing data - set to empty dict for now (will be populated via API)
    bind.execute(sa.text("""
        UPDATE bar_info
        SET cuisine_temp = '{}'::jsonb,
            price_range_temp = '{}'::jsonb,
            rating_temp = '{}'::jsonb
    """))

    # Drop old columns
    op.drop_column('bar_info', 'cuisine')
    op.drop_column('bar_info', 'price_range')
    op.drop_column('bar_info', 'rating')

    # Rename temporary columns
    op.alter_column('bar_info', 'cuisine_temp', new_column_name='cuisine')
    op.alter_column('bar_info', 'price_range_temp', new_column_name='price_range')
    op.alter_column('bar_info', 'rating_temp', new_column_name='rating')


def downgrade():
    # Convert back to string columns
    bind = op.get_bind()

    # Create temporary string columns
    op.add_column('bar_info', sa.Column('cuisine_temp', sa.String(length=255), nullable=True))
    op.add_column('bar_info', sa.Column('price_range_temp', sa.String(length=50), nullable=True))
    op.add_column('bar_info', sa.Column('rating_temp', sa.String(length=100), nullable=True))

    # Migrate data back - extract English version or first available language
    bind.execute(sa.text("""
        UPDATE bar_info
        SET cuisine_temp = COALESCE(cuisine->>'en', cuisine->>'de'),
            price_range_temp = COALESCE(price_range->>'en', price_range->>'de'),
            rating_temp = COALESCE(rating->>'en', rating->>'de')
    """))

    # Drop JSONB columns
    op.drop_column('bar_info', 'cuisine')
    op.drop_column('bar_info', 'price_range')
    op.drop_column('bar_info', 'rating')

    # Rename temporary columns back
    op.alter_column('bar_info', 'cuisine_temp', new_column_name='cuisine')
    op.alter_column('bar_info', 'price_range_temp', new_column_name='price_range')
    op.alter_column('bar_info', 'rating_temp', new_column_name='rating')
