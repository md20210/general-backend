#!/usr/bin/env python3
"""
Initialize Bar Ca l'Elena data in the database
"""
import os
from backend.db.session import SessionLocal
from backend.models.bar import BarInfo
from sqlalchemy import text

def initialize_bar_info():
    """Initialize or update bar_info with correct data"""
    db = SessionLocal()
    try:
        # Check if bar_info already exists
        existing = db.query(BarInfo).filter(BarInfo.id == 1).first()

        if existing:
            print("ℹ️  Bar info already exists, updating...")
            # Update coordinates
            existing.latitude = 41.361305556
            existing.longitude = 2.116388889
            existing.google_maps_url = "https://maps.app.goo.gl/gXUiS3RRQ4FV52HS7"
            db.commit()
            print(f"✅ Updated bar info!")
        else:
            print("📝 Creating new bar info...")
            # Create new bar_info
            bar_info = BarInfo(
                name="Bar Ca l'Elena",
                phone="+34 933 36 50 43",
                address="Carrer d'Amadeu Torner, 20",
                city="L'Hospitalet de Llobregat",
                postal_code="08902",
                latitude=41.361305556,  # 41°21'40.7"N
                longitude=2.116388889,   # 2°06'59.0"E
                google_maps_url="https://maps.app.goo.gl/gXUiS3RRQ4FV52HS7",
                description={
                    "ca": "Bar tradicional català amb menú diari i tapes",
                    "es": "Bar tradicional catalán con menú diario y tapas",
                    "en": "Traditional Catalan bar with daily menu and tapas",
                    "de": "Traditionelle katalanische Bar mit Tagesmenü und Tapas",
                    "fr": "Bar catalan traditionnel avec menu du jour et tapas"
                },
                price_range="€-€€",
                rating="4.0/5",
                opening_hours={
                    "ca": "Dilluns a Divendres: 6:00 - 23:00",
                    "es": "Lunes a Viernes: 6:00 - 23:00",
                    "en": "Monday to Friday: 6:00 AM - 11:00 PM",
                    "de": "Montag bis Freitag: 6:00 - 23:00 Uhr",
                    "fr": "Lundi au Vendredi: 6h00 - 23h00"
                }
            )
            db.add(bar_info)
            db.commit()
            print("✅ Bar info created!")

        # Verify
        info = db.query(BarInfo).filter(BarInfo.id == 1).first()
        if info:
            print(f"\n📍 Bar Information:")
            print(f"   Name: {info.name}")
            print(f"   Address: {info.address}, {info.postal_code} {info.city}")
            print(f"   Phone: {info.phone}")
            print(f"   Coordinates: {info.latitude}, {info.longitude}")
            print(f"   (41°21'40.7\"N 2°06'59.0\"E)")
            print(f"   Google Maps: {info.google_maps_url}")
        else:
            print("❌ Failed to create/update bar info")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_bar_info()
