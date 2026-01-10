#!/usr/bin/env python3
"""
Create bar_newsletter table
"""
import os
import sys
from sqlalchemy import create_engine, text

def create_newsletter_table():
    """Create bar_newsletter table if it doesn't exist"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    # Fix URL for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            print("🔧 Creating bar_newsletter table...")

            # Create table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bar_newsletter (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255),
                    language VARCHAR(5) DEFAULT 'ca',
                    is_active BOOLEAN DEFAULT TRUE,
                    subscribed_at TIMESTAMP DEFAULT NOW(),
                    unsubscribed_at TIMESTAMP
                );
            """))
            print("   ✅ bar_newsletter table created")

            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bar_newsletter_email ON bar_newsletter(email);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bar_newsletter_active ON bar_newsletter(is_active);
            """))
            print("   ✅ Indexes created")

            conn.commit()

            print("\n✅ Newsletter table ready!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_newsletter_table()
    sys.exit(0 if success else 1)
