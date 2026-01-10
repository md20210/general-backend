"""Add Bar Ca l'Elena tables

Revision ID: 20260110_bar
Revises: elasticsearch_003
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260110_bar'
down_revision = 'elasticsearch_003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bar_info table
    op.create_table(
        'bar_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('opening_hours', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cuisine', sa.String(length=255), nullable=True),
        sa.Column('price_range', sa.String(length=50), nullable=True),
        sa.Column('rating', sa.String(length=100), nullable=True),
        sa.Column('location_lat', sa.String(length=50), nullable=True),
        sa.Column('location_lng', sa.String(length=50), nullable=True),
        sa.Column('facebook_url', sa.String(length=500), nullable=True),
        sa.Column('featured_items', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reviews', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bar_info_id'), 'bar_info', ['id'], unique=False)

    # Create bar_menus table
    op.create_table(
        'bar_menus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('menu_type', sa.String(length=100), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bar_menus_id'), 'bar_menus', ['id'], unique=False)

    # Create bar_news table
    op.create_table(
        'bar_news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('publish_date', sa.DateTime(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('is_event', sa.Boolean(), nullable=True),
        sa.Column('event_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bar_news_id'), 'bar_news', ['id'], unique=False)

    # Create bar_reservations table
    op.create_table(
        'bar_reservations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=True),
        sa.Column('reservation_date', sa.DateTime(), nullable=True),
        sa.Column('num_guests', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bar_reservations_id'), 'bar_reservations', ['id'], unique=False)

    # Create bar_newsletter table
    op.create_table(
        'bar_newsletter',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('subscribed_at', sa.DateTime(), nullable=True),
        sa.Column('unsubscribed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bar_newsletter_id'), 'bar_newsletter', ['id'], unique=False)
    op.create_index(op.f('ix_bar_newsletter_email'), 'bar_newsletter', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_bar_newsletter_email'), table_name='bar_newsletter')
    op.drop_index(op.f('ix_bar_newsletter_id'), table_name='bar_newsletter')
    op.drop_table('bar_newsletter')

    op.drop_index(op.f('ix_bar_reservations_id'), table_name='bar_reservations')
    op.drop_table('bar_reservations')

    op.drop_index(op.f('ix_bar_news_id'), table_name='bar_news')
    op.drop_table('bar_news')

    op.drop_index(op.f('ix_bar_menus_id'), table_name='bar_menus')
    op.drop_table('bar_menus')

    op.drop_index(op.f('ix_bar_info_id'), table_name='bar_info')
    op.drop_table('bar_info')
