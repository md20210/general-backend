"""Convert BarNews to multilingual JSON fields

Revision ID: 20260110_barnews_multilingual
Revises: 20260110_add_bar_settings
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '20260110_barnews_multilingual'
down_revision = '20260110_add_bar_settings'
branch_labels = None
depends_on = None


def upgrade():
    """Convert BarNews title and content to JSON for multilingual support."""

    # First, we need to migrate existing data to the new JSON format
    # Add temporary columns
    op.add_column('bar_news', sa.Column('title_new', JSON, nullable=True))
    op.add_column('bar_news', sa.Column('content_new', JSON, nullable=True))

    # Migrate existing data - assume existing data is in German (de)
    op.execute("""
        UPDATE bar_news SET
            title_new = jsonb_build_object(
                'ca', title,
                'es', title,
                'en', title,
                'de', title,
                'fr', title
            ),
            content_new = jsonb_build_object(
                'ca', content,
                'es', content,
                'en', content,
                'de', content,
                'fr', content
            );
    """)

    # Drop old columns and rename new ones
    op.drop_column('bar_news', 'title')
    op.drop_column('bar_news', 'content')
    op.alter_column('bar_news', 'title_new', new_column_name='title')
    op.alter_column('bar_news', 'content_new', new_column_name='content')


def downgrade():
    """Revert BarNews title and content back to text fields."""

    # Add temporary text columns
    op.add_column('bar_news', sa.Column('title_old', sa.String(500), nullable=True))
    op.add_column('bar_news', sa.Column('content_old', sa.Text, nullable=True))

    # Extract German (de) version back to text
    op.execute("""
        UPDATE bar_news SET
            title_old = title->>'de',
            content_old = content->>'de';
    """)

    # Drop JSON columns and rename old ones
    op.drop_column('bar_news', 'title')
    op.drop_column('bar_news', 'content')
    op.alter_column('bar_news', 'title_old', new_column_name='title')
    op.alter_column('bar_news', 'content_old', new_column_name='content')
