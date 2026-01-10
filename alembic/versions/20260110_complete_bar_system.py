"""Complete Bar Ca l'Elena system - all tables and features

Revision ID: 20260110_bar_complete
Revises: elasticsearch_003
Create Date: 2026-01-10 16:30:00.000000

This migration creates all Bar Ca l'Elena tables in one go:
- bar_info: Basic bar information with multilingual support
- bar_settings: Opening hours and settings
- bar_menu: Menu items with multilingual support
- bar_news: News/announcements with multilingual support
- bar_featured_items: Featured menu items
- bar_newsletter: Newsletter subscriptions with language preference
- bar_customer_reviews: Customer reviews
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '20260110_bar_complete'
down_revision = 'elasticsearch_003'
branch_labels = None
depends_on = None


def upgrade():
    """Create all Bar Ca l'Elena tables"""

    # 1. bar_info table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_info (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            address VARCHAR(255),
            city VARCHAR(100),
            postal_code VARCHAR(20),
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            google_maps_url TEXT,
            description JSON,
            price_range VARCHAR(50),
            rating VARCHAR(10),
            opening_hours JSON,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # 2. bar_settings table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_settings (
            id SERIAL PRIMARY KEY,
            opening_hours JSON,
            special_hours JSON,
            is_open BOOLEAN DEFAULT TRUE,
            announcement JSON,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # 3. bar_menu table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_menu (
            id SERIAL PRIMARY KEY,
            name JSON NOT NULL,
            description JSON,
            price NUMERIC(10, 2),
            category JSON,
            image_url VARCHAR(500),
            is_available BOOLEAN DEFAULT TRUE,
            is_daily_menu BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # 4. bar_news table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_news (
            id SERIAL PRIMARY KEY,
            title JSON NOT NULL,
            content JSON NOT NULL,
            image_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # 5. bar_featured_items table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_featured_items (
            id SERIAL PRIMARY KEY,
            dish_name JSON NOT NULL,
            image_url VARCHAR(500),
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # 6. bar_newsletter table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_newsletter (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255),
            language VARCHAR(5) DEFAULT 'ca',
            is_active BOOLEAN DEFAULT TRUE,
            subscribed_at TIMESTAMP DEFAULT NOW(),
            unsubscribed_at TIMESTAMP
        )
    """)

    # 7. bar_customer_reviews table
    op.execute("""
        CREATE TABLE IF NOT EXISTS bar_customer_reviews (
            id SERIAL PRIMARY KEY,
            customer_name JSON,
            review_text JSON,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Create indexes for better performance
    op.execute("CREATE INDEX IF NOT EXISTS idx_bar_menu_category ON bar_menu USING gin(category)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bar_newsletter_email ON bar_newsletter(email)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bar_newsletter_active ON bar_newsletter(is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bar_news_active ON bar_news(is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bar_featured_active ON bar_featured_items(is_active)")


def downgrade():
    """Drop all Bar Ca l'Elena tables"""
    op.execute("DROP TABLE IF EXISTS bar_customer_reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_newsletter CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_featured_items CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_news CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_menu CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_settings CASCADE")
    op.execute("DROP TABLE IF EXISTS bar_info CASCADE")
