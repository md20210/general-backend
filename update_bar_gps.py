#!/usr/bin/env python3
"""
Update Bar Ca l'Elena GPS coordinates to exact values
GPS: 41°21'40.7"N 2°06'59.0"E = 41.361305556, 2.116388889
"""
import os
import sys
from sqlalchemy import create_engine, text

def update_gps():
    """Update GPS coordinates in bar_info"""
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
            print("📍 Updating GPS coordinates for Bar Ca l'Elena...")
            print(f"   New coordinates: 41°21'40.7\"N 2°06'59.0\"E")
            print(f"   Decimal: 41.361305556, 2.116388889")

            # Update coordinates
            result = conn.execute(text("""
                UPDATE bar_info SET
                    location_lat = '41.361305556',
                    location_lng = '2.116388889'
                WHERE id = 1;
            """))

            conn.commit()

            if result.rowcount > 0:
                print(f"   ✅ Updated {result.rowcount} row(s)")

                # Verify update
                result = conn.execute(text("SELECT location_lat, location_lng FROM bar_info WHERE id = 1;"))
                row = result.fetchone()
                print(f"   Verified: lat={row[0]}, lng={row[1]}")
            else:
                print("   ⚠️  No rows updated (bar_info id=1 not found)")

            print("\n✅ GPS coordinates updated!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = update_gps()
    sys.exit(0 if success else 1)
