#!/usr/bin/env python3
"""
Update Bar Ca l'Elena GPS coordinates in database
"""
import os
from dotenv import load_dotenv
from backend.db.session import SessionLocal
from backend.models.bar import BarInfo
from sqlalchemy import text

load_dotenv()

def update_coordinates():
    """Update GPS coordinates to correct location"""
    db = SessionLocal()
    try:
        # Update coordinates to correct location
        # 41°21'40.7"N 2°06'59.0"E
        # Carrer d'Amadeu Torner, 20, 08902 L'Hospitalet de Llobregat
        result = db.execute(
            text("UPDATE bar_info SET latitude = 41.361305556, longitude = 2.116388889 WHERE id = 1")
        )
        db.commit()

        # Verify update
        info = db.query(BarInfo).filter(BarInfo.id == 1).first()
        if info:
            print("✅ GPS coordinates updated successfully!")
            print(f"   Bar: {info.name}")
            print(f"   Latitude: {info.latitude}")
            print(f"   Longitude: {info.longitude}")
            print(f"   Google Maps: https://www.google.com/maps?q={info.latitude},{info.longitude}")
        else:
            print("❌ Bar info not found in database")

    except Exception as e:
        print(f"❌ Error updating coordinates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_coordinates()
