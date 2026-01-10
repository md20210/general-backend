#!/usr/bin/env python3
"""
Create Bar tables and initialize data
Bypasses Alembic to avoid migration conflicts
"""
import os
import sys
from sqlalchemy import create_engine, text

def create_bar_tables_and_data():
    """Create Bar tables and initialize data"""
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
            print("🔧 Creating Bar tables...")

            # Create bar_info table
            conn.execute(text("""
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
                );
            """))
            print("   ✅ bar_info table created")

            # Create bar_newsletter table
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

            # Initialize bar_info data with correct GPS coordinates
            print("\n📍 Initializing Bar Ca l'Elena data...")

            # Check if data already exists
            result = conn.execute(text("SELECT COUNT(*) FROM bar_info WHERE id = 1;"))
            count = result.scalar()

            if count == 0:
                # Insert new data
                conn.execute(text("""
                    INSERT INTO bar_info (
                        id, name, phone, address, city, postal_code,
                        latitude, longitude, google_maps_url,
                        description, price_range, rating, opening_hours
                    ) VALUES (
                        1,
                        'Bar Ca l''Elena',
                        '+34 933 36 50 43',
                        'Carrer d''Amadeu Torner, 20',
                        'L''Hospitalet de Llobregat',
                        '08902',
                        41.361305556,
                        2.116388889,
                        'https://maps.app.goo.gl/gXUiS3RRQ4FV52HS7',
                        '{"ca": "Bar tradicional català amb menú diari i tapes", "es": "Bar tradicional catalán con menú diario y tapas", "en": "Traditional Catalan bar with daily menu and tapas", "de": "Traditionelle katalanische Bar mit Tagesmenü und Tapas", "fr": "Bar catalan traditionnel avec menu du jour et tapas"}',
                        '€-€€',
                        '4.0/5',
                        '{}'
                    );
                """))
                print("   ✅ Bar data inserted")
            else:
                # Update existing data with correct GPS coordinates
                conn.execute(text("""
                    UPDATE bar_info SET
                        latitude = 41.361305556,
                        longitude = 2.116388889,
                        google_maps_url = 'https://maps.app.goo.gl/gXUiS3RRQ4FV52HS7',
                        address = 'Carrer d''Amadeu Torner, 20',
                        city = 'L''Hospitalet de Llobregat',
                        postal_code = '08902'
                    WHERE id = 1;
                """))
                print("   ✅ Bar data updated with correct GPS coordinates")
                print(f"      GPS: 41°21'40.7\"N 2°06'59.0\"E")
                print(f"      Decimal: 41.361305556, 2.116388889")

            conn.commit()

            print("\n✅ All Bar tables and data ready!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_bar_tables_and_data()
    sys.exit(0 if success else 1)
