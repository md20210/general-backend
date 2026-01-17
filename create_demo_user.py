#!/usr/bin/env python3
"""Create demo user for Application Tracker testing"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from backend.config import settings

async def create_demo_user():
    """Create demo user with fixed UUID"""
    engine = create_engine(settings.DATABASE_URL)

    with Session(engine) as session:
        # Check if demo user exists
        result = session.execute(
            text("SELECT id FROM \"user\" WHERE id = '00000000-0000-0000-0000-000000000001'")
        ).first()

        if result:
            print("✅ Demo user already exists")
            return

        # Create demo user
        session.execute(text("""
            INSERT INTO "user" (id, email, hashed_password, is_active, is_superuser, is_verified)
            VALUES (
                '00000000-0000-0000-0000-000000000001',
                'demo@applicationtracker.test',
                '$2b$12$dummypasswordhashfordemo000000000000000000000000000000000',
                true,
                false,
                true
            )
        """))
        session.commit()
        print("✅ Demo user created: 00000000-0000-0000-0000-000000000001")

if __name__ == "__main__":
    asyncio.run(create_demo_user())
